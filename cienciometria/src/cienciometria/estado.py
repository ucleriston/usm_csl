"""Estado da pesquisa: em que etapa ela está, e o que falta para a próxima.

Uma revisão cienciométrica leva meses e atravessa muitas sessões de conversa. Se
o estado morar na conversa, ele se perde. Aqui ele é inferido dos artefatos que
existem na pasta da revisão: o que está feito é o que está no disco, não o que
alguém lembra de ter feito.

Cada etapa declara o que precisa existir para ser considerada cumprida, o que
falta quando não está, e qual é o próximo passo concreto.
"""

import json
import os
import re

MARCADORES = ("«", "»", "{{", "[preencher", "_____")


def _texto(caminho):
    if not os.path.exists(caminho):
        return ""
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _preenchido(caminho, minimo=1200):
    """Um documento conta como preenchido quando perdeu os marcadores do modelo."""
    texto = _texto(caminho)
    if len(texto) < minimo:
        return False
    return not any(m in texto for m in MARCADORES)


def _linhas_csv(caminho, minimo_colunas=2):
    if not os.path.exists(caminho):
        return 0
    n = 0
    with open(caminho, encoding="utf-8-sig", errors="replace") as fh:
        for i, linha in enumerate(fh):
            if i == 0 or linha.startswith("#") or not linha.strip():
                continue
            if len([c for c in linha.split(",") if c.strip()]) >= minimo_colunas:
                n += 1
    return n


def _conta_corpus(caminho):
    if not os.path.exists(caminho):
        return 0
    with open(caminho, encoding="utf-8-sig", errors="replace") as fh:
        return max(0, sum(1 for _ in fh) - 1)


