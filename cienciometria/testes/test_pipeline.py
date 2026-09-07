"""Testes do pipeline. Executar da raiz do projeto:

    PYTHONPATH=src python -m unittest discover -s testes -v
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from cienciometria import indicadores, parsers, redes, triagem  # noqa: E402
from cienciometria.corpus_io import carregar_corpus, salvar_corpus  # noqa: E402
from cienciometria.dedup import deduplicar, similaridade  # noqa: E402
from cienciometria.modelo import desserializar, registro_vazio, serializar  # noqa: E402
from cienciometria.normalizacao import (  # noqa: E402
    chave_texto, extrair_paises, normalizar_autor, normalizar_doi, normalizar_registro,
)

TESAUROS_VAZIOS = {"termos": {}, "fontes": {}, "instituicoes": {}, "paises": {"brazil": "BRA"}}


class TestNormalizacao(unittest.TestCase):
    def test_nomes_em_formatos_diferentes_convergem(self):
        for variante in ("Oates, W. E.", "William E. Oates", "OATES W.E.", "Oates W E"):
            self.assertEqual(normalizar_autor(variante), "Oates, W. E.")

    def test_particula_integra_o_sobrenome(self):
        self.assertEqual(normalizar_autor("van Eck, N.J."), "van Eck, N. J.")
        self.assertEqual(normalizar_autor("de Mello L."), "de Mello, L.")

    def test_hifen_preservado(self):
        self.assertEqual(normalizar_autor("Ter-Minassian, Teresa"), "Ter-Minassian, T.")

    def test_doi_normalizado(self):
        for variante in ("https://doi.org/10.1234/ABC", "doi: 10.1234/abc", "10.1234/abc "):
            self.assertEqual(normalizar_doi(variante), "10.1234/abc")

    def test_chave_texto_remove_acento_e_pontuacao(self):
        self.assertEqual(chave_texto("Federalismo Fiscal: autonomia?"), "federalismo fiscal autonomia")

    def test_pais_extraido_da_afiliacao(self):
        self.assertEqual(extrair_paises("Univ Federal, Recife, Brazil", {"brazil": "BRA"}), ["BRA"])

    def test_pais_nao_casa_dentro_de_outra_palavra(self):
        self.assertEqual(extrair_paises("Brazilwood Institute", {"brazil": "BRA"}), [])

    def test_colaboracao_internacional_marcada(self):
        reg = registro_vazio(titulo="X", paises=["BRA", "USA"])
        normalizar_registro(reg, TESAUROS_VAZIOS)
        self.assertEqual(reg["colab_internacional"], 1)


class TestSerializacao(unittest.TestCase):
    def test_ida_e_volta_preserva_listas(self):
        reg = registro_vazio(id="x:1", titulo="T", autores=["Alfa, A.", "Beta, B."], ano=2020)
        volta = desserializar(serializar(reg))
        self.assertEqual(volta["autores"], ["Alfa, A.", "Beta, B."])
        self.assertEqual(volta["ano"], 2020)


class TestParsers(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def _escrever(self, nome, conteudo):
        caminho = os.path.join(self.dir, nome)
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write(conteudo)
        return caminho

    def test_scopus_csv(self):
        caminho = self._escrever(
            "scopus_x.csv",
            "Authors,Title,Year,Source title,Cited by,DOI,Author Keywords,References\n"
            '"Alfa A.; Beta B.","Fiscal federalism",2015,"National Tax Journal",12,'
            '10.1/a,"fiscal federalism; local government","REF A, 2001; REF B, 1999"\n',
        )
        registros = parsers.ler_arquivo(caminho)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["ano"], 2015)
        self.assertEqual(registros[0]["citacoes"], 12)
        self.assertEqual(len(registros[0]["autores"]), 2)
        self.assertEqual(len(registros[0]["referencias"]), 2)
        self.assertEqual(registros[0]["base_origem"], "scopus")

    def test_wos_txt_com_campos_multilinha(self):
        caminho = self._escrever(
            "wos_x.txt",
            "PT J\nAU Alfa A\n   Beta B\nTI Transferencias\n   intergovernamentais\n"
            "SO Nova Economia\nDE fiscal federalism; revenue sharing\nTC 5\nPY 2019\n"
            "DI 10.2/b\nCR REF A, 2001\n   REF B, 1999\nER\n",
        )
        registros = parsers.ler_arquivo(caminho)
        self.assertEqual(len(registros), 1)
        reg = registros[0]
        self.assertEqual(reg["titulo"], "Transferencias intergovernamentais")
        self.assertEqual(reg["autores"], ["Alfa A", "Beta B"])
        self.assertEqual(len(reg["referencias"]), 2)
        self.assertEqual(reg["palavras_chave"], ["fiscal federalism", "revenue sharing"])

    def test_ris(self):
        caminho = self._escrever(
            "scielo_x.ris",
            "TY  - JOUR\nAU  - Alfa, A.\nAU  - Beta, B.\nTI  - Federalismo fiscal\n"
            "PY  - 2021\nJO  - Revista X\nDO  - 10.3/c\nKW  - federalismo fiscal\n"
            "KW  - municipio\nLA  - pt\nER  - \n",
        )
        registros = parsers.ler_arquivo(caminho)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["ano"], 2021)
        self.assertEqual(registros[0]["palavras_chave"], ["federalismo fiscal", "municipio"])

    def test_bibtex(self):
        caminho = self._escrever(
            "scielo_y.bib",
            "@article{k1,\n  author = {Alfa, A. and Beta, B.},\n"
            "  title = {Descentralizacao fiscal},\n  year = {2018},\n"
            "  journal = {Revista Y},\n  doi = {10.4/d},\n  keywords = {descentralizacao, municipio}\n}\n",
        )
        registros = parsers.ler_arquivo(caminho)
        self.assertEqual(len(registros), 1)
        self.assertEqual(registros[0]["ano"], 2018)
        self.assertEqual(len(registros[0]["autores"]), 2)

    def test_arquivo_de_extensao_desconhecida_e_ignorado(self):
        caminho = self._escrever("notas.md", "texto qualquer")
        self.assertEqual(parsers.ler_arquivo(caminho), [])


class TestDeduplicacao(unittest.TestCase):
    def _reg(self, **kw):
        reg = registro_vazio(**kw)
        reg["titulo_norm"] = chave_texto(reg["titulo"])
        reg["bases_todas"] = [reg["base_origem"]] if reg["base_origem"] else []
        return reg

    def test_doi_identico_funde(self):
        a = self._reg(id="a", doi="10.1/x", titulo="T A", base_origem="scopus", citacoes=10)
        b = self._reg(id="b", doi="10.1/x", titulo="T A", base_origem="wos", citacoes=15)
        corpus, _, est = deduplicar([a, b])
        self.assertEqual(len(corpus), 1)
        self.assertEqual(corpus[0]["citacoes"], 15)          # prevalece o maior
        self.assertEqual(corpus[0]["fonte_citacoes"], "wos")
        self.assertEqual(sorted(corpus[0]["bases_todas"]), ["scopus", "wos"])
        self.assertEqual(est["removidas_por_doi"], 1)

    def test_titulo_e_ano_sem_doi(self):
        a = self._reg(id="a", doi="10.1/x", titulo="Federalismo fiscal municipal",
                      ano=2010, base_origem="scopus")
        b = self._reg(id="b", titulo="Federalismo fiscal municipal!", ano=2010, base_origem="scielo")
        corpus, _, est = deduplicar([a, b])
        self.assertEqual(len(corpus), 1)
        self.assertEqual(est["removidas_por_titulo_ano"], 1)

    def test_titulos_diferentes_nao_fundem(self):
        a = self._reg(id="a", doi="10.1/x", titulo="Federalismo fiscal", ano=2010, base_origem="scopus")
        b = self._reg(id="b", titulo="Guerra fiscal entre estados", ano=2010, base_origem="scielo")
        corpus, _, _ = deduplicar([a, b])
        self.assertEqual(len(corpus), 2)

    def test_par_ambiguo_vai_para_revisao_humana(self):
        base = "descentralizacao fiscal e capacidade dos municipios brasileiros"
        a = self._reg(id="a", doi="10.1/x", titulo=base, ano=2015, base_origem="scopus")
        b = self._reg(id="b", titulo=base.replace("brasileiros", "argentinos"),
                      ano=2015, base_origem="scielo")
        self.assertGreaterEqual(similaridade(chave_texto(a["titulo"]), chave_texto(b["titulo"])), 0.88)
        corpus, revisao, _ = deduplicar([a, b])
        self.assertEqual(len(corpus), 2)
        self.assertEqual(len(revisao), 1)

    def test_referencias_mais_longas_prevalecem(self):
        a = self._reg(id="a", doi="10.1/x", titulo="T", base_origem="scopus", referencias=["r1"])
        b = self._reg(id="b", doi="10.1/x", titulo="T", base_origem="wos",
                      referencias=["r1", "r2", "r3"])
        corpus, _, _ = deduplicar([a, b])
        self.assertEqual(corpus[0]["n_referencias"], 3)


class TestIndicadores(unittest.TestCase):
    def test_lotka_recupera_expoente_conhecido(self):
        # distribuição construída com alpha = 2: 100 autores com 1 trabalho, 25 com 2, 11 com 3
        corpus, autor = [], 0
        for trabalhos, quantos in ((1, 100), (2, 25), (3, 11), (4, 6)):
            for _ in range(quantos):
                autor += 1
                for t in range(trabalhos):
                    corpus.append(registro_vazio(id="d%d_%d" % (autor, t),
                                                 autores=["Autor%d, A." % autor]))
        resultado = indicadores.lei_de_lotka(corpus)
        self.assertAlmostEqual(resultado["alpha"], 2.0, delta=0.25)
        self.assertTrue(resultado["adere"])

    def test_bradford_divide_em_tres_zonas(self):
        corpus = []
        for fonte, n in (("A", 30), ("B", 20), ("C", 10), ("D", 10), ("E", 5), ("F", 5)):
            corpus += [registro_vazio(id="%s%d" % (fonte, i), fonte=fonte) for i in range(n)]
        resultado = indicadores.lei_de_bradford(corpus)
        self.assertEqual(len(resultado["zonas"]), 3)
        self.assertEqual(sum(z["artigos"] for z in resultado["zonas"]), 80)
        self.assertEqual(resultado["tabela"][0]["fonte"], "A")

    def test_h_index(self):
        self.assertEqual(indicadores.h_index([10, 8, 5, 4, 3]), 4)
        self.assertEqual(indicadores.h_index([0, 0]), 0)

    def test_indice_de_price(self):
        corpus = [registro_vazio(id="a", ano=2020, referencias=[
            "AUTOR A, 2018, REV", "AUTOR B, 2017, REV", "AUTOR C, 2000, REV", "AUTOR D, 1990, REV"])]
        resultado = indicadores.indice_de_price(corpus)
        self.assertEqual(resultado["indice_price_corpus"], 50.0)
        self.assertEqual(resultado["referencias_datadas"], 4)

    def test_producao_anual_preenche_anos_vazios(self):
        corpus = [registro_vazio(id="a", ano=2000), registro_vazio(id="b", ano=2003)]
        serie = indicadores.producao_anual(corpus, 2003)
        self.assertEqual([l["ano"] for l in serie], [2000, 2001, 2002, 2003])
        self.assertEqual(serie[1]["publicacoes"], 0)

    def test_colaboracao_scp_mcp(self):
        corpus = [
            registro_vazio(id="a", paises=["BRA"], n_autores=2, colab_internacional=0),
            registro_vazio(id="b", paises=["BRA", "USA"], n_autores=3, colab_internacional=1),
        ]
        resultado = indicadores.colaboracao(corpus)
        self.assertEqual(resultado["scp"], 1)
        self.assertEqual(resultado["mcp"], 1)
        self.assertEqual(resultado["coautoria_internacional_%"], 50.0)


class TestRedes(unittest.TestCase):
    def test_coocorrencia_conta_pares(self):
        nos, arestas = redes.rede_coocorrencia([["a", "b"], ["a", "b"], ["a", "c"]], minimo=1)
        self.assertEqual(nos["a"], 3)
        self.assertEqual(arestas[("a", "b")], 2)

    def test_item_repetido_no_mesmo_documento_conta_uma_vez(self):
        nos, _ = redes.rede_coocorrencia([["a", "a", "b"]], minimo=1)
        self.assertEqual(nos["a"], 1)

    def test_agrupamento_e_deterministico(self):
        listas = [["a", "b"], ["a", "b"], ["c", "d"], ["c", "d"]]
        nos, arestas = redes.rede_coocorrencia(listas, minimo=1)
        g1 = redes.propagacao_de_rotulos(nos, arestas, semente=42)
        g2 = redes.propagacao_de_rotulos(nos, arestas, semente=42)
        self.assertEqual(g1, g2)
        self.assertEqual(g1["a"], g1["b"])
        self.assertNotEqual(g1["a"], g1["c"])

    def test_chave_de_referencia_usa_doi_quando_existe(self):
        self.assertEqual(redes._chave_referencia("Autor, 2001, DOI 10.1234/abc"), "10.1234/abc")
        self.assertEqual(redes._chave_referencia("OATES W, 1972, FISCAL FEDERALISM"), "OATES W (1972)")

    def test_metricas_detectam_componentes(self):
        nos, arestas = redes.rede_coocorrencia([["a", "b"], ["c", "d"]], minimo=1)
        m = redes.metricas_da_rede(nos, arestas)
        self.assertEqual(m["componentes"], 2)
        self.assertEqual(m["componente_gigante"], 2)

    def test_exportacao_pajek(self):
        nos, arestas = redes.rede_coocorrencia([["a", "b"]], minimo=1)
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "r.net")
            redes.exportar_pajek(caminho, nos, arestas)
            with open(caminho, encoding="utf-8") as fh:
                conteudo = fh.read()
        self.assertIn("*Vertices 2", conteudo)
        self.assertIn("*Edges", conteudo)

    def test_mapa_tematico_calcula_quadrantes(self):
        listas = [["a", "b"], ["a", "b"], ["c", "d"], ["c", "d"], ["b", "c"]]
        nos, arestas = redes.rede_coocorrencia(listas, minimo=1)
        grupos = redes.propagacao_de_rotulos(nos, arestas, semente=1)
        mapa = redes.mapa_tematico(nos, arestas, grupos)
        self.assertTrue(all("quadrante" in l for l in mapa))


class TestTriagem(unittest.TestCase):
    def test_kappa_concordancia_total(self):
        pares = [("incluido", "incluido")] * 8 + [("excluido", "excluido")] * 2
        self.assertEqual(triagem.kappa_de_cohen(pares)["kappa"], 1.0)

    def test_kappa_penaliza_divergencia(self):
        pares = [("incluido", "excluido")] * 5 + [("incluido", "incluido")] * 5
        resultado = triagem.kappa_de_cohen(pares)
        self.assertLess(resultado["kappa"], 0.75)
        self.assertFalse(resultado["atinge_meta_0.75"])

    def test_decisao_invalida_e_sinalizada(self):
        linhas = [{"id": "a", "decisao_r1": "talvez", "decisao_r2": "incluido"}]
        self.assertEqual(triagem.concordancia(linhas)["decisoes_invalidas"], ["a"])

    def test_contagens_prisma(self):
        brutos = [registro_vazio(id="a", base_origem="scopus"),
                  registro_vazio(id="b", base_origem="wos")]
        linhas = [
            {"id": "a", "decisao_final": "incluido", "codigo_exclusao_final": ""},
            {"id": "b", "decisao_final": "excluido", "codigo_exclusao_final": "E2"},
        ]
        fluxo = triagem.contagens_prisma(brutos, {"removidas_total": 0, "saida": 2}, linhas)
        self.assertEqual(fluxo["incluidos"], 1)
        self.assertEqual(fluxo["exclusoes_por_codigo"]["E2"]["n"], 1)
        self.assertIn("IDENTIFICAÇÃO", triagem.diagrama_prisma(fluxo))


class TestCorpusIO(unittest.TestCase):
    def test_salvar_e_carregar(self):
        reg = registro_vazio(id="a", titulo="T", autores=["Alfa, A."], ano=2020,
                             palavras_chave=["fiscal federalism"])
        with tempfile.TemporaryDirectory() as d:
            caminho = os.path.join(d, "corpus.csv")
            salvar_corpus(caminho, [reg])
            volta = carregar_corpus(caminho)
        self.assertEqual(len(volta), 1)
        self.assertEqual(volta[0]["autores"], ["Alfa, A."])
        self.assertEqual(volta[0]["palavras_chave"], ["fiscal federalism"])


if __name__ == "__main__":
    unittest.main()


class TestRevisao(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()

    def test_criar_revisao_a_partir_do_modelo(self):
        from cienciometria.revisao import Revisao

        revisao = Revisao.criar("tema-x", titulo="Tema X", tema="Assunto X", base=self.dir)
        self.assertTrue(revisao.existe())
        self.assertEqual(revisao.config["titulo"], "Tema X")
        self.assertTrue(os.path.exists(os.path.join(revisao.dir, "config", "revisao.json")))
        self.assertTrue(os.path.isdir(revisao.dir_bruto))
        with open(os.path.join(revisao.dir, "docs", "01-projeto-de-pesquisa.md"), encoding="utf-8") as fh:
            projeto = fh.read()
        self.assertIn("Tema X", projeto)
        self.assertNotIn("{{TITULO}}", projeto)

    def test_nao_sobrescreve_revisao_existente(self):
        from cienciometria.revisao import Revisao

        Revisao.criar("tema-y", base=self.dir)
        with self.assertRaises(FileExistsError):
            Revisao.criar("tema-y", base=self.dir)

    def test_configuracao_padrao_preenche_o_que_falta(self):
        from cienciometria.revisao import Revisao

        revisao = Revisao.criar("tema-z", base=self.dir)
        self.assertEqual(revisao.limiar("min_termo"), 5)
        self.assertEqual(len(revisao.periodos()), 4)
        self.assertIn("scopus", revisao.config["precedencia_bases"])

    def test_ano_de_corte_cai_para_a_janela_quando_nao_declarado(self):
        from cienciometria.revisao import Revisao

        revisao = Revisao.criar("tema-w", base=self.dir)
        caminho = os.path.join(revisao.dir_config, "revisao.json")
        import json as _json
        config = _json.load(open(caminho, encoding="utf-8"))
        config["janela"] = {"inicio": 2000, "fim": 2024}
        _json.dump(config, open(caminho, "w", encoding="utf-8"))
        self.assertEqual(Revisao("tema-w", base=self.dir).ano_corte(), 2024)


class TestProposicoes(unittest.TestCase):
    def setUp(self):
        from cienciometria import proposicoes

        self.mod = proposicoes
        self.resultados = {
            "lotka": {"alpha": 2.05, "adere": True},
            "bradford": {"zonas": [{"artigos_%": 33.0}]},
            "coautoria": {"metricas": {"componente_gigante_%": 41.0}},
        }

    def test_caminho_com_indice_de_lista(self):
        self.assertEqual(self.mod.valor_em(self.resultados, "bradford.zonas.0.artigos_%"), 33.0)
        self.assertIsNone(self.mod.valor_em(self.resultados, "bradford.zonas.9.artigos_%"))

    def test_conjuncao_sustentada(self):
        p = {"id": "P1", "enunciado": "e", "criterio": {"tipo": "todos", "condicoes": [
            {"campo": "lotka.alpha", "operador": "entre", "valor": [1.7, 2.3]},
            {"campo": "lotka.adere", "operador": "==", "valor": True}]}}
        self.assertEqual(self.mod.avaliar_uma(p, self.resultados)["situacao"], "sustentada")

    def test_conjuncao_refutada_por_uma_condicao(self):
        p = {"id": "P1", "enunciado": "e", "criterio": {"tipo": "todos", "condicoes": [
            {"campo": "lotka.alpha", "operador": "entre", "valor": [1.7, 2.3]},
            {"campo": "coautoria.metricas.componente_gigante_%", "operador": ">", "valor": 60}]}}
        self.assertEqual(self.mod.avaliar_uma(p, self.resultados)["situacao"], "refutada")

    def test_disjuncao(self):
        p = {"id": "P4", "enunciado": "e", "criterio": {"tipo": "algum", "condicoes": [
            {"campo": "coautoria.metricas.componente_gigante_%", "operador": "<=", "valor": 60},
            {"campo": "lotka.alpha", "operador": ">", "valor": 99}]}}
        self.assertEqual(self.mod.avaliar_uma(p, self.resultados)["situacao"], "sustentada")

    def test_campo_ausente_nao_vira_veredicto(self):
        p = {"id": "P9", "enunciado": "e", "criterio": {"campo": "nao.existe", "operador": ">=", "valor": 1}}
        self.assertEqual(self.mod.avaliar_uma(p, self.resultados)["situacao"], "não avaliável")

    def test_proposicao_manual_fica_pendente(self):
        p = {"id": "P3", "enunciado": "e", "criterio": {"tipo": "manual", "observacao": "codificar"}}
        self.assertEqual(self.mod.avaliar_uma(p, self.resultados)["situacao"], "exige etapa manual")

    def test_sem_proposicoes_declaradas(self):
        linhas = self.mod.avaliar([], self.resultados)
        self.assertEqual(linhas[0]["situacao"], "não avaliável")
