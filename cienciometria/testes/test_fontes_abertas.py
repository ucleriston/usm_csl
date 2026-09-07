"""Testes dos parsers de fontes abertas (OpenAlex e Crossref).

As fixtures reproduzem o formato documentado das duas APIs. Elas verificam o
mapeamento para o modelo do corpus; a chamada de rede em si é exercitada
separadamente, com um transporte falso, porque teste que depende de internet
não é teste, é aposta.
"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from cienciometria import coleta, parsers, redes  # noqa: E402
from cienciometria.normalizacao import converter_paises, normalizar_registro  # noqa: E402

OPENALEX = {
    "meta": {"count": 2, "next_cursor": None},
    "results": [
        {
            "id": "https://openalex.org/W2000000001",
            "doi": "https://doi.org/10.1234/abc",
            "title": "Fiscal federalism and local revenue",
            "publication_year": 2015,
            "cited_by_count": 42,
            "type": "article",
            "language": "en",
            "abstract_inverted_index": {"This": [0], "paper": [1], "studies": [2], "transfers": [3]},
            "open_access": {"is_oa": True},
            "primary_location": {"source": {
                "display_name": "National Tax Journal", "issn_l": "0028-0283",
                "host_organization_name": "University of Chicago Press"}},
            "authorships": [
                {"author": {"display_name": "Wallace E. Oates",
                            "orcid": "https://orcid.org/0000-0002-1825-0097"},
                 "institutions": [{"display_name": "University of Maryland", "country_code": "US"}]},
                {"author": {"display_name": "Marta Arretche"},
                 "institutions": [{"display_name": "Universidade de São Paulo", "country_code": "BR"}]},
            ],
            "keywords": [{"display_name": "fiscal federalism"}],
            "concepts": [{"display_name": "public finance"}, {"display_name": "fiscal federalism"}],
            "referenced_works": ["https://openalex.org/W1111", "https://openalex.org/W2222"],
        },
        {
            "id": "https://openalex.org/W1111",
            "title": "An earlier work",
            "publication_year": 1999,
            "authorships": [{"author": {"display_name": "Ana Silva"}, "institutions": []}],
            "referenced_works": [],
        },
    ],
}

CROSSREF = {
    "message": {
        "total-results": 1,
        "next-cursor": None,
        "items": [{
            "DOI": "10.5555/XYZ",
            "title": ["Intergovernmental transfers in practice"],
            "container-title": ["Revista de Administração Pública"],
            "issued": {"date-parts": [[2020, 3, 1]]},
            "is-referenced-by-count": 7,
            "type": "journal-article",
            "language": "pt",
            "publisher": "FGV",
            "volume": "54", "issue": "2", "page": "101-120",
            "abstract": "<jats:p>Resumo do artigo.</jats:p>",
            "subject": ["Public Administration"],
            "URL": "https://doi.org/10.5555/xyz",
            "author": [
                {"given": "João", "family": "Souza",
                 "affiliation": [{"name": "Universidade de Brasília"}]},
                {"given": "Ana", "family": "Lima", "affiliation": []},
            ],
            "reference": [
                {"DOI": "10.1234/ABC"},
                {"unstructured": "OATES, W. Fiscal federalism. 1972."},
                {"author": "Tiebout", "year": "1956", "journal-title": "JPE"},
            ],
        }],
    }
}


class TestOpenAlex(unittest.TestCase):
    def setUp(self):
        self.registros = parsers.ler_openalex_json(OPENALEX)

    def test_le_todos_os_registros(self):
        self.assertEqual(len(self.registros), 2)

    def test_campos_principais(self):
        r = self.registros[0]
        self.assertEqual(r["doi"], "10.1234/abc")
        self.assertEqual(r["id_externo"], "openalex:W2000000001")
        self.assertEqual(r["ano"], 2015)
        self.assertEqual(r["citacoes"], 42)
        self.assertEqual(r["fonte"], "National Tax Journal")
        self.assertEqual(r["issn"], "0028-0283")

    def test_resumo_reconstruido_do_indice_invertido(self):
        self.assertEqual(self.registros[0]["resumo"], "This paper studies transfers")

    def test_autores_instituicoes_e_paises(self):
        r = self.registros[0]
        self.assertEqual(r["autores"], ["Wallace E. Oates", "Marta Arretche"])
        self.assertEqual(r["orcid"], ["0000-0002-1825-0097"])
        self.assertIn("University of Maryland", r["instituicoes"])
        self.assertEqual(r["paises"], ["US", "BR"])

    def test_palavras_sem_repeticao_entre_keywords_e_concepts(self):
        self.assertEqual(self.registros[0]["palavras_chave"],
                         ["fiscal federalism", "public finance"])

    def test_referencias_viram_identificadores_estaveis(self):
        self.assertEqual(self.registros[0]["referencias"], ["openalex:W1111", "openalex:W2222"])

    def test_pais_convertido_para_iso3_na_normalizacao(self):
        tesauros = {"termos": {}, "fontes": {}, "instituicoes": {}, "paises": {},
                    "iso2": {"us": "USA", "br": "BRA"}}
        r = normalizar_registro(dict(self.registros[0]), tesauros)
        self.assertEqual(r["paises"], ["USA", "BRA"])
        self.assertEqual(r["colab_internacional"], 1)

    def test_codigo_desconhecido_passa_adiante(self):
        self.assertEqual(converter_paises(["ZZ"], {"br": "BRA"}), ["ZZ"])


class TestCrossref(unittest.TestCase):
    def setUp(self):
        self.registro = parsers.ler_crossref_json(CROSSREF)[0]

    def test_campos_principais(self):
        self.assertEqual(self.registro["doi"], "10.5555/xyz")
        self.assertEqual(self.registro["ano"], 2020)
        self.assertEqual(self.registro["fonte"], "Revista de Administração Pública")
        self.assertEqual(self.registro["citacoes"], 7)

    def test_autores_no_formato_sobrenome_nome(self):
        self.assertEqual(self.registro["autores"], ["Souza, João", "Lima, Ana"])

    def test_resumo_sem_marcacao_jats(self):
        self.assertEqual(self.registro["resumo"], "Resumo do artigo.")

    def test_referencias_com_doi_estruturado_e_nao_estruturado(self):
        refs = self.registro["referencias"]
        self.assertEqual(refs[0], "doi:10.1234/abc")
        self.assertIn("OATES", refs[1])
        self.assertIn("Tiebout", refs[2])


class TestDeteccaoDeFormato(unittest.TestCase):
    def _arquivo(self, dados, nome):
        caminho = os.path.join(self.dir, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(dados, fh)
        return caminho

    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def test_detecta_openalex_e_crossref_pelo_conteudo(self):
        self.assertEqual(len(parsers.ler_arquivo(self._arquivo(OPENALEX, "openalex_p1.json"))), 2)
        self.assertEqual(len(parsers.ler_arquivo(self._arquivo(CROSSREF, "crossref_p1.json"))), 1)

    def test_json_desconhecido_nao_quebra(self):
        self.assertEqual(parsers.ler_arquivo(self._arquivo({"outra": "coisa"}, "x.json")), [])

    def test_diretorio_mistura_json_com_exportacoes(self):
        self._arquivo(OPENALEX, "openalex_p1.json")
        registros, relatorio = parsers.ler_diretorio(self.dir)
        self.assertEqual(len(registros), 2)
        self.assertTrue(all(r["base_origem"] == "openalex" for r in registros))


class TestChavesDeReferencia(unittest.TestCase):
    def test_identificador_vira_chave_direta(self):
        self.assertEqual(redes._chave_referencia("openalex:W1111"), "openalex:W1111")
        self.assertEqual(redes._chave_referencia("doi:10.1/x"), "doi:10.1/x")

    def test_rotulo_legivel_quando_o_citado_esta_no_corpus(self):
        corpus = parsers.ler_openalex_json(OPENALEX)
        rotulos = redes.rotulos_do_corpus(corpus)
        self.assertEqual(redes._chave_referencia("openalex:W1111", rotulos), "Ana Silva (1999)")

    def test_cocitacao_usa_identificadores(self):
        corpus = parsers.ler_openalex_json(OPENALEX)
        nos, arestas, cobertura = redes.rede_cocitacao(corpus, minimo=1)
        self.assertIn("openalex:W2222", nos)
        self.assertEqual(cobertura["documentos_com_referencias"], 1)


class TestChamadaDeRede(unittest.TestCase):
    """Exercita paginação, corte por limite e tratamento de erro sem tocar a rede."""

    def setUp(self):
        self.original = coleta._pedir
        self.chamadas = []

    def tearDown(self):
        coleta._pedir = self.original

    def test_paginacao_por_cursor_e_gravacao_das_paginas(self):
        paginas = [
            {"meta": {"count": 3, "next_cursor": "c2"}, "results": [{"id": "W1"}, {"id": "W2"}]},
            {"meta": {"count": 3, "next_cursor": None}, "results": [{"id": "W3"}]},
        ]

        def falso(url, email, tentativas=4):
            self.chamadas.append(url)
            return paginas[len(self.chamadas) - 1]

        coleta._pedir = falso
        coleta.PAUSA = 0
        with tempfile.TemporaryDirectory() as destino:
            resultado = coleta.coletar_openalex("tema", destino, de=1990, ate=2020)
            arquivos = sorted(os.listdir(destino))
        self.assertEqual(resultado["registros"], 3)
        self.assertEqual(len(arquivos), 2)
        self.assertIn("cursor=%2A", self.chamadas[0])
        self.assertIn("cursor=c2", self.chamadas[1])
        self.assertIn("from_publication_date%3A1990", self.chamadas[0])

    def test_limite_interrompe_a_coleta(self):
        def falso(url, email, tentativas=4):
            return {"meta": {"next_cursor": "sempre"}, "results": [{"id": "W%d" % i} for i in range(50)]}

        coleta._pedir = falso
        coleta.PAUSA = 0
        with tempfile.TemporaryDirectory() as destino:
            resultado = coleta.coletar_openalex("tema", destino, limite=50)
        self.assertEqual(resultado["registros"], 50)

    def test_bloqueio_de_rede_vira_erro_explicito(self):
        def falso(url, email, tentativas=4):
            raise coleta.ColetaBloqueada("host bloqueado")

        coleta._pedir = falso
        with tempfile.TemporaryDirectory() as destino:
            with self.assertRaises(coleta.ColetaBloqueada):
                coleta.coletar_openalex("tema", destino)


if __name__ == "__main__":
    unittest.main()