def avaliar(revisao):
    """Devolve a lista de etapas com situação, pendências e próximo passo."""
    config = revisao.config
    execucao = revisao.execucao()
    docs = os.path.join(revisao.dir, "docs")
    etapas = []

    # ------------------------------------------------------------------ E1 escopo
    faltas = []
    if not config.get("tema"):
        faltas.append("`tema` em config/revisao.json")
    if not (config.get("janela") or {}).get("inicio"):
        faltas.append("janela temporal em config/revisao.json")
    proposicoes = config.get("proposicoes") or []
    if not proposicoes:
        faltas.append("ao menos uma proposição com critério de refutação")
    if not _preenchido(os.path.join(docs, "01-projeto-de-pesquisa.md")):
        faltas.append("docs/01-projeto-de-pesquisa.md ainda com os marcadores do modelo")
    etapas.append({
        "id": "E1", "nome": "Escopo e proposições", "skill": "escopo-da-pesquisa",
        "faltas": faltas,
        "proximo": "converse com o usuário para delimitar o objeto e escreva o recorte "
                   "em config/revisao.json e docs/01",
    })

    # ------------------------------------------------------------------ E2 protocolo
    faltas = []
    if not config.get("codigos_exclusao"):
        faltas.append("códigos de exclusão em config/revisao.json")
    if not _preenchido(os.path.join(docs, "02-protocolo-prisma.md")):
        faltas.append("docs/02-protocolo-prisma.md ainda com os marcadores do modelo")
    etapas.append({
        "id": "E2", "nome": "Protocolo", "skill": "triagem-e-prisma", "faltas": faltas,
        "proximo": "defina elegibilidade, códigos de exclusão e o procedimento de triagem",
    })

    # ------------------------------------------------------------------ E3 busca
    faltas = []
    if not _preenchido(os.path.join(docs, "03-estrategias-de-busca.md"), minimo=600):
        faltas.append("docs/03-estrategias-de-busca.md ainda com os marcadores do modelo")
    if _linhas_csv(os.path.join(revisao.dir_config, "sementes.csv"), 3) < 5:
        faltas.append("conjunto-semente (config/sementes.csv) com pelo menos 5 trabalhos")
    if not execucao.get("data_de_corte"):
        faltas.append("data de corte em config/execucao.json")
    if not any((e or {}).get("resultados") for e in execucao.get("execucoes") or []):
        faltas.append("nenhuma execução de busca registrada com resultados")
    etapas.append({
        "id": "E3", "nome": "Busca", "skill": "estrategia-de-busca", "faltas": faltas,
        "proximo": "monte as strings, calibre pelo conjunto-semente e registre cada execução",
    })

    # ------------------------------------------------------------------ E4 corpus
    n_corpus = _conta_corpus(revisao.corpus)
    faltas = []
    if not n_corpus:
        faltas.append("corpus vazio: rode `importar` (ou `coletar` antes, em fonte aberta)")
    if not os.path.exists(os.path.join(revisao.dir_processado, "dedup.json")):
        faltas.append("deduplicação não executada")
    etapas.append({
        "id": "E4", "nome": "Corpus", "skill": "revisao-cienciometrica", "faltas": faltas,
        "detalhe": "%d registros" % n_corpus if n_corpus else "",
        "proximo": "cienciometria importar --revisao %s && cienciometria dedup --revisao %s"
                   % (revisao.slug, revisao.slug),
    })

    # ------------------------------------------------------------------ E5 triagem
    faltas = []
    triagem = revisao.triagem
    if not os.path.exists(triagem):
        faltas.append("planilha de triagem preenchida (dados/processado/triagem-preenchida.csv)")
    else:
        texto = _texto(triagem)
        if "incluido" not in texto and "excluido" not in texto:
            faltas.append("planilha existe, mas sem decisões preenchidas")
    etapas.append({
        "id": "E5", "nome": "Triagem", "skill": "triagem-e-prisma", "faltas": faltas,
        "proximo": "cienciometria triagem --revisao %s, dois revisores, depois `kappa`" % revisao.slug,
        "opcional_quando": "o corpus já é o conjunto elegível por construção — decisão a declarar",
    })

    # ------------------------------------------------------------------ E6 análise
    resultados = os.path.join(revisao.dir_saidas, "resultados.json")
    faltas = []
    if not os.path.exists(resultados):
        faltas.append("análise não executada")
    else:
        try:
            with open(resultados, encoding="utf-8") as fh:
                dados = json.load(fh)
            if not dados.get("copalavras"):
                faltas.append("redes não geradas (rode `redes`)")
        except (ValueError, OSError):
            faltas.append("saidas/resultados.json ilegível — reexecute a análise")
    etapas.append({
        "id": "E6", "nome": "Análise", "skill": "interpretar-resultados", "faltas": faltas,
        "proximo": "cienciometria analise --revisao %s" % revisao.slug,
    })

    # ------------------------------------------------------------------ E7 fichamento
    from .fichamento import listar_fichas, MINIMO_SUGERIDO

    fichas = listar_fichas(revisao)
    completas = [f for f in fichas if f["completa"]]
    faltas = []
    if len(completas) < MINIMO_SUGERIDO:
        faltas.append("fichamento de %d artigos-núcleo (há %d completo(s) de %d ficha(s))"
                      % (MINIMO_SUGERIDO, len(completas), len(fichas)))
    etapas.append({
        "id": "E7", "nome": "Fichamento", "skill": "fichamento", "faltas": faltas,
        "detalhe": "%d fichas, %d completas" % (len(fichas), len(completas)),
        "proximo": "cienciometria fichar --revisao %s --sugerir" % revisao.slug,
    })

    # ------------------------------------------------------------------ E8 artigo
    artigo = os.path.join(revisao.dir_saidas, "artigo.md")
    faltas = [] if os.path.exists(artigo) else ["rascunho do artigo não gerado"]
    etapas.append({
        "id": "E8", "nome": "Artigo", "skill": "relatorio-cienciometrico", "faltas": faltas,
        "proximo": "cienciometria artigo --revisao %s" % revisao.slug,
    })

    for etapa in etapas:
        etapa["feito"] = not etapa["faltas"]
    return etapas


def resumo(revisao):
    """Etapas, a primeira pendente e o próximo passo."""
    etapas = avaliar(revisao)
    pendentes = [e for e in etapas if not e["feito"]]
    return {
        "revisao": revisao.slug,
        "titulo": revisao.config.get("titulo") or revisao.slug,
        "etapas": etapas,
        "concluidas": sum(1 for e in etapas if e["feito"]),
        "total": len(etapas),
        "etapa_atual": pendentes[0] if pendentes else None,
        "concluida": not pendentes,
    }


def formatar(dados):
    linhas = ["Revisão: %s" % dados["titulo"], ""]
    for etapa in dados["etapas"]:
        marca = "[x]" if etapa["feito"] else "[ ]"
        detalhe = (" — %s" % etapa["detalhe"]) if etapa.get("detalhe") else ""
        linhas.append("%s %s %s%s" % (marca, etapa["id"], etapa["nome"], detalhe))
        for falta in etapa["faltas"]:
            linhas.append("       falta: %s" % falta)
    linhas.append("")
    if dados["concluida"]:
        linhas.append("Todas as etapas cumpridas (%d de %d)." % (dados["concluidas"], dados["total"]))
    else:
        atual = dados["etapa_atual"]
        linhas.append("Etapa atual: %s %s   (skill: %s)" % (atual["id"], atual["nome"], atual["skill"]))
        linhas.append("Próximo passo: %s" % atual["proximo"])
    return "\n".join(linhas)
