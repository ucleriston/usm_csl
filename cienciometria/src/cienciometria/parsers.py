"""Leitura das exportações das bases.

Formatos suportados:
  * Scopus CSV (todos os campos)
  * Web of Science plain text (Full Record and Cited References)
  * Dimensions CSV e Lens CSV (detectados pelo cabeçalho)
  * BibTeX (.bib) e RIS (.ris) — usados pelo SciELO e pelos gerenciadores

Cada função devolve uma lista de registros no formato de modelo.registro_vazio().
"""

import csv
import json
import os
import re
import sys

from .modelo import registro_vazio

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def _partes(valor, sep=";"):
    return [p.strip() for p in (valor or "").split(sep) if p.strip()]


# --------------------------------------------------------------------------- Scopus

COLUNAS_SCOPUS = {
    "authors": "autores",
    "author full names": "autores",
    "title": "titulo",
    "year": "ano",
    "source title": "fonte",
    "volume": "volume",
    "issue": "numero",
    "page start": "paginas",
    "cited by": "citacoes",
    "doi": "doi",
    "affiliations": "afiliacoes",
    "authors with affiliations": "afiliacoes",
    "abstract": "resumo",
    "author keywords": "palavras_chave",
    "index keywords": "palavras_indexadas",
    "references": "referencias",
    "document type": "tipo_documento",
    "language of original document": "idioma",
    "publisher": "editora",
    "issn": "issn",
    "link": "url",
    "authors with affiliations": "afiliacoes",
}


def ler_scopus_csv(caminho):
    registros = []
    with open(caminho, encoding="utf-8-sig", newline="") as fh:
        for i, linha in enumerate(csv.DictReader(fh)):
            baixa = { (k or "").strip().lower(): (v or "") for k, v in linha.items() }
            reg = registro_vazio(id="scopus:%d" % i, base_origem="scopus")
            for coluna, campo in COLUNAS_SCOPUS.items():
                if coluna not in baixa or not baixa[coluna].strip():
                    continue
                valor = baixa[coluna].strip()
                if campo in ("autores", "palavras_chave", "palavras_indexadas", "referencias"):
                    reg[campo] = _partes(valor)
                elif campo in ("ano", "citacoes"):
                    reg[campo] = int(re.sub(r"\D", "", valor) or 0)
                elif campo == "afiliacoes" and reg["afiliacoes"]:
                    continue
                else:
                    reg[campo] = valor
            reg["fonte_citacoes"] = "scopus" if reg["citacoes"] else ""
            if reg["titulo"]:
                registros.append(reg)
    return registros


# --------------------------------------------------------------------------- Web of Science

CAMPOS_WOS = {
    "AU": "autores",
    "TI": "titulo",
    "SO": "fonte",
    "PY": "ano",
    "DI": "doi",
    "AB": "resumo",
    "DE": "palavras_chave",
    "ID": "palavras_indexadas",
    "C1": "afiliacoes",
    "TC": "citacoes",
    "CR": "referencias",
    "DT": "tipo_documento",
    "LA": "idioma",
    "PU": "editora",
    "SN": "issn",
    "VL": "volume",
    "IS": "numero",
    "BP": "paginas",
    "OI": "orcid",
}

MULTILINHA = {"AU", "CR", "C1", "DE", "ID", "OI"}


def ler_wos_txt(caminho):
    """Lê o formato tagueado da WoS (registros separados por 'ER')."""
    registros, atual, tag = [], None, None
    with open(caminho, encoding="utf-8-sig", errors="replace") as fh:
        for linha in fh:
            linha = linha.rstrip("\n")
            if not linha.strip():
                continue
            marca = linha[:2]
            if marca == "ER":
                if atual:
                    registros.append(atual)
                atual, tag = None, None
                continue
            if marca == "PT":
                atual = {"_bruto": {}}
                tag = None
                continue
            if atual is None:
                continue
            if re.match(r"^[A-Z][A-Z0-9] ", linha):
                tag = marca
                atual["_bruto"].setdefault(tag, []).append(linha[3:].strip())
            elif tag and linha.startswith("   "):
                atual["_bruto"].setdefault(tag, []).append(linha.strip())
    if atual:
        registros.append(atual)

    saida = []
    for i, cru in enumerate(registros):
        bruto = cru["_bruto"]
        reg = registro_vazio(id="wos:%d" % i, base_origem="wos")
        for tag, valores in bruto.items():
            campo = CAMPOS_WOS.get(tag)
            if not campo:
                continue
            if tag in MULTILINHA:
                reg[campo] = [v for v in valores if v]
            elif campo in ("ano", "citacoes"):
                reg[campo] = int(re.sub(r"\D", "", valores[0]) or 0)
            else:
                reg[campo] = " ".join(valores).strip()
        if isinstance(reg["afiliacoes"], list):
            reg["afiliacoes"] = " ; ".join(reg["afiliacoes"])
        for campo in ("palavras_chave", "palavras_indexadas"):
            if isinstance(reg[campo], list):
                reg[campo] = [t for v in reg[campo] for t in _partes(v)]
        reg["fonte_citacoes"] = "wos" if reg["citacoes"] else ""
        if reg["titulo"]:
            saida.append(reg)
    return saida


