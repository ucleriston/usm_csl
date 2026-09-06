"""Triagem, concordância entre revisores e contagens do fluxo PRISMA."""

import csv
from collections import Counter

from .modelo import CODIGOS_EXCLUSAO

COLUNAS_TRIAGEM = [
    "id", "doi", "ano", "titulo", "fonte", "palavras_chave", "resumo",
    "decisao_r1", "codigo_exclusao_r1", "nota_r1",
    "decisao_r2", "codigo_exclusao_r2", "nota_r2",
    "decisao_final", "codigo_exclusao_final", "nota_consenso",
]

DECISOES = {"incluido", "excluido", "duvida"}


def planilha_de_triagem(corpus, limite_resumo=1200):
    """Gera as linhas da planilha cega de triagem (uma por registro)."""
    linhas = []
    for r in corpus:
        linhas.append(
            {
                "id": r["id"],
                "doi": r.get("doi", ""),
                "ano": r.get("ano", ""),
                "titulo": r.get("titulo", ""),
                "fonte": r.get("fonte", ""),
                "palavras_chave": "; ".join(r.get("palavras_chave") or []),
                "resumo": (r.get("resumo") or "")[:limite_resumo],
                "decisao_r1": "", "codigo_exclusao_r1": "", "nota_r1": "",
                "decisao_r2": "", "codigo_exclusao_r2": "", "nota_r2": "",
                "decisao_final": "", "codigo_exclusao_final": "", "nota_consenso": "",
            }
        )
    return linhas


def kappa_de_cohen(pares):
    """Kappa para pares (decisão do revisor 1, decisão do revisor 2)."""
    pares = [(a.strip().lower(), b.strip().lower()) for a, b in pares if a.strip() and b.strip()]
    n = len(pares)
    if n == 0:
        return {"n": 0, "kappa": None, "concordancia_observada": None}
    categorias = sorted({c for par in pares for c in par})
    observada = sum(1 for a, b in pares if a == b) / n
    marg1 = Counter(a for a, _ in pares)
    marg2 = Counter(b for _, b in pares)
    esperada = sum((marg1[c] / n) * (marg2[c] / n) for c in categorias)
    kappa = (observada - esperada) / (1 - esperada) if esperada < 1 else 1.0
    return {
        "n": n,
        "categorias": categorias,
        "concordancia_observada": round(observada, 4),
        "concordancia_esperada": round(esperada, 4),
        "kappa": round(kappa, 4),
        "interpretacao": interpretar_kappa(kappa),
        "atinge_meta_0.75": bool(kappa >= 0.75),
    }


def interpretar_kappa(k):
    if k is None:
        return "indefinido"
    if k < 0.20:
        return "insignificante"
    if k < 0.40:
        return "sofrivel"
    if k < 0.60:
        return "moderada"
    if k < 0.75:
        return "substancial"
    return "quase perfeita"


def ler_triagem(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def concordancia(linhas):
    pares = [(l.get("decisao_r1", ""), l.get("decisao_r2", "")) for l in linhas]
    resultado = kappa_de_cohen(pares)
    divergentes = [
        l["id"] for l in linhas
        if l.get("decisao_r1", "").strip() and l.get("decisao_r2", "").strip()
        and l["decisao_r1"].strip().lower() != l["decisao_r2"].strip().lower()
    ]
    resultado["divergencias"] = len(divergentes)
    resultado["ids_divergentes"] = divergentes[:100]
    invalidas = [
        l["id"] for l in linhas
        for campo in ("decisao_r1", "decisao_r2")
        if l.get(campo, "").strip() and l[campo].strip().lower() not in DECISOES
    ]
    resultado["decisoes_invalidas"] = sorted(set(invalidas))
    return resultado


def contagens_prisma(registros_brutos, estatisticas_dedup, linhas_triagem=None):
    """Monta as contagens do fluxo PRISMA a partir do pipeline."""
    por_base = Counter(r.get("base_origem", "?") for r in registros_brutos)
    fluxo = {
        "identificados_total": len(registros_brutos),
        "identificados_por_base": dict(por_base),
        "duplicatas_removidas": estatisticas_dedup.get("removidas_total", 0),
        "duplicatas_por_doi": estatisticas_dedup.get("removidas_por_doi", 0),
        "duplicatas_por_titulo_ano": estatisticas_dedup.get("removidas_por_titulo_ano", 0),
        "duplicatas_por_similaridade": estatisticas_dedup.get("removidas_por_similaridade", 0),
        "pares_em_revisao_manual": estatisticas_dedup.get("pares_para_revisao", 0),
        "triados": estatisticas_dedup.get("saida", 0),
    }
    if linhas_triagem:
        finais = [l.get("decisao_final", "").strip().lower() for l in linhas_triagem]
        fluxo["excluidos_triagem"] = sum(1 for d in finais if d == "excluido")
        fluxo["incluidos"] = sum(1 for d in finais if d == "incluido")
        fluxo["pendentes"] = sum(1 for d in finais if d not in ("incluido", "excluido"))
        codigos = Counter(
            l.get("codigo_exclusao_final", "").strip().upper()
            for l in linhas_triagem
            if l.get("decisao_final", "").strip().lower() == "excluido"
        )
        fluxo["exclusoes_por_codigo"] = {
            c: {"n": n, "descricao": CODIGOS_EXCLUSAO.get(c, "código não previsto")}
            for c, n in sorted(codigos.items())
        }
        sem_codigo = codigos.get("", 0)
        if sem_codigo:
            fluxo["alerta"] = "%d exclusões sem código E1-E8" % sem_codigo
    return fluxo


def diagrama_prisma(fluxo):
    """Rende o fluxo PRISMA em texto, pronto para o relatório."""
    linhas = ["```", "IDENTIFICAÇÃO"]
    linhas.append("  Registros identificados nas bases ............ n = %d" % fluxo["identificados_total"])
    for base, n in sorted(fluxo["identificados_por_base"].items(), key=lambda kv: -kv[1]):
        linhas.append("    %-40s n = %d" % (base, n))
    linhas.append("TRIAGEM")
    linhas.append("  Duplicatas removidas ........................ n = %d" % fluxo["duplicatas_removidas"])
    linhas.append("    por DOI ................................... n = %d" % fluxo["duplicatas_por_doi"])
    linhas.append("    por título + ano .......................... n = %d" % fluxo["duplicatas_por_titulo_ano"])
    linhas.append("    por similaridade .......................... n = %d" % fluxo["duplicatas_por_similaridade"])
    linhas.append("  Pares em revisão manual ..................... n = %d" % fluxo["pares_em_revisao_manual"])
    linhas.append("  Registros triados ........................... n = %d" % fluxo["triados"])
    if "incluidos" in fluxo:
        linhas.append("    excluídos ................................. n = %d" % fluxo["excluidos_triagem"])
        for codigo, dados in fluxo.get("exclusoes_por_codigo", {}).items():
            linhas.append("      %-4s %-34s n = %d" % (codigo or "s/c", dados["descricao"][:34], dados["n"]))
        linhas.append("    pendentes ................................. n = %d" % fluxo["pendentes"])
        linhas.append("INCLUSÃO")
        linhas.append("  Registros incluídos no corpus ............... n = %d" % fluxo["incluidos"])
    linhas.append("```")
    return "\n".join(linhas)
