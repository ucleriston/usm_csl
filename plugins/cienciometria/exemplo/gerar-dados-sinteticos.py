"""Gera a amostra SINTÉTICA da revisão de demonstração (revisoes/exemplo-sintetico).

Nenhum registro produzido aqui é real: autores, títulos e citações são fabricados
por combinação determinística (semente fixa) apenas para exercitar os parsers, a
deduplicação e os indicadores. Não usar como dado de pesquisa.

    python testes/gerar_exemplo.py [pasta de destino]

Sem argumento, escreve na revisão de demonstração do repositório. Instalado como
plugin, receba a pasta `dados/bruto` da revisão onde os arquivos devem entrar.
"""

import csv
import os
import random

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "revisoes", "exemplo-sintetico", "dados", "bruto")

SOBRENOMES = ["Alfa", "Beta", "Gama", "Delta", "Epsilon", "Zeta", "Eta", "Teta", "Iota", "Kapa"]
INICIAIS = ["A.", "B.", "C.", "D.", "E.", "F."]
FONTES = [
    ("National Tax Journal", "00280283"),
    ("International Tax and Public Finance", "09275940"),
    ("Journal of Public Economics", "00472727"),
    ("Publius: The Journal of Federalism", "00485950"),
    ("Revista de Administracao Publica", "00347612"),
    ("Nova Economia", "01036351"),
    ("Gestion y Politica Publica", "14054981"),
]
TERMOS = [
    "fiscal federalism", "fiscal decentralization", "intergovernmental transfers",
    "revenue sharing", "local government", "subnational debt", "tax competition",
    "fiscal capacity", "tax effort", "fiscal equalization", "municipal finance",
    "soft budget constraint", "state capacity", "tax reform", "regional inequality",
]
TITULOS = [
    "%s and %s in subnational governments: evidence from %s",
    "The political economy of %s: %s and the role of %s",
    "Measuring %s across municipalities: %s and %s",
    "%s revisited: %s under %s",
]
PAISES = [
    ("Universidade Federal de Pernambuco, Recife, Brazil", "BRA"),
    ("Universidade de Sao Paulo, Sao Paulo, Brazil", "BRA"),
    ("University of Toronto, Toronto, Canada", "CAN"),
    ("Georgia State University, Atlanta, United States", "USA"),
    ("Universidad de Buenos Aires, Buenos Aires, Argentina", "ARG"),
    ("Universidad Nacional Autonoma de Mexico, Mexico", "MEX"),
]


def gerar(n=120, semente=7):
    rng = random.Random(semente)
    registros = []
    for i in range(n):
        ano = rng.choices(range(1992, 2026), weights=[1 + (a - 1990) ** 1.4 for a in range(1992, 2026)])[0]
        autores = [
            "%s %s" % (rng.choice(SOBRENOMES), rng.choice(INICIAIS))
            for _ in range(rng.randint(1, 4))
        ]
        termos = rng.sample(TERMOS, rng.randint(3, 5))
        fonte, issn = rng.choice(FONTES)
        afiliacoes = rng.sample(PAISES, rng.randint(1, 2))
        titulo = (rng.choice(TITULOS) % tuple(
            x.capitalize() for x in rng.sample(TERMOS + ["Brazil", "Argentina", "Canada"], 3)
        ))
        idade = 2026 - ano
        registros.append(
            {
                "autores": autores,
                "titulo": "%s [registro sintetico %03d]" % (titulo, i),
                "ano": ano,
                "fonte": fonte,
                "issn": issn,
                "doi": "10.5555/exemplo.%04d" % i,
                "citacoes": max(0, int(rng.gammavariate(1.6, 6) * (idade / 8.0))),
                "palavras": termos,
                "afiliacoes": "; ".join(a for a, _ in afiliacoes),
                "referencias": [
                    "%s %s, %d, %s, V%d, P%d" % (
                        rng.choice(SOBRENOMES).upper(), rng.choice(INICIAIS),
                        rng.randint(max(1970, ano - 30), ano),
                        rng.choice(FONTES)[0].upper(), rng.randint(1, 60), rng.randint(1, 400))
                    for _ in range(rng.randint(8, 30))
                ],
                "resumo": "Resumo sintetico para teste do pipeline. Trata de %s em entes subnacionais." %
                          ", ".join(termos[:2]),
            }
        )
    return registros


def escrever_scopus(registros, caminho):
    colunas = ["Authors", "Title", "Year", "Source title", "Volume", "Issue", "Page start",
               "Cited by", "DOI", "Affiliations", "Abstract", "Author Keywords", "References",
               "Document Type", "Language of Original Document", "Publisher", "ISSN"]
    with open(caminho, "w", encoding="utf-8", newline="") as fh:
        escritor = csv.DictWriter(fh, fieldnames=colunas)
        escritor.writeheader()
        for r in registros:
            escritor.writerow({
                "Authors": "; ".join(r["autores"]),
                "Title": r["titulo"],
                "Year": r["ano"],
                "Source title": r["fonte"],
                "Volume": 1, "Issue": 1, "Page start": 1,
                "Cited by": r["citacoes"],
                "DOI": r["doi"],
                "Affiliations": r["afiliacoes"],
                "Abstract": r["resumo"],
                "Author Keywords": "; ".join(r["palavras"]),
                "References": "; ".join(r["referencias"]),
                "Document Type": "Article",
                "Language of Original Document": "English",
                "Publisher": "Editora Sintetica",
                "ISSN": r["issn"],
            })