# --------------------------------------------------------------------------- BibTeX

CAMPOS_BIB = {
    "author": "autores",
    "title": "titulo",
    "year": "ano",
    "journal": "fonte",
    "booktitle": "fonte",
    "doi": "doi",
    "abstract": "resumo",
    "keywords": "palavras_chave",
    "publisher": "editora",
    "issn": "issn",
    "volume": "volume",
    "number": "numero",
    "pages": "paginas",
    "language": "idioma",
    "url": "url",
    "affiliation": "afiliacoes",
}


def ler_bibtex(caminho, base="scielo"):
    with open(caminho, encoding="utf-8", errors="replace") as fh:
        texto = fh.read()
    registros = []
    for i, bloco in enumerate(re.split(r"\n(?=@)", texto)):
        if not bloco.strip().startswith("@"):
            continue
        tipo = re.match(r"@(\w+)", bloco.strip())
        reg = registro_vazio(id="%s:%d" % (base, i), base_origem=base)
        reg["tipo_documento"] = {"article": "artigo", "incollection": "capitulo",
                                 "inproceedings": "anais", "inbook": "capitulo"}.get(
            (tipo.group(1).lower() if tipo else ""), "artigo")
        for chave, valor in re.findall(
            r"(\w+)\s*=\s*[{\"](.*?)[}\"]\s*,?\s*(?=\n\s*\w+\s*=|\n?\s*\}\s*$)", bloco, re.S
        ):
            campo = CAMPOS_BIB.get(chave.lower())
            if not campo:
                continue
            valor = re.sub(r"\s+", " ", valor.replace("{", "").replace("}", "")).strip()
            if campo == "autores":
                reg[campo] = [a.strip() for a in re.split(r"\band\b", valor) if a.strip()]
            elif campo == "palavras_chave":
                reg[campo] = [p.strip() for p in re.split(r"[;,]", valor) if p.strip()]
            elif campo == "ano":
                reg[campo] = int(re.sub(r"\D", "", valor) or 0)
            elif campo == "fonte" and reg["fonte"]:
                continue
            else:
                reg[campo] = valor
        if reg["titulo"]:
            registros.append(reg)
    return registros


# --------------------------------------------------------------------------- RIS

CAMPOS_RIS = {
    "AU": "autores", "A1": "autores",
    "TI": "titulo", "T1": "titulo",
    "PY": "ano", "Y1": "ano",
    "JO": "fonte", "JF": "fonte", "T2": "fonte",
    "DO": "doi",
    "AB": "resumo", "N2": "resumo",
    "KW": "palavras_chave",
    "PB": "editora",
    "SN": "issn",
    "VL": "volume", "IS": "numero", "SP": "paginas",
    "LA": "idioma",
    "UR": "url",
    "AD": "afiliacoes",
    "TY": "tipo_documento",
}

TIPO_RIS = {"JOUR": "artigo", "CHAP": "capitulo", "CONF": "anais", "CPAPER": "anais"}


