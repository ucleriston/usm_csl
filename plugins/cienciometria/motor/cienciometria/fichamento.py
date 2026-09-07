"""Fichamento dos artigos que sustentam a lacuna.

A revisão cienciométrica mostra a forma do campo; ela não diz o que os trabalhos
afirmam. A lacuna que justifica uma pesquisa nova sai da leitura de um núcleo de
artigos — e sai mais rápido, e mais defensável, quando essa leitura é registrada
sempre nos mesmos campos, para que as lacunas declaradas por autores diferentes
possam ser comparadas lado a lado.

Os campos seguem o modelo de fichamento usado em sala: título, referência,
palavras-chave, objetivos, conceitos, autores do referencial, método (estratégia,
contexto, amostra, coleta, análise), resultados, contribuições, lacunas apontadas
pelos autores e citações extraídas.
"""

import os
import re

MINIMO_SUGERIDO = 10

CAMPOS = [
    ("titulo", "Título"),
    ("referencia", "Referência"),
    ("palavras_chave", "Palavras-chave"),
    ("objetivos", "Objetivos deste artigo"),
    ("conceitos", "Principais conceitos que o artigo apresenta"),
    ("autores_referencial", "Principais autores usados no referencial teórico"),
    ("metodo_estrategia", "Método — Estratégia de pesquisa"),
    ("metodo_contexto", "Método — Contexto"),
    ("metodo_amostra", "Método — Amostra ou participantes"),
    ("metodo_coleta", "Método — Coleta de dados"),
    ("metodo_analise", "Método — Análise dos dados"),
    ("resultados", "Principais resultados (com suas palavras)"),
    ("contribuicoes", "Contribuições (com suas palavras)"),
    ("lacunas", "Lacunas apontadas pelos autores e sugestões para futuras pesquisas"),
    ("termos_da_lacuna", "Termos da lacuna (2 a 4, para conferir no corpus)"),
    ("citacoes", "Citações importantes extraídas do texto (com página)"),
]

# campos sem os quais a ficha não serve ao seu propósito
OBRIGATORIOS = ["referencia", "objetivos", "metodo_estrategia", "resultados", "lacunas"]

VAZIOS = ("", "-", "—", "a preencher", "[a preencher]", "n/a", "na")


def dir_fichas(revisao):
    return os.path.join(revisao.dir, "fichamentos")


def _slug(texto, limite=60):
    base = re.sub(r"[^a-z0-9]+", "-", (texto or "").lower())
    return re.sub(r"-+", "-", base).strip("-")[:limite] or "sem-titulo"


def caminho_da_ficha(revisao, registro):
    nome = "%s-%s.md" % (
        registro.get("ano") or "sd",
        _slug((registro.get("autores") or ["sem-autor"])[0].split(",")[0]
              + "-" + (registro.get("titulo") or "")),
    )
    return os.path.join(dir_fichas(revisao), nome)


def criar_ficha(revisao, registro):
    """Cria a ficha já preenchida no que o corpus sabe; o resto exige leitura."""
    destino = caminho_da_ficha(revisao, registro)
    if os.path.exists(destino):
        return destino, False
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    autores = "; ".join(registro.get("autores") or [])
    referencia = "%s (%s). %s. %s." % (
        autores or "s.a.", registro.get("ano") or "s.d.",
        registro.get("titulo") or "sem título", registro.get("fonte") or "sem fonte")
    if registro.get("doi"):
        referencia += " https://doi.org/%s" % registro["doi"]

    linhas = [
        "---",
        "id_corpus: %s" % registro.get("id", ""),
        "doi: %s" % registro.get("doi", ""),
        "ano: %s" % (registro.get("ano") or ""),
        "fonte: %s" % (registro.get("fonte") or ""),
        "citacoes: %s" % (registro.get("citacoes") or 0),
        "---",
        "",
        "# %s" % (registro.get("titulo") or "sem título"),
        "",
    ]
    prefilled = {
        "titulo": registro.get("titulo") or "",
        "referencia": referencia,
        "palavras_chave": "; ".join(registro.get("palavras_chave") or []),
    }
    for chave, rotulo in CAMPOS:
        linhas.append("## %s" % rotulo)
        linhas.append("")
        linhas.append(prefilled.get(chave, ""))
        linhas.append("")
    linhas.append("<!-- Campos preenchidos automaticamente a partir do corpus: título, "
                  "referência e palavras-chave. O resto exige a leitura do texto: não "
                  "preencha de memória nem a partir do resumo apenas. -->")
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write("\n".join(linhas) + "\n")
    return destino, True


def ler_ficha(caminho):
    """Lê uma ficha e devolve os campos, mais o que ainda falta preencher."""
    with open(caminho, encoding="utf-8") as fh:
        texto = fh.read()
    meta = {}
    corpo = texto
    if texto.startswith("---"):
        partes = texto.split("---", 2)
        if len(partes) >= 3:
            for linha in partes[1].strip().splitlines():
                if ":" in linha:
                    k, v = linha.split(":", 1)
                    meta[k.strip()] = v.strip()
            corpo = partes[2]

    rotulos = {rotulo: chave for chave, rotulo in CAMPOS}
    campos = {chave: "" for chave, _ in CAMPOS}
    atual = None
    acumulado = []
    for linha in corpo.splitlines():
        cabecalho = re.match(r"^##\s+(.*)$", linha.strip())
        if cabecalho:
            if atual:
                campos[atual] = "\n".join(acumulado).strip()
            atual = rotulos.get(cabecalho.group(1).strip())
            acumulado = []
        elif atual and not linha.strip().startswith("<!--"):
            acumulado.append(linha)
    if atual:
        campos[atual] = "\n".join(acumulado).strip()

    faltando = [
        rotulo for chave, rotulo in CAMPOS
        if chave in OBRIGATORIOS and campos[chave].strip().lower() in VAZIOS
    ]
    return {
        "arquivo": os.path.basename(caminho),
        "caminho": caminho,
        "meta": meta,
        "campos": campos,
        "faltando": faltando,
        "completa": not faltando,
    }