def escrever_wos(registros, caminho):
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write("FN Arquivo sintetico\nVR 1.0\n")
        for r in registros:
            fh.write("PT J\n")
            for i, autor in enumerate(r["autores"]):
                fh.write(("AU " if i == 0 else "   ") + autor + "\n")
            fh.write("TI %s\n" % r["titulo"])
            fh.write("SO %s\n" % r["fonte"])
            fh.write("DE %s\n" % "; ".join(r["palavras"]))
            fh.write("C1 %s\n" % r["afiliacoes"])
            fh.write("AB %s\n" % r["resumo"])
            for i, ref in enumerate(r["referencias"]):
                fh.write(("CR " if i == 0 else "   ") + ref + "\n")
            fh.write("TC %d\n" % r["citacoes"])
            fh.write("PY %d\n" % r["ano"])
            fh.write("DI %s\n" % r["doi"])
            fh.write("LA English\nDT Article\n")
            fh.write("SN %s\n" % r["issn"])
            fh.write("ER\n\n")


def escrever_openalex(registros, caminho):
    """Grava no formato cru do OpenAlex, para exercitar também o parser de fonte aberta."""
    import json

    def invertido(texto):
        indice = {}
        for posicao, palavra in enumerate(texto.split()):
            indice.setdefault(palavra, []).append(posicao)
        return indice

    obras = []
    for i, r in enumerate(registros):
        obras.append({
            "id": "https://openalex.org/W90000%04d" % i,
            "doi": "https://doi.org/" + r["doi"],
            "title": r["titulo"],
            "publication_year": r["ano"],
            "cited_by_count": r["citacoes"],
            "type": "article",
            "language": "en",
            "abstract_inverted_index": invertido(r["resumo"]),
            "primary_location": {"source": {"display_name": r["fonte"], "issn_l": r["issn"]}},
            "authorships": [
                {"author": {"display_name": autor},
                 "institutions": [{"display_name": "Instituto Sintetico", "country_code": "BR"}]}
                for autor in r["autores"]
            ],
            "keywords": [{"display_name": p} for p in r["palavras"]],
            "referenced_works": ["https://openalex.org/W90000%04d" % j
                                 for j in range(max(0, i - 12), i)],
        })
    with open(caminho, "w", encoding="utf-8") as fh:
        json.dump({"meta": {"count": len(obras), "next_cursor": None}, "results": obras}, fh,
                  ensure_ascii=False)


def escrever_ris(registros, caminho):
    with open(caminho, "w", encoding="utf-8") as fh:
        for r in registros:
            fh.write("TY  - JOUR\n")
            for autor in r["autores"]:
                fh.write("AU  - %s\n" % autor)
            fh.write("TI  - %s\n" % r["titulo"])
            fh.write("PY  - %d\n" % r["ano"])
            fh.write("JO  - %s\n" % r["fonte"])
            fh.write("DO  - %s\n" % r["doi"])
            fh.write("AB  - %s\n" % r["resumo"])
            for p in r["palavras"]:
                fh.write("KW  - %s\n" % p)
            fh.write("AD  - %s\n" % r["afiliacoes"])
            fh.write("LA  - pt\n")
            fh.write("ER  - \n\n")


def main(destino=None):
    global DESTINO
    if destino:
        DESTINO = os.path.abspath(os.path.expanduser(destino))
    os.makedirs(DESTINO, exist_ok=True)
    registros = gerar()
    # sobreposição deliberada entre bases, para exercitar a deduplicação
    escrever_scopus(registros[:90], os.path.join(DESTINO, "scopus_exemplo.csv"))
    escrever_wos(registros[60:110], os.path.join(DESTINO, "wos_exemplo.txt"))
    escrever_ris(registros[100:], os.path.join(DESTINO, "scielo_exemplo.ris"))
    escrever_openalex(registros[110:], os.path.join(DESTINO, "openalex_exemplo.json"))
    with open(os.path.join(DESTINO, "LEIA-ME.md"), "w", encoding="utf-8") as fh:
        fh.write(
            "# Amostra sintética\n\n"
            "**Estes arquivos NÃO contêm registros bibliográficos reais.** São gerados por\n"
            "`testes/gerar_exemplo.py` com semente fixa, apenas para exercitar o pipeline sem\n"
            "depender de bases proprietárias, e podem ser refeitos a qualquer momento.\n\n"
            "Sobreposição proposital entre os arquivos (registros 60-89 em Scopus e WoS; 100-109\n"
            "em WoS e SciELO) para que a deduplicação tenha o que remover.\n"
        )
    print("Amostra sintética gerada em %s" % os.path.relpath(DESTINO, RAIZ))


if __name__ == "__main__":
    import sys

    main(sys.argv[1] if len(sys.argv) > 1 else None)