def ler_ris(caminho, base="scielo"):
    registros, atual, tag = [], None, None
    with open(caminho, encoding="utf-8-sig", errors="replace") as fh:
        for linha in fh:
            linha = linha.rstrip("\n")
            cabeca = re.match(r"^([A-Z][A-Z0-9])  - ?(.*)$", linha)
            if cabeca:
                tag, valor = cabeca.group(1), cabeca.group(2).strip()
                if tag == "TY":
                    atual = registro_vazio(id="%s:%d" % (base, len(registros)), base_origem=base)
                    atual["tipo_documento"] = TIPO_RIS.get(valor.upper(), "artigo")
                    continue
                if tag == "ER":
                    if atual and atual["titulo"]:
                        registros.append(atual)
                    atual = None
                    continue
                if atual is None:
                    continue
                campo = CAMPOS_RIS.get(tag)
                if not campo:
                    continue
                if campo in ("autores", "palavras_chave"):
                    atual[campo].append(valor)
                elif campo == "ano":
                    atual[campo] = int(re.sub(r"\D", "", valor)[:4] or 0)
                elif campo == "fonte" and atual["fonte"]:
                    continue
                elif campo == "afiliacoes":
                    atual[campo] = (atual[campo] + " ; " + valor).strip(" ;")
                else:
                    atual[campo] = valor
            elif atual is not None and tag and linha.strip():
                campo = CAMPOS_RIS.get(tag)
                if campo and campo not in ("autores", "palavras_chave"):
                    atual[campo] = (str(atual[campo]) + " " + linha.strip()).strip()
    if atual and atual["titulo"]:
        registros.append(atual)
    return registros


# --------------------------------------------------------------------------- CSV genérico

COLUNAS_GENERICAS = {
    "title": "titulo", "titulo": "titulo", "document title": "titulo",
    "authors": "autores", "author names": "autores", "autores": "autores",
    "publication year": "ano", "year": "ano", "date": "ano", "ano": "ano",
    "source title": "fonte", "source title (anthology or book title)": "fonte",
    "journal": "fonte", "publication venue": "fonte", "source": "fonte",
    "doi": "doi",
    "abstract": "resumo",
    "mesh terms": "palavras_indexadas",
    "keywords": "palavras_chave", "author keywords": "palavras_chave",
    "times cited": "citacoes", "citing patents count": "", "citations": "citacoes",
    "scholarly citations": "citacoes", "cited by": "citacoes",
    "research organizations - standardized": "afiliacoes",
    "authors affiliations": "afiliacoes", "affiliations": "afiliacoes",
    "countries": "paises", "country of research organization": "paises",
    "publication type": "tipo_documento", "document type": "tipo_documento",
    "language": "idioma", "publisher": "editora", "issn": "issn", "volume": "volume",
    "issue": "numero", "pages": "paginas", "source urls": "url",
}


def ler_csv_generico(caminho, base):
    """Lê CSV de Dimensions, Lens ou qualquer exportação com cabeçalho reconhecível."""
    registros = []
    with open(caminho, encoding="utf-8-sig", newline="") as fh:
        # Dimensions insere linhas de cabeçalho antes da tabela
        posicao = fh.tell()
        primeira = fh.readline()
        if not re.search(r"(?i)\b(title|doi|authors)\b", primeira):
            for _ in range(5):
                posicao = fh.tell()
                linha = fh.readline()
                if re.search(r"(?i)\b(title|doi|authors)\b", linha):
                    break
        fh.seek(posicao)
        for i, linha in enumerate(csv.DictReader(fh)):
            baixa = {(k or "").strip().lower(): (v or "") for k, v in linha.items()}
            reg = registro_vazio(id="%s:%d" % (base, i), base_origem=base)
            for coluna, campo in COLUNAS_GENERICAS.items():
                if not campo or coluna not in baixa or not baixa[coluna].strip():
                    continue
                valor = baixa[coluna].strip()
                if campo in ("autores", "palavras_chave", "palavras_indexadas", "paises"):
                    if reg[campo]:
                        continue
                    reg[campo] = _partes(valor, ";" if ";" in valor else ",")
                elif campo in ("ano", "citacoes"):
                    if reg[campo]:
                        continue
                    reg[campo] = int(re.sub(r"\D", "", valor)[:4] or 0)
                elif reg[campo]:
                    continue
                else:
                    reg[campo] = valor
            reg["fonte_citacoes"] = base if reg["citacoes"] else ""
            if reg["titulo"]:
                registros.append(reg)
    return registros


# --------------------------------------------------------------------------- fontes abertas (JSON)

