"""Garante que o plugin publicado continua igual ao motor deste repositório.

O motor é a fonte de verdade; `plugins/cienciometria/` é uma cópia sincronizada.
Cópia que envelhece silenciosamente é pior que duplicação assumida — por isso o
teste falha assim que as duas divergem, apontando o comando que resolve.
"""

import json
import os
import subprocess
import sys
import unittest

RAIZ_MOTOR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAIZ_REPO = os.path.dirname(RAIZ_MOTOR)
PLUGIN = os.path.join(RAIZ_REPO, "plugins", "cienciometria")

sys.path.insert(0, os.path.join(RAIZ_MOTOR, "ferramentas"))


class TestSincronia(unittest.TestCase):
    def test_plugin_sincronizado_com_o_motor(self):
        import sincronizar_plugin

        diferencas = sincronizar_plugin.conferir()
        self.assertEqual(
            diferencas, [],
            "plugin dessincronizado; rode: python3 ferramentas/sincronizar_plugin.py",
        )


class TestEstrutura(unittest.TestCase):
    def test_manifesto_valido(self):
        with open(os.path.join(PLUGIN, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
            manifesto = json.load(fh)
        self.assertEqual(manifesto["name"], "cienciometria")
        for campo in ("description", "version", "author"):
            self.assertIn(campo, manifesto)

    def test_marketplace_aponta_para_o_plugin(self):
        with open(os.path.join(RAIZ_REPO, ".claude-plugin", "marketplace.json"), encoding="utf-8") as fh:
            mercado = json.load(fh)
        fontes = {p["name"]: p["source"] for p in mercado["plugins"]}
        self.assertIn("cienciometria", fontes)
        self.assertTrue(os.path.isdir(os.path.join(RAIZ_REPO, fontes["cienciometria"])))

    def test_skills_tem_frontmatter_completo(self):
        pasta = os.path.join(PLUGIN, "skills")
        skills = sorted(os.listdir(pasta))
        self.assertGreaterEqual(len(skills), 4)
        for skill in skills:
            caminho = os.path.join(pasta, skill, "SKILL.md")
            self.assertTrue(os.path.exists(caminho), "%s sem SKILL.md" % skill)
            with open(caminho, encoding="utf-8") as fh:
                texto = fh.read()
            self.assertTrue(texto.startswith("---\n"), "%s sem frontmatter" % skill)
            frontmatter = texto.split("---", 2)[1]
            self.assertIn("name: %s" % skill, frontmatter,
                          "o campo name de %s precisa bater com a pasta" % skill)
            self.assertIn("description:", frontmatter)
            # o instalador recusa descrição acima de 1024 caracteres
            descricao = frontmatter.split("description:", 1)[1]
            descricao = " ".join(l.strip() for l in descricao.splitlines()
                                 if not l.strip().startswith(("name:", "compatibility:")))
            self.assertLessEqual(
                len(descricao.replace(">-", "").strip()), 1024,
                "descrição de %s passa do limite de 1024 caracteres do instalador" % skill)

    def test_comandos_declaram_descricao(self):
        pasta = os.path.join(PLUGIN, "commands")
        for arquivo in sorted(os.listdir(pasta)):
            with open(os.path.join(pasta, arquivo), encoding="utf-8") as fh:
                texto = fh.read()
            self.assertTrue(texto.startswith("---\n"), "%s sem frontmatter" % arquivo)
            self.assertIn("description:", texto.split("---", 2)[1])

    def test_lancador_executavel(self):
        lancador = os.path.join(PLUGIN, "bin", "cienciometria")
        self.assertTrue(os.access(lancador, os.X_OK), "bin/cienciometria não é executável")


class TestMotorEmbarcado(unittest.TestCase):
    def test_plugin_roda_e_cria_revisao_fora_da_instalacao(self):
        import tempfile

        with tempfile.TemporaryDirectory() as pasta:
            resultado = subprocess.run(
                [os.path.join(PLUGIN, "bin", "cienciometria"), "nova", "tema-x",
                 "--titulo", "Tema X"],
                cwd=pasta, capture_output=True, text=True, timeout=60,
            )
            self.assertEqual(resultado.returncode, 0, resultado.stderr)
            criada = os.path.join(pasta, "revisoes", "tema-x", "config", "revisao.json")
            self.assertTrue(os.path.exists(criada), "revisão não foi criada na pasta de trabalho")
            # nada foi escrito dentro da instalação do plugin
            self.assertFalse(os.path.exists(os.path.join(PLUGIN, "revisoes")))


if __name__ == "__main__":
    unittest.main()
