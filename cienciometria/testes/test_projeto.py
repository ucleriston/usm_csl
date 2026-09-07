"""Testes do estado do projeto, do fichamento e do rascunho do artigo."""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from cienciometria import artigo, estado, fichamento  # noqa: E402
from cienciometria.corpus_io import salvar_corpus  # noqa: E402
from cienciometria.modelo import registro_vazio  # noqa: E402
from cienciometria.revisao import Revisao  # noqa: E402


def _registro(id_, titulo, ano=2015, citacoes=10, **kw):
    return registro_vazio(id=id_, titulo=titulo, ano=ano, citacoes=citacoes,
                          autores=kw.pop("autores", ["Alfa, A."]), **kw)


class BaseRevisao(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.revisao = Revisao.criar("teste", titulo="Revisão de teste", base=self.dir)

    def _corpus(self, registros):
        salvar_corpus(self.revisao.corpus, registros)


class TestEstado(BaseRevisao):
    def test_projeto_novo_para_na_primeira_etapa(self):
        dados = estado.resumo(self.revisao)
        self.assertEqual(dados["etapa_atual"]["id"], "E1")
        self.assertFalse(dados["concluida"])
        self.assertEqual(len(dados["etapas"]), 8)

    def test_etapa_do_corpus_reconhece_registros(self):
        self._corpus([_registro("a:1", "Um artigo")])
        with open(os.path.join(self.revisao.dir_processado, "dedup.json"), "w") as fh:
            json.dump({"saida": 1}, fh)
        etapas = {e["id"]: e for e in estado.avaliar(self.revisao)}
        self.assertTrue(etapas["E4"]["feito"])
        self.assertIn("1 registros", etapas["E4"]["detalhe"])

    def test_documento_com_marcadores_do_modelo_nao_conta_como_preenchido(self):
        caminho = os.path.join(self.revisao.dir, "docs", "01-projeto-de-pesquisa.md")
        with open(caminho, "w", encoding="utf-8") as fh:
            fh.write("texto longo " * 200 + "«substitua isto»")
        etapas = {e["id"]: e for e in estado.avaliar(self.revisao)}
        self.assertFalse(etapas["E1"]["feito"])

    def test_cada_etapa_aponta_uma_skill_e_um_proximo_passo(self):
        for etapa in estado.avaliar(self.revisao):
            self.assertTrue(etapa["skill"], etapa["id"])
            self.assertTrue(etapa["proximo"], etapa["id"])

    def test_formatacao_indica_a_etapa_atual(self):
        texto = estado.formatar(estado.resumo(self.revisao))
        self.assertIn("Etapa atual: E1", texto)
        self.assertIn("Próximo passo:", texto)


class TestFichamento(BaseRevisao):
    def test_ficha_nasce_com_o_que_o_corpus_sabe(self):
        registro = _registro("a:1", "Um artigo sobre finanças", fonte="Revista X",
                             doi="10.1/x", palavras_chave=["fiscal federalism"])
        caminho, nova = fichamento.criar_ficha(self.revisao, registro)
        self.assertTrue(nova)
        ficha = fichamento.ler_ficha(caminho)
        self.assertEqual(ficha["campos"]["titulo"], "Um artigo sobre finanças")
        self.assertIn("10.1/x", ficha["campos"]["referencia"])
        self.assertIn("fiscal federalism", ficha["campos"]["palavras_chave"])
        self.assertEqual(ficha["meta"]["id_corpus"], "a:1")

    def test_ficha_recem_criada_esta_incompleta(self):
        caminho, _ = fichamento.criar_ficha(self.revisao, _registro("a:1", "Artigo"))
        ficha = fichamento.ler_ficha(caminho)
        self.assertFalse(ficha["completa"])
        self.assertIn("Objetivos deste artigo", ficha["faltando"])

    def test_nao_sobrescreve_ficha_existente(self):
        registro = _registro("a:1", "Artigo")
        caminho, _ = fichamento.criar_ficha(self.revisao, registro)
        with open(caminho, "a", encoding="utf-8") as fh:
            fh.write("\nanotação do pesquisador\n")
        caminho2, nova = fichamento.criar_ficha(self.revisao, registro)
        self.assertFalse(nova)
        self.assertIn("anotação do pesquisador", open(caminho2, encoding="utf-8").read())

    def test_ficha_preenchida_fica_completa(self):
        caminho, _ = fichamento.criar_ficha(self.revisao, _registro("a:1", "Artigo"))
        texto = open(caminho, encoding="utf-8").read()
        for rotulo in ("Objetivos deste artigo", "Método — Estratégia de pesquisa",
                       "Principais resultados (com suas palavras)",
                       "Lacunas apontadas pelos autores e sugestões para futuras pesquisas"):
            texto = texto.replace("## %s\n\n\n" % rotulo, "## %s\n\nconteúdo\n\n" % rotulo)
        open(caminho, "w", encoding="utf-8").write(texto)
        self.assertTrue(fichamento.ler_ficha(caminho)["completa"])

    def test_sugestao_cobre_mais_citados_e_recentes(self):
        corpus = [_registro("a:%d" % i, "Artigo %d" % i, ano=1995 + i, citacoes=100 - i)
                  for i in range(20)]
        sugestoes = fichamento.sugerir_leitura(corpus, {}, quantidade=6)
        motivos = {s["motivo"] for s in sugestoes}
        self.assertIn("mais citado do corpus", motivos)
        self.assertIn("recente e já citado", motivos)
        self.assertEqual(len({s["id"] for s in sugestoes}), len(sugestoes))

    def test_sugestao_inclui_representante_de_agrupamento(self):
        corpus = [_registro("a:%d" % i, "Artigo %d" % i, citacoes=50 - i,
                            palavras_chave=["tema raro"] if i == 19 else ["tema comum"])
                  for i in range(20)]
        resultados = {"copalavras": {"mapa": [
            {"agrupamento": 1, "termos_representativos": "tema raro; outro"}]}}
        sugestoes = fichamento.sugerir_leitura(corpus, resultados, quantidade=4)
        self.assertTrue(any("agrupamento" in s["motivo"] for s in sugestoes))

    def test_matriz_confronta_lacuna_declarada_com_o_corpus(self):
        caminho, _ = fichamento.criar_ficha(self.revisao, _registro("a:1", "Artigo"))
        texto = open(caminho, encoding="utf-8").read()
        texto = texto.replace(
            "## Lacunas apontadas pelos autores e sugestões para futuras pesquisas\n\n\n",
            "## Lacunas apontadas pelos autores e sugestões para futuras pesquisas\n\n"
            "Falta estudo sobre capacidade estatal.\n\n")
        texto = texto.replace("## Termos da lacuna (2 a 4, para conferir no corpus)\n\n\n",
                              "## Termos da lacuna (2 a 4, para conferir no corpus)\n\n"
                              "capacidade estatal\n\n")
        open(caminho, "w", encoding="utf-8").write(texto)
        corpus = [_registro("c:%d" % i, "Estudo de capacidade estatal %d" % i) for i in range(4)]
        corpus += [_registro("d:%d" % i, "Outro assunto %d" % i) for i in range(6)]
        linhas = fichamento.matriz_de_lacunas(self.revisao, corpus)
        self.assertEqual(len(linhas), 1)
        self.assertIn("capacidade estatal=4", linhas[0]["ocorrencias_no_corpus"])
        self.assertEqual(linhas[0]["cobertura_%"], 40.0)


class TestArtigo(BaseRevisao):
    def _resultados(self):
        return {
            "n_corpus": 100, "semente": 42, "tcac": 7.5,
            "producao_anual": [{"ano": 2000, "publicacoes": 2}, {"ano": 2020, "publicacoes": 9}],
            "lotka": {"alpha": 2.1, "ks": 0.02, "ks_critico_5%": 0.09, "adere": True,
                      "n_autores": 150},
            "bradford": {"zonas": [{"zona": 1, "fontes": 3, "artigos_%": 33.0}],
                         "multiplicador": 2.1, "tabela": [{"zona": 1, "fonte": "Revista X",
                                                           "artigos": 10, "acumulado": 10}]},
            "impacto": {"citacoes_totais": 900, "media_por_trabalho": 9.0, "h_index": 15,
                        "sem_citacao_%": 12.0, "mais_citados": []},
            "colaboracao": {"autores_por_trabalho": 2.4, "indice_colaboracao": 3.0,
                            "trabalhos_com_um_autor_%": 20.0, "coautoria_internacional_%": 35.0,
                            "por_pais": []},
            "price": {"indice_price_corpus": 30.0, "meia_vida_citada": 9, "cobertura_%": 80.0},
            "copalavras": {"metricas": {"nos": 50, "arestas": 200, "densidade": 0.16},
                           "agrupamentos": 4, "mapa": []},
            "coautoria": {"metricas": {"nos": 120, "componentes": 9, "componente_gigante_%": 40.0}},
            "cocitacao": {"cobertura_%": 78.0, "top": []},
        }

    def test_numeros_da_analise_entram_no_rascunho(self):
        texto = artigo.montar(self.revisao, self._resultados())
        for esperado in ("100", "7.5", "2.1", "15", "78.0"):
            self.assertIn(esperado, texto)

    def test_secoes_do_artigo_presentes(self):
        texto = artigo.montar(self.revisao, self._resultados())
        for secao in ("## Resumo", "## 1 Introdução", "## 2 Material e Métodos",
                      "### 3.1", "### 3.4", "## 4 Discussão", "## 5 Conclusão",
                      "## Referências"):
            self.assertIn(secao, texto)

    def test_marca_o_que_exige_escrita_humana(self):
        texto = artigo.montar(self.revisao, self._resultados())
        contagem = artigo.pendencias(texto)
        self.assertGreater(contagem["escrever"], 5)

    def test_dado_ausente_vira_marcacao_e_nunca_numero(self):
        texto = artigo.montar(self.revisao, {"n_corpus": 10})
        self.assertIn("[SEM DADO", texto)
        self.assertGreater(artigo.pendencias(texto)["sem_dado"], 0)

    def test_expoente_negativo_nao_e_apresentado_como_lotka(self):
        resultados = self._resultados()
        resultados["lotka"] = {"alpha": -0.3, "ks": 0.1, "ks_critico_5%": 0.2, "adere": True,
                               "n_autores": 50}
        texto = artigo.montar(self.revisao, resultados)
        self.assertIn("não é positivo", texto)
        self.assertNotIn("o que sustenta a Lei de Lotka", texto)

    def test_sem_fichamento_a_introducao_avisa(self):
        texto = artigo.montar(self.revisao, self._resultados(), lacunas=[])
        self.assertIn("nenhuma lacuna consolidada", texto)

    def test_lacunas_entram_com_a_conferencia_no_corpus(self):
        lacunas = [{"ficha": "f.md", "ano": "2010", "lacuna_declarada": "falta X",
                    "ocorrencias_no_corpus": "x=3"}]
        texto = artigo.montar(self.revisao, self._resultados(), lacunas=lacunas)
        self.assertIn("falta X", texto)
        self.assertIn("x=3", texto)


if __name__ == "__main__":
    unittest.main()