def _abstract_openalex(indice):
    """Reconstrói o resumo a partir do índice invertido que o OpenAlex devolve."""
    if not indice:
        return ""
    posicoes = []
    for palavra, indices in indice.items():
        for i in indices:
            posicoes.append((i, palavra))
    return " ".join(palavra for _, palavra in sorted(posicoes))


def _texto(valor):
    if isinstance(valor, list):
        return valor[0] if valor else ""
    return valor or ""


def ler_openalex_json(dados, origem="openalex"):
    """Converte a resposta crua do OpenAlex para registros do corpus."""
    registros = []
    for i, obra in enumerate(dados.get("results") or []):
        reg = registro_vazio(id="%s:%d" % (origem, i), base_origem=origem)
        reg["id_externo"] = (obra.get("id") or "").replace("https://openalex.org/", "openalex:")
        reg["doi"] = (obra.get("doi") or "").replace("https://doi.org/", "")
        reg["titulo"] = obra.get("title") or obra.get("display_name") or ""
        reg["ano"] = int(obra.get("publication_year") or 0)
        reg["citacoes"] = int(obra.get("cited_by_count") or 0)
        reg["fonte_citacoes"] = origem if reg["citacoes"] else ""
        reg["tipo_documento"] = obra.get("type") or ""
        reg["idioma"] = obra.get("language") or ""
        reg["resumo"] = _abstract_openalex(obra.get("abstract_inverted_index"))

        local = (obra.get("primary_location") or {}).get("source") or {}
        reg["fonte"] = local.get("display_name") or ""
        reg["issn"] = local.get("issn_l") or ""
        reg["editora"] = local.get("host_organization_name") or ""
        reg["url"] = obra.get("doi") or obra.get("id") or ""
        reg["acesso_aberto"] = str((obra.get("open_access") or {}).get("is_oa", "")).lower()

        afiliacoes, paises, instituicoes = [], [], []
        for autoria in obra.get("authorships") or []:
            autor = (autoria.get("author") or {}).get("display_name")
            if autor:
                reg["autores"].append(autor)
            orcid = (autoria.get("author") or {}).get("orcid")
            if orcid:
                reg["orcid"].append(orcid.replace("https://orcid.org/", ""))
            for instituicao in autoria.get("institutions") or []:
                nome = instituicao.get("display_name")
                if nome:
                    afiliacoes.append(nome)
                    if nome not in instituicoes:
                        instituicoes.append(nome)
                pais = instituicao.get("country_code")
                if pais and pais not in paises:
                    paises.append(pais)
        reg["afiliacoes"] = " ; ".join(afiliacoes)
        reg["instituicoes"] = instituicoes
        # o OpenAlex já entrega o país em ISO-2; o léxico do motor usa ISO-3, então
        # a conversão fica com o normalizador — aqui guardamos o que a fonte deu
        reg["paises"] = paises

        termos = []
        for chave in ("keywords", "concepts"):
            for termo in obra.get(chave) or []:
                nome = termo.get("display_name")
                if nome and nome not in termos:
                    termos.append(nome)
        reg["palavras_chave"] = termos

        reg["referencias"] = [
            (ref or "").replace("https://openalex.org/", "openalex:")
            for ref in obra.get("referenced_works") or []
        ]
        if reg["titulo"]:
            registros.append(reg)
    return registros


def _referencia_crossref(ref):
    """Monta uma referência legível a partir do registro estruturado do Crossref."""
    if ref.get("DOI"):
        return "doi:" + ref["DOI"].lower()
    if ref.get("unstructured"):
        return re.sub(r"\s+", " ", ref["unstructured"]).strip()
    partes = [ref.get("author"), ref.get("year"), _texto(ref.get("journal-title")),
              _texto(ref.get("article-title"))]
    return ", ".join(p for p in partes if p)


