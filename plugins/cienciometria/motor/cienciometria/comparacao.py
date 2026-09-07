"""Compara duas exportações de busca e mede o que mudou entre elas.

Calibrar uma string é decidir, uma alteração de cada vez, se o que ela derruba é
ruído ou literatura pertinente. Isso não se responde pela contagem total: dois
resultados de 400 registros podem não ter os mesmos 400. O que interessa é quais
registros saíram, quais entraram, e de que periódicos eles vêm.
"""

import os
from collections import Counter

from . import parsers
from .normalizacao import chave_texto, normalizar_doi


def _chave(reg):
    """DOI quando houver; senão, título normalizado com o ano."""
    doi = normalizar_doi(reg.get("doi"))
    if doi:
        return doi
    return "%s|%s" % (chave_texto(reg.get("titulo")), reg.get("ano") or "")


def _ler(caminho):
    if os.path.isdir(caminho):
        registros, _ = parsers.ler_diretorio(caminho)
        return registros
    return parsers.ler_arquivo(caminho)


def comparar(caminho_antes, caminho_depois):
    """Devolve o que saiu, o que entrou e o que permaneceu entre duas buscas."""
    antes, depois = _ler(caminho_antes), _ler(caminho_depois)
    indice_antes = {_chave(r): r for r in antes if _chave(r)}
    indice_depois = {_chave(r): r for r in depois if _chave(r)}

    perdidos = [indice_antes[k] for k in indice_antes if k not in indice_depois]
    ganhos = [indice_depois[k] for k in indice_depois if k not in indice_antes]
    mantidos = [k for k in indice_antes if k in indice_depois]

    def fontes(registros):
        contagem = Counter((r.get("fonte") or "sem fonte").strip().upper() for r in registros)
        return [{"fonte": f, "registros": n} for f, n in contagem.most_common(15)]

    def tabela(registros):
        return [
            {
                "doi": r.get("doi", ""),
                "ano": r.get("ano", ""),
                "titulo": r.get("titulo", ""),
                "fonte": r.get("fonte", ""),
                "citacoes": r.get("citacoes", 0),
                "autores": "; ".join((r.get("autores") or [])[:3]),
            }
            for r in sorted(registros, key=lambda x: -int(x.get("citacoes") or 0))
        ]

    total_antes = len(indice_antes)
    return {
        "antes": total_antes,
        "depois": len(indice_depois),
        "mantidos": len(mantidos),
        "perdidos": len(perdidos),
        "ganhos": len(ganhos),
        "retencao_%": round(100 * len(mantidos) / total_antes, 2) if total_antes else 0.0,
        "tabela_perdidos": tabela(perdidos),
        "tabela_ganhos": tabela(ganhos),
        "fontes_dos_perdidos": fontes(perdidos),
        "mais_citado_perdido": tabela(perdidos)[0] if perdidos else None,
    }
