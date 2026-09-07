"""Leitura das exportações das bases.

Formatos suportados:
  * Scopus CSV (todos os campos)
  * Web of Science plain text (Full Record and Cited References)
  * Dimensions CSV e Lens CSV (detectados pelo cabeçalho)
  * BibTeX (.bib) e RIS (.ris) — usados pelo SciELO e pelos gerenciadores

Cada função devolve uma lista de registros no formato de modelo.registro_vazio().
"""

import csv
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


# --------------------------------------------------------------------------- despacho

def detectar_base(nome):
    n = nome.lower()
    for base in ("scopus", "wos", "scielo", "dimensions", "lens"):
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
    return []


def ler_diretorio(diretorio):
    """Lê todos os arquivos de exportação de um diretório, recursivamente."""
    registros, relatorio = [], []
    for raiz, _, arquivos in os.walk(diretorio):
        for arquivo in sorted(arquivos):
            if arquivo.startswith("."):
                continue
            caminho = os.path.join(raiz, arquivo)
            if os.path.splitext(arquivo)[1].lower() not in (".csv", ".txt", ".bib", ".ris", ".ciw"):
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