def ler_crossref_json(dados, origem="crossref"):
    """Converte a resposta crua do Crossref para registros do corpus."""
    registros = []
    itens = (dados.get("message") or {}).get("items") or []
    for i, obra in enumerate(itens):
        reg = registro_vazio(id="%s:%d" % (origem, i), base_origem=origem)
        reg["doi"] = (obra.get("DOI") or "").lower()
        reg["id_externo"] = "doi:" + reg["doi"] if reg["doi"] else ""
        reg["titulo"] = _texto(obra.get("title"))
        partes = ((obra.get("issued") or {}).get("date-parts") or [[None]])[0]
        reg["ano"] = int(partes[0]) if partes and partes[0] else 0
        reg["fonte"] = _texto(obra.get("container-title"))
        reg["issn"] = _texto(obra.get("ISSN"))
        reg["editora"] = obra.get("publisher") or ""
        reg["citacoes"] = int(obra.get("is-referenced-by-count") or 0)
        reg["fonte_citacoes"] = origem if reg["citacoes"] else ""
        reg["tipo_documento"] = obra.get("type") or ""
        reg["idioma"] = obra.get("language") or ""
        reg["resumo"] = re.sub(r"<[^>]+>", " ", obra.get("abstract") or "").strip()
        reg["volume"] = obra.get("volume") or ""
        reg["numero"] = obra.get("issue") or ""
        reg["paginas"] = obra.get("page") or ""
        reg["url"] = obra.get("URL") or ""
        reg["palavras_chave"] = list(obra.get("subject") or [])

        afiliacoes = []
        for autor in obra.get("author") or []:
            nome = ", ".join(p for p in (autor.get("family"), autor.get("given")) if p)
            if nome:
                reg["autores"].append(nome)
            if autor.get("ORCID"):
                reg["orcid"].append(autor["ORCID"].replace("http://orcid.org/", ""))
            for afiliacao in autor.get("affiliation") or []:
                if afiliacao.get("name"):
                    afiliacoes.append(afiliacao["name"])
        reg["afiliacoes"] = " ; ".join(afiliacoes)
        reg["referencias"] = [
            r for r in (_referencia_crossref(ref) for ref in obra.get("reference") or []) if r
        ]
        if reg["titulo"]:
            registros.append(reg)
    return registros


def ler_json(caminho):
    """Lê um JSON de fonte aberta, detectando OpenAlex ou Crossref pelo formato."""
    with open(caminho, encoding="utf-8") as fh:
        dados = json.load(fh)
    if isinstance(dados, dict) and "results" in dados:
        return ler_openalex_json(dados)
    if isinstance(dados, dict) and isinstance(dados.get("message"), dict):
        return ler_crossref_json(dados)
    if isinstance(dados, list):  # lista crua de obras do OpenAlex
        return ler_openalex_json({"results": dados})
    return []


# --------------------------------------------------------------------------- despacho

def detectar_base(nome):
    n = nome.lower()
    for base in ("scopus", "wos", "scielo", "dimensions", "lens", "openalex", "crossref"):
        if base in n:
            return base
    if "web_of_science" in n or "savedrecs" in n:
        return "wos"
    return "manual"


def ler_arquivo(caminho):
    """Lê um arquivo de exportação, escolhendo o parser por extensão e por nome."""
    base = detectar_base(os.path.basename(caminho))
    ext = os.path.splitext(caminho)[1].lower()
    if ext == ".csv":
        return ler_scopus_csv(caminho) if base == "scopus" else ler_csv_generico(caminho, base)
    if ext in (".txt", ".ciw"):
        return ler_wos_txt(caminho)
    if ext == ".bib":
        return ler_bibtex(caminho, base)
    if ext == ".ris":
        return ler_ris(caminho, base)
    if ext == ".json":
        return ler_json(caminho)
    return []


def ler_diretorio(diretorio):
    """Lê todos os arquivos de exportação de um diretório, recursivamente."""
    registros, relatorio = [], []
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in sorted(arquivos):
            if arquivo.startswith("."):
                continue
            caminho = os.path.join(raiz, arquivo)
            if os.path.splitext(arquivo)[1].lower() not in (
                    ".csv", ".txt", ".bib", ".ris", ".ciw", ".json"):
                continue
            try:
                lidos = ler_arquivo(caminho)
            except Exception as erro:  # arquivo corrompido não interrompe a importação
                relatorio.append((caminho, 0, "ERRO: %s" % erro))
                continue
            for j, reg in enumerate(lidos):
                reg["id"] = "%s:%s:%d" % (reg["base_origem"], os.path.basename(caminho), j)
                reg["bases_todas"] = [reg["base_origem"]]
            registros.extend(lidos)
            relatorio.append((caminho, len(lidos), "ok"))
    return registros, relatorio