def listar_fichas(revisao):
    pasta = dir_fichas(revisao)
    if not os.path.isdir(pasta):
        return []
    fichas = []
    for arquivo in sorted(os.listdir(pasta)):
        if arquivo.endswith(".md"):
            try:
                fichas.append(ler_ficha(os.path.join(pasta, arquivo)))
            except OSError:
                continue
    return fichas


def sugerir_leitura(corpus, resultados, quantidade=MINIMO_SUGERIDO):
    """Propõe quais artigos fichar, por critérios declarados e verificáveis.

    Três critérios, porque cada um cobre um viés do outro: os mais citados (o que
    o campo consagrou), os mais recentes entre os citados (o que está em curso) e
    um representante por agrupamento temático (o que a leitura por citação
    esconderia). A escolha final é humana; isto é uma proposta com justificativa.
    """
    def cit(r):
        return int(r.get("citacoes") or 0)

    escolhidos, vistos = [], set()

    def juntar(registros, motivo, limite):
        n = 0
        for r in registros:
            if n >= limite:
                break
            if r["id"] in vistos or not r.get("titulo"):
                continue
            vistos.add(r["id"])
            escolhidos.append({
                "id": r["id"], "ano": r.get("ano"), "titulo": r.get("titulo"),
                "fonte": r.get("fonte"), "citacoes": cit(r),
                "citacoes_por_ano": r.get("citacoes_por_ano", ""),
                "autores": "; ".join((r.get("autores") or [])[:3]),
                "doi": r.get("doi", ""), "motivo": motivo,
            })
            n += 1

    metade = max(1, quantidade // 2)
    juntar(sorted(corpus, key=lambda r: -cit(r)), "mais citado do corpus", metade)

    recentes = [r for r in corpus if int(r.get("ano") or 0) >= _ano_recente(corpus)]
    juntar(sorted(recentes, key=lambda r: -cit(r)), "recente e já citado",
           max(1, quantidade // 4))

    # um representante por agrupamento temático, quando a análise já existe
    mapa = ((resultados or {}).get("copalavras") or {}).get("mapa") or []
    for agrupamento in mapa:
        termos = [t.strip().lower() for t in
                  (agrupamento.get("termos_representativos") or "").split(";") if t.strip()]
        if not termos:
            continue
        candidatos = [
            r for r in corpus
            if r["id"] not in vistos
            and any(t in " ".join(p.lower() for p in (r.get("palavras_chave") or []))
                    for t in termos[:3])
        ]
        juntar(sorted(candidatos, key=lambda r: -cit(r)),
               "representa o agrupamento %s (%s)" % (agrupamento.get("agrupamento"),
                                                     termos[0]), 1)
    return escolhidos[:max(quantidade, len(mapa) + quantidade // 2)]


def _ano_recente(corpus, janela=5):
    anos = [int(r.get("ano") or 0) for r in corpus if r.get("ano")]
    return (max(anos) - janela) if anos else 0


def _ocorrencias(corpus, termo):
    termo = termo.strip().lower()
    if len(termo) < 3:
        return 0
    n = 0
    for r in corpus:
        alvo = " ".join([
            r.get("titulo") or "", r.get("resumo") or "",
            " ".join(r.get("palavras_chave") or []),
        ]).lower()
        if termo in alvo:
            n += 1
    return n


def matriz_de_lacunas(revisao, corpus):
    """Reúne as lacunas declaradas nas fichas e as confronta com o corpus.

    Autor que afirma "X é pouco estudado" faz uma afirmação verificável: se o
    termo aparece em metade do corpus, a lacuna já foi preenchida desde a
    publicação daquele artigo — e isso muda o argumento da sua pesquisa.
    """
    linhas = []
    for ficha in listar_fichas(revisao):
        lacuna = ficha["campos"].get("lacunas", "").strip()
        if not lacuna or lacuna.lower() in VAZIOS:
            continue
        termos = [t.strip() for t in re.split(r"[;,]", ficha["campos"].get("termos_da_lacuna", ""))
                  if t.strip()]
        contagens = {t: _ocorrencias(corpus, t) for t in termos}
        linhas.append({
            "ficha": ficha["arquivo"],
            "ano": ficha["meta"].get("ano", ""),
            "citacoes": ficha["meta"].get("citacoes", ""),
            "lacuna_declarada": " ".join(lacuna.split()),
            "termos": "; ".join(termos),
            "ocorrencias_no_corpus": "; ".join("%s=%d" % (t, n) for t, n in contagens.items()),
            "maior_ocorrencia": max(contagens.values()) if contagens else "",
            "cobertura_%": (round(100 * max(contagens.values()) / len(corpus), 1)
                            if contagens and corpus else ""),
        })
    return sorted(linhas, key=lambda l: -(int(l["citacoes"] or 0)))
