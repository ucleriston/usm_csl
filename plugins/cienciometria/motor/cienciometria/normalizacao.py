"""Normalização de texto, nomes, fontes, países e palavras-chave.

Toda unificação passa por tesauro versionado em config/ (livro de códigos, §7):
nenhuma equivalência fica embutida no código, para que a decisão seja auditável.
"""

import json
import os
import re
import unicodedata

PARTICULAS = {"de", "da", "do", "das", "dos", "van", "von", "del", "della", "di", "la", "le", "el"}

_CACHE = {}


def sem_acento(texto):
    nfkd = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def chave_texto(texto):
    """Chave canônica: minúsculas, sem acento, sem pontuação, espaços colapsados."""
    t = sem_acento(texto or "").lower()
    t = re.sub(r"[^a-z0-9 ]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def normalizar_doi(doi):
    d = (doi or "").strip().lower()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    return d.strip()


def carregar_tesauro(caminho):
    """Carrega um tesauro JSON {variante: forma canônica}; chaves em minúsculas."""
    if caminho in _CACHE:
        return _CACHE[caminho]
    dados = {}
    if caminho and os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as fh:
            bruto = json.load(fh)
        # chaves iniciadas por "_" são comentários do arquivo, não entradas
        dados = {chave_texto(k): v for k, v in bruto.items() if not k.startswith("_")}
    _CACHE[caminho] = dados
    return dados


def aplicar_tesauro(valor, tesauro, padrao_maiusculas=True):
    if not valor:
        return ""
    canon = tesauro.get(chave_texto(valor))
    if canon:
        return canon
    return valor.upper().strip() if padrao_maiusculas else valor.strip()


def _capitalizar(palavra):
    """Capitaliza preservando compostos com hífen ou apóstrofo: Ter-Minassian, O'Brien."""
    return re.sub(r"[A-Za-zÀ-ÿ]+", lambda m: m.group(0).capitalize(), palavra)


def _e_iniciais(token):
    """Reconhece um bloco de iniciais: 'M', 'W.E.', 'N.J.', 'JR' não conta como nome."""
    limpo = token.replace(".", "")
    return 1 <= len(limpo) <= 3 and limpo.isalpha() and limpo.isupper()


def normalizar_autor(nome):
    """Devolve 'Sobrenome, I. J.' preservando partículas no sobrenome.

    Aceita 'Sobrenome, Nome', 'Nome Sobrenome' e 'SOBRENOME N'.
    """
    nome = re.sub(r"\s+", " ", (nome or "").strip().strip(".,;"))
    if not nome:
        return ""
    if "," in nome:
        sobrenome, resto = nome.split(",", 1)
    else:
        partes = nome.split(" ")
        if len(partes) == 1:
            return partes[0].title()
        corte_iniciais = len(partes)
        while corte_iniciais > 1 and _e_iniciais(partes[corte_iniciais - 1]):
            corte_iniciais -= 1
        if corte_iniciais < len(partes):
            # formato Scopus/WoS: "Oates W.E.", "Oates W E", "Arretche M.", "de Mello L."
            sobrenome = " ".join(partes[:corte_iniciais])
            resto = " ".join(partes[corte_iniciais:])
        else:
            # a primeira partícula depois do prenome abre o sobrenome composto
            corte = len(partes) - 1
            for i in range(1, len(partes) - 1):
                if partes[i].lower() in PARTICULAS:
                    corte = i
                    break
            sobrenome = " ".join(partes[corte:])
            resto = " ".join(partes[:corte])
    iniciais = [p[0].upper() + "." for p in re.split(r"[\s.\-]+", resto) if p]
    sobrenome = " ".join(
        w.lower() if w.lower() in PARTICULAS else _capitalizar(w) for w in sobrenome.split()
    )
    return (sobrenome + (", " + " ".join(iniciais) if iniciais else "")).strip()


def normalizar_palavras(palavras, tesauro):
    """Normaliza e desduplica uma lista de palavras-chave preservando a ordem."""
    vistos, saida = set(), []
    for p in palavras or []:
        termo = aplicar_tesauro(re.sub(r"\s+", " ", p.strip(" .;,")), tesauro)
        if termo and termo not in vistos:
            vistos.add(termo)
            saida.append(termo)
    return saida


def extrair_paises(afiliacoes, lexico):
    """Extrai códigos ISO-3 de país a partir do texto de afiliação.

    O léxico mapeia topônimos (país, e também estados/cidades quando declarados
    em config/lexico-paises.json) para o código do país.
    """
    texto = chave_texto(afiliacoes)
    achados = []
    for termo, iso in lexico.items():
        if not termo:
            continue
        if re.search(r"(?<![a-z])" + re.escape(termo) + r"(?![a-z])", texto):
            if iso not in achados:
                achados.append(iso)
    return achados


def converter_paises(codigos, tabela):
    """Converte ISO-2 (como o OpenAlex devolve) para ISO-3; o que não constar passa adiante."""
    saida = []
    for codigo in codigos or []:
        limpo = (codigo or "").strip().upper()
        if not limpo:
            continue
        convertido = tabela.get(chave_texto(limpo), limpo) if len(limpo) == 2 else limpo
        if convertido not in saida:
            saida.append(convertido)
    return saida


def normalizar_registro(reg, tesauros):
    """Aplica todas as normalizações a um registro já importado."""
    reg["doi"] = normalizar_doi(reg.get("doi"))
    reg["titulo"] = re.sub(r"\s+", " ", (reg.get("titulo") or "").strip())
    reg["titulo_norm"] = chave_texto(reg["titulo"])
    reg["autores"] = [a for a in (normalizar_autor(a) for a in reg.get("autores", [])) if a]
    reg["n_autores"] = len(reg["autores"])
    reg["fonte"] = aplicar_tesauro(reg.get("fonte"), tesauros["fontes"])
    reg["palavras_chave"] = normalizar_palavras(reg.get("palavras_chave"), tesauros["termos"])
    reg["palavras_indexadas"] = normalizar_palavras(
        reg.get("palavras_indexadas"), tesauros["termos"]
    )
    reg["issn"] = re.sub(r"[^0-9Xx]", "", reg.get("issn") or "").upper()
    if not reg.get("instituicoes"):
        reg["instituicoes"] = instituicoes_de_afiliacao(
            reg.get("afiliacoes", ""), tesauros["instituicoes"]
        )
    if reg.get("paises"):
        reg["paises"] = converter_paises(reg["paises"], tesauros.get("iso2", {}))
    else:
        reg["paises"] = extrair_paises(reg.get("afiliacoes", ""), tesauros["paises"])
    reg["colab_internacional"] = 1 if len(reg["paises"]) > 1 else 0
    reg["n_referencias"] = len(reg.get("referencias", []))
    reg["idioma"] = normalizar_idioma(reg.get("idioma"))
    reg["tipo_documento"] = normalizar_tipo(reg.get("tipo_documento"))
    return reg


def instituicoes_de_afiliacao(afiliacoes, tesauro):
    """Segmenta o campo de afiliação e normaliza cada instituição pelo tesauro."""
    instituicoes, vistos = [], set()
    for bloco in re.split(r"[;\n]", afiliacoes or ""):
        for parte in bloco.split(","):
            parte = parte.strip()
            if not re.search(
                r"\b(univ|universidade|university|universidad|inst|faculdade|school|college|"
                r"centro|center|fundacao|foundation|escola|academy|academia)\b",
                sem_acento(parte).lower(),
            ):
                continue
            nome = aplicar_tesauro(parte, tesauro)
            if nome and nome not in vistos:
                vistos.add(nome)
                instituicoes.append(nome)
    return instituicoes


_IDIOMAS = {
    "english": "en", "en": "en", "ingles": "en",
    "portuguese": "pt", "pt": "pt", "portugues": "pt",
    "spanish": "es", "es": "es", "espanhol": "es", "castellano": "es",
}

_TIPOS = {
    "article": "artigo", "ar": "artigo", "j": "artigo", "artigo": "artigo",
    "review": "revisao", "re": "revisao", "revisao": "revisao",
    "book chapter": "capitulo", "chapter": "capitulo", "ch": "capitulo", "capitulo": "capitulo",
    "conference paper": "anais", "proceedings paper": "anais", "cp": "anais", "anais": "anais",
}


def normalizar_idioma(valor):
    return _IDIOMAS.get(chave_texto(valor), chave_texto(valor)[:2])


def normalizar_tipo(valor):
    return _TIPOS.get(chave_texto(valor), chave_texto(valor))


def carregar_tesauros(dir_config):
    """Carrega, de uma vez, os quatro tesauros usados pelo pipeline."""
    j = lambda nome: os.path.join(dir_config, nome)
    return {
        "termos": carregar_tesauro(j("thesauro-termos.json")),
        "fontes": carregar_tesauro(j("thesauro-fontes.json")),
        "instituicoes": carregar_tesauro(j("thesauro-instituicoes.json")),
        "paises": carregar_tesauro(j("lexico-paises.json")),
        "iso2": carregar_tesauro(j("iso2-iso3.json")),
    }
