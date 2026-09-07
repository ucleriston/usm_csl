"""Modelo de dados do corpus.

Um registro é um dicionário com as chaves de CAMPOS. Campos de lista são
guardados em memória como list[str] e serializados em CSV com ';'.
"""

SEP = "; "

CAMPOS = [
    "id",
    "doi",
    "base_origem",
    "bases_todas",
    "titulo",
    "titulo_norm",
    "autores",
    "n_autores",
    "orcid",
    "afiliacoes",
    "instituicoes",
    "paises",
    "colab_internacional",
    "ano",
    "fonte",
    "issn",
    "tipo_documento",
    "idioma",
    "editora",
    "volume",
    "numero",
    "paginas",
    "resumo",
    "palavras_chave",
    "palavras_indexadas",
    "citacoes",
    "fonte_citacoes",
    "citacoes_por_ano",
    "referencias",
    "n_referencias",
    "url",
    # codificação manual (livro de códigos, §5)
    "nivel_ente",
    "abordagem",
    "tema_declarado",
    "pais_do_caso",
    "forma_estado",
    "periodo_analisado",
    "metodo_principal",
    "decisao_triagem",
    "codigo_exclusao",
    "revisor",
    "nota",
]

CAMPOS_LISTA = {
    "autores",
    "orcid",
    "instituicoes",
    "paises",
    "palavras_chave",
    "palavras_indexadas",
    "referencias",
    "bases_todas",
    "nivel_ente",
    "tema_declarado",
    "pais_do_caso",
}

CAMPOS_INT = {"ano", "n_autores", "citacoes", "n_referencias", "colab_internacional"}

# Precedência de metadados na deduplicação (livro de códigos, §8).
PRIORIDADE_BASES = ["scopus", "wos", "dimensions", "lens", "scielo", "manual"]

CODIGOS_EXCLUSAO = {
    "E1": "Federalismo apenas político, sem componente fiscal",
    "E2": "Finanças do governo central, sem recorte subnacional",
    "E3": "Descentralização sem componente fiscal",
    "E4": "Editorial, resenha, errata, carta, entrevista",
    "E5": "Metadado insuficiente",
    "E6": "Duplicata",
    "E7": "Menção marginal ou metafórica",
    "E8": "Texto integral indisponível",
}


def registro_vazio(**kwargs):
    """Cria um registro com todos os campos, aplicando os valores informados."""
    reg = {}
    for campo in CAMPOS:
        if campo in CAMPOS_LISTA:
            reg[campo] = []
        elif campo in CAMPOS_INT:
            reg[campo] = 0
        else:
            reg[campo] = ""
    reg.update({k: v for k, v in kwargs.items() if k in reg})
    return reg


def serializar(reg):
    """Converte um registro para linha de CSV (todos os valores em texto)."""
    linha = {}
    for campo in CAMPOS:
        valor = reg.get(campo, "")
        if campo in CAMPOS_LISTA:
            valor = SEP.join(str(v) for v in valor if str(v).strip())
        linha[campo] = "" if valor is None else str(valor)
    return linha


def desserializar(linha):
    """Converte uma linha de CSV de volta para registro."""
    reg = registro_vazio()
    for campo in CAMPOS:
        bruto = (linha.get(campo) or "").strip()
        if campo in CAMPOS_LISTA:
            reg[campo] = [p.strip() for p in bruto.split(";") if p.strip()]
        elif campo in CAMPOS_INT:
            try:
                reg[campo] = int(float(bruto)) if bruto else 0
            except ValueError:
                reg[campo] = 0
        else:
            reg[campo] = bruto
    return reg
