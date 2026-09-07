"""Leitura e escrita do corpus em CSV e utilidades de saída."""

import csv
import os
import sys

from .modelo import CAMPOS, desserializar, serializar

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))


def salvar_corpus(caminho, registros):
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=CAMPOS)
        escritor.writeheader()
        for reg in registros:
            escritor.writerow(serializar(reg))
    return len(registros)


def carregar_corpus(caminho):
    with open(caminho, encoding="utf-8-sig", newline="") as fh:
        return [desserializar(linha) for linha in csv.DictReader(fh)]


def salvar_tabela(caminho, linhas, colunas=None):
    """Grava uma lista de dicionários em CSV; cria diretórios se necessário."""
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    colunas = colunas or (list(linhas[0].keys()) if linhas else ["vazio"])
    with open(caminho, "w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=colunas, extrasaction="ignore")
        escritor.writeheader()
        for linha in linhas:
            escritor.writerow(linha)
    return len(linhas)


def salvar_arestas(caminho, arestas, pesos_normalizados=None):
    linhas = []
    for (a, b), peso in sorted(arestas.items(), key=lambda kv: -kv[1]):
        linha = {"origem": a, "destino": b, "peso": peso}
        if pesos_normalizados:
            linha["forca_associacao"] = round(pesos_normalizados.get((a, b), 0.0), 4)
        linhas.append(linha)
    colunas = ["origem", "destino", "peso"] + (["forca_associacao"] if pesos_normalizados else [])
    return salvar_tabela(caminho, linhas, colunas)


def salvar_nos(caminho, nos, agrupamentos=None):
    linhas = [
        {
            "item": no,
            "frequencia": freq,
            "agrupamento": (agrupamentos or {}).get(no, ""),
        }
        for no, freq in sorted(nos.items(), key=lambda kv: -kv[1])
    ]
    return salvar_tabela(caminho, linhas, ["item", "frequencia", "agrupamento"])


def registrar_execucao(dir_saida, comando, detalhes):
    """Anexa uma linha ao log de auditoria (docs/06-reprodutibilidade.md, §7)."""
    import datetime
    import subprocess

    os.makedirs(dir_saida, exist_ok=True)
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True, text=True, timeout=10, check=False,
        ).stdout.strip() or "sem-git"
    except Exception:
        commit = "sem-git"
    with open(os.path.join(dir_saida, "execucao.log"), "a", encoding="utf-8") as fh:
        fh.write("%s\t%s\tcommit=%s\t%s\n" % (
            datetime.datetime.now().isoformat(timespec="seconds"), comando, commit, detalhes))
