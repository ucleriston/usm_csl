"""Coleta de registros em fontes abertas: OpenAlex e Crossref.

Existe para quem não tem acesso a Scopus ou Web of Science. As duas APIs são
públicas, não exigem chave e devolvem, no caso do OpenAlex, também as
referências citadas — sem elas não há co-citação.

O que é salvo em dados/bruto/ é a **resposta crua**, página por página, em JSON.
O mapeamento para o modelo do corpus acontece depois, na importação: assim, se o
mapeamento precisar de ajuste, basta reimportar, sem consultar a API de novo.

Uso pela linha de comando:

    cienciometria coletar --revisao <slug> --fonte openalex \\
        --busca "fiscal federalism" --de 1990 --ate 2026 --email voce@exemplo.org
"""

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from . import __version__

OPENALEX = "https://api.openalex.org/works"
CROSSREF = "https://api.crossref.org/works"
POR_PAGINA = 200
PAUSA = 0.2  # cortesia entre páginas; as duas APIs pedem uso comedido


class ColetaBloqueada(RuntimeError):
    """A rede recusou a consulta (política de egresso, bloqueio ou API fora do ar)."""


def _pedir(url, email, tentativas=4):
    """GET com repetição e espera crescente. Erros de política não são repetidos."""
    cabecalho = {
        "User-Agent": "cienciometria/%s (mailto:%s)" % (__version__, email or "sem-email"),
        "Accept": "application/json",
    }
    espera = 2
    for tentativa in range(1, tentativas + 1):
        try:
            with urllib.request.urlopen(
                urllib.request.Request(url, headers=cabecalho), timeout=60
            ) as resposta:
                return json.load(resposta)
        except urllib.error.HTTPError as erro:
            if erro.code in (403, 401):
                raise ColetaBloqueada(
                    "a API recusou a consulta (HTTP %d). Se você está num ambiente com política "
                    "de egresso, o host %s pode estar bloqueado — reporte o host em vez de tentar "
                    "contornar." % (erro.code, urllib.parse.urlparse(url).hostname)
                )
            if erro.code not in (429, 500, 502, 503, 504) or tentativa == tentativas:
                raise ColetaBloqueada("HTTP %d ao consultar %s" % (erro.code, url))
        except urllib.error.URLError as erro:
            if tentativa == tentativas:
                raise ColetaBloqueada(
                    "não foi possível alcançar a API (%s). Verifique a rede; se houver proxy com "
                    "política de egresso, o host pode estar bloqueado." % erro.reason
                )
        time.sleep(espera)
        espera *= 2
    raise ColetaBloqueada("falha ao consultar %s" % url)


# --------------------------------------------------------------------------- OpenAlex

def _filtros_openalex(busca, de, ate, tipos, idiomas, extra):
    filtros = []
    if busca:
        filtros.append("title_and_abstract.search:%s" % busca)
    if de:
        filtros.append("from_publication_date:%d-01-01" % int(de))
    if ate:
        filtros.append("to_publication_date:%d-12-31" % int(ate))
    if tipos:
        filtros.append("type:%s" % "|".join(tipos))
    if idiomas:
        filtros.append("language:%s" % "|".join(idiomas))
    if extra:
        filtros.append(extra)
    return ",".join(filtros)


def coletar_openalex(busca, destino, de=None, ate=None, tipos=None, idiomas=None,
                     email=None, limite=5000, extra=None, ao_avancar=None):
    """Baixa os resultados por cursor e grava uma página por arquivo JSON."""
    filtro = _filtros_openalex(busca, de, ate, tipos, idiomas, extra)
    cursor, baixados, paginas = "*", 0, []
    while cursor and baixados < limite:
        parametros = {
            "filter": filtro,
            "per-page": min(POR_PAGINA, limite - baixados),
            "cursor": cursor,
        }
        if email:
            parametros["mailto"] = email
        url = OPENALEX + "?" + urllib.parse.urlencode(parametros)
        dados = _pedir(url, email)
        registros = dados.get("results") or []
        if not registros:
            break
        caminho = os.path.join(destino, "openalex_pagina_%03d.json" % (len(paginas) + 1))
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False)
        paginas.append(caminho)
        baixados += len(registros)
        cursor = (dados.get("meta") or {}).get("next_cursor")
        if ao_avancar:
            ao_avancar(baixados, (dados.get("meta") or {}).get("count"))
        time.sleep(PAUSA)
    return {"fonte": "openalex", "filtro": filtro, "registros": baixados, "paginas": paginas}


# --------------------------------------------------------------------------- Crossref

def coletar_crossref(busca, destino, de=None, ate=None, tipos=None, email=None,
                     limite=5000, ao_avancar=None):
    """Crossref tem cobertura enorme, mas metadados mais pobres que o OpenAlex.

    Em especial, as referências citadas só vêm quando a editora as deposita, e as
    afiliações costumam estar ausentes — o que limita as redes de colaboração.
    """
    cursor, baixados, paginas = "*", 0, []
    filtros = []
    if de:
        filtros.append("from-pub-date:%d-01-01" % int(de))
    if ate:
        filtros.append("until-pub-date:%d-12-31" % int(ate))
    for tipo in tipos or []:
        filtros.append("type:%s" % tipo)
    while cursor and baixados < limite:
        parametros = {
            "query.bibliographic": busca,
            "rows": min(100, limite - baixados),
            "cursor": cursor,
        }
        if filtros:
            parametros["filter"] = ",".join(filtros)
        if email:
            parametros["mailto"] = email
        url = CROSSREF + "?" + urllib.parse.urlencode(parametros)
        dados = _pedir(url, email)
        mensagem = dados.get("message") or {}
        registros = mensagem.get("items") or []
        if not registros:
            break
        caminho = os.path.join(destino, "crossref_pagina_%03d.json" % (len(paginas) + 1))
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(dados, fh, ensure_ascii=False)
        paginas.append(caminho)
        baixados += len(registros)
        cursor = mensagem.get("next-cursor")
        if ao_avancar:
            ao_avancar(baixados, mensagem.get("total-results"))
        time.sleep(PAUSA)
    return {"fonte": "crossref", "filtro": ";".join(filtros), "registros": baixados,
            "paginas": paginas}


def coletar(fonte, **kwargs):
    if fonte == "openalex":
        return coletar_openalex(**kwargs)
    if fonte == "crossref":
        kwargs.pop("idiomas", None)
        kwargs.pop("extra", None)
        return coletar_crossref(**kwargs)
    raise ValueError("fonte desconhecida: %s (use openalex ou crossref)" % fonte)
