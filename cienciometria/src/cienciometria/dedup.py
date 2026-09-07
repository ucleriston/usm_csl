"""Deduplicação do corpus (protocolo, §6).

Regra em três passos:
  1. DOI idêntico;
  2. título normalizado idêntico e mesmo ano (tolerância de 1 ano);
  3. similaridade de título >= LIMIAR_AUTO no mesmo ano.

Pares entre LIMIAR_REVISAO e LIMIAR_AUTO não são fundidos automaticamente:
saem em revisao-duplicatas.csv para conferência humana.
"""

import difflib
from collections import defaultdict

from .modelo import PRIORIDADE_BASES

LIMIAR_AUTO = 0.93
LIMIAR_REVISAO = 0.88

try:  # opcional: acelera corpus grande
    from rapidfuzz.fuzz import ratio as _ratio_rapido
except ImportError:  # pragma: no cover
    _ratio_rapido = None


def similaridade(a, b):
    if _ratio_rapido is not None:
        return _ratio_rapido(a, b) / 100.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def _prioridade(reg, ordem=None):
    ordem = ordem or PRIORIDADE_BASES
    try:
        return ordem.index(reg.get("base_origem", "manual"))
    except ValueError:
        return len(ordem)


def fundir(principal, secundario):
    """Funde dois registros do mesmo trabalho conforme a precedência do §8 do livro de códigos."""
    fundido = dict(principal)
    for campo, valor in secundario.items():
        if campo in ("id", "base_origem", "bases_todas"):
            continue
        atual = fundido.get(campo)
        if not atual and valor:
            fundido[campo] = valor
    # regras específicas que não seguem a precedência entre bases
    if int(secundario.get("citacoes") or 0) > int(fundido.get("citacoes") or 0):
        fundido["citacoes"] = secundario["citacoes"]
        fundido["fonte_citacoes"] = secundario.get("base_origem", "")
    if len(secundario.get("referencias") or []) > len(fundido.get("referencias") or []):
        fundido["referencias"] = secundario["referencias"]
        fundido["n_referencias"] = len(secundario["referencias"])
    if len(secundario.get("resumo") or "") > len(fundido.get("resumo") or ""):
        fundido["resumo"] = secundario["resumo"]
    if secundario.get("base_origem") == "scielo" and secundario.get("idioma") in ("pt", "es"):
        fundido["idioma"] = secundario["idioma"]
        if secundario.get("fonte"):
            fundido["fonte"] = secundario["fonte"]
    if not fundido.get("doi") and secundario.get("doi"):
        fundido["doi"] = secundario["doi"]
    bases = list(fundido.get("bases_todas") or [fundido.get("base_origem", "")])
    for b in secundario.get("bases_todas") or [secundario.get("base_origem", "")]:
        if b and b not in bases:
            bases.append(b)
    fundido["bases_todas"] = bases
    return fundido


def deduplicar(registros, limiar_auto=None, limiar_revisao=None, precedencia=None):
    """Devolve (corpus deduplicado, pares para revisão manual, estatísticas).

    Os limiares e a precedência entre bases vêm da configuração da revisão;
    na falta dela, valem os padrões deste módulo.
    """
    limiar_auto = LIMIAR_AUTO if limiar_auto is None else limiar_auto
    limiar_revisao = LIMIAR_REVISAO if limiar_revisao is None else limiar_revisao
    ordenados = sorted(registros, key=lambda r: _prioridade(r, precedencia))
    por_doi, sem_doi = {}, []
    duplicatas = {"doi": 0, "titulo_ano": 0, "similaridade": 0}

    for reg in ordenados:
        doi = (reg.get("doi") or "").strip()
        if doi:
            if doi in por_doi:
                por_doi[doi] = fundir(por_doi[doi], reg)
                duplicatas["doi"] += 1
            else:
                por_doi[doi] = reg
        else:
            sem_doi.append(reg)

    corpus = list(por_doi.values())

    # índice por título normalizado para os passos 2 e 3
    indice = defaultdict(list)
    for pos, reg in enumerate(corpus):
        indice[reg["titulo_norm"]].append(pos)

    revisao = []
    for reg in sem_doi:
        alvo = reg["titulo_norm"]
        posicao = None
        if alvo in indice:
            for pos in indice[alvo]:
                if abs(int(corpus[pos].get("ano") or 0) - int(reg.get("ano") or 0)) <= 1:
                    posicao = pos
                    duplicatas["titulo_ano"] += 1
                    break
        if posicao is None:
            melhor, melhor_pos = 0.0, None
            for pos, outro in enumerate(corpus):
                if abs(int(outro.get("ano") or 0) - int(reg.get("ano") or 0)) > 1:
                    continue
                if abs(len(outro["titulo_norm"]) - len(alvo)) > 20:
                    continue
                s = similaridade(alvo, outro["titulo_norm"])
                if s > melhor:
                    melhor, melhor_pos = s, pos
            if melhor >= limiar_auto:
                posicao = melhor_pos
                duplicatas["similaridade"] += 1
            elif melhor >= limiar_revisao and melhor_pos is not None:
                revisao.append(
                    {
                        "similaridade": round(melhor, 4),
                        "id_a": corpus[melhor_pos]["id"],
                        "titulo_a": corpus[melhor_pos]["titulo"],
                        "ano_a": corpus[melhor_pos]["ano"],
                        "id_b": reg["id"],
                        "titulo_b": reg["titulo"],
                        "ano_b": reg["ano"],
                        "decisao": "",
                    }
                )
        if posicao is None:
            corpus.append(reg)
            indice[alvo].append(len(corpus) - 1)
        else:
            corpus[posicao] = fundir(corpus[posicao], reg)

    estatisticas = {
        "entrada": len(registros),
        "saida": len(corpus),
        "removidas_total": len(registros) - len(corpus),
        "removidas_por_doi": duplicatas["doi"],
        "removidas_por_titulo_ano": duplicatas["titulo_ano"],
        "removidas_por_similaridade": duplicatas["similaridade"],
        "pares_para_revisao": len(revisao),
        "limiar_automatico": limiar_auto,
        "limiar_revisao_humana": limiar_revisao,
    }
    return corpus, revisao, estatisticas
