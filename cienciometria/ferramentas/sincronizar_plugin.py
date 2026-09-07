"""Sincroniza o plugin com o motor deste repositório.

O motor é a fonte de verdade; o plugin em `plugins/cienciometria/` é uma cópia
versionada para que possa ser instalado e usado fora daqui. Rodar após qualquer
mudança no motor:

    python3 ferramentas/sincronizar_plugin.py           # copia
    python3 ferramentas/sincronizar_plugin.py --conferir  # só verifica (usado nos testes)
"""

import filecmp
import os
import shutil
import sys

RAIZ_MOTOR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ_REPO = os.path.dirname(RAIZ_MOTOR)
DESTINO = os.path.join(RAIZ_REPO, "plugins", "cienciometria")

# (origem relativa ao motor, destino relativo ao plugin)
COPIAS = [
    ("src/cienciometria", "motor/cienciometria"),
    ("docs", "docs"),
    ("config", "config"),
    ("modelos/revisao-modelo", "modelos/revisao-modelo"),
    ("modelos/ficha-de-extracao.md", "modelos/ficha-de-extracao.md"),
    ("modelos/registro-de-decisoes.csv", "modelos/registro-de-decisoes.csv"),
]

IGNORAR = shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store")


def _arquivos(raiz):
    saida = []
    for pasta, _, arquivos in os.walk(raiz):
        if "__pycache__" in pasta:
            continue
        for arquivo in arquivos:
            if arquivo.endswith(".pyc") or arquivo == ".DS_Store":
                continue
            caminho = os.path.join(pasta, arquivo)
            saida.append(os.path.relpath(caminho, raiz))
    return sorted(saida)


def conferir():
    """Devolve a lista de diferenças entre motor e plugin (vazia = sincronizado)."""
    diferencas = []
    for origem_rel, destino_rel in COPIAS:
        origem = os.path.join(RAIZ_MOTOR, origem_rel)
        destino = os.path.join(DESTINO, destino_rel)
        if os.path.isfile(origem):
            if not os.path.exists(destino) or not filecmp.cmp(origem, destino, shallow=False):
                diferencas.append(destino_rel)
            continue
        if not os.path.isdir(destino):
            diferencas.append(destino_rel + " (ausente)")
            continue
        no_motor, no_plugin = _arquivos(origem), _arquivos(destino)
        for relativo in sorted(set(no_motor) | set(no_plugin)):
            a = os.path.join(origem, relativo)
            b = os.path.join(destino, relativo)
            if not os.path.exists(a):
                diferencas.append(os.path.join(destino_rel, relativo) + " (sobra no plugin)")
            elif not os.path.exists(b):
                diferencas.append(os.path.join(destino_rel, relativo) + " (falta no plugin)")
            elif not filecmp.cmp(a, b, shallow=False):
                diferencas.append(os.path.join(destino_rel, relativo) + " (difere)")
    return diferencas


def sincronizar():
    for origem_rel, destino_rel in COPIAS:
        origem = os.path.join(RAIZ_MOTOR, origem_rel)
        destino = os.path.join(DESTINO, destino_rel)
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        if os.path.isfile(origem):
            shutil.copy2(origem, destino)
            continue
        if os.path.isdir(destino):
            shutil.rmtree(destino)
        shutil.copytree(origem, destino, ignore=IGNORAR)
    # as revisões do usuário não vão para o plugin; só o esqueleto
    for pasta in ("dados/bruto", "dados/processado", "saidas"):
        caminho = os.path.join(DESTINO, "modelos", "revisao-modelo", pasta)
        os.makedirs(caminho, exist_ok=True)
        marcador = os.path.join(caminho, ".gitkeep")
        if not os.path.exists(marcador):
            open(marcador, "w").close()
    return len(COPIAS)


if __name__ == "__main__":
    if "--conferir" in sys.argv:
        diferencas = conferir()
        if diferencas:
            print("Plugin dessincronizado do motor:")
            for d in diferencas:
                print("  " + d)
            print("\nRode: python3 ferramentas/sincronizar_plugin.py")
            sys.exit(1)
        print("Plugin sincronizado com o motor.")
    else:
        print("%d conjuntos copiados para %s" % (sincronizar(), os.path.relpath(DESTINO, RAIZ_REPO)))
