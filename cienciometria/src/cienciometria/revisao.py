"""Uma revisão é uma pasta em revisoes/<slug>/ com a sua própria configuração.

O motor (parsers, indicadores, redes, relatório) não sabe de tema nenhum: tudo
o que é específico de uma revisão — recorte, strings, tesauros, limiares,
subperíodos e proposições — vem do arquivo config/revisao.json da instância.
"""

import copy
import datetime
import json
import os
import shutil

# Onde está instalado o motor: guarda os seus próprios recursos (esqueleto de revisão,
# léxico de países). Pode ser o repositório ou a pasta de um plugin instalado.
DIR_MOTOR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR_CONFIG_MOTOR = os.path.join(DIR_MOTOR, "config")
DIR_MODELO = os.path.join(DIR_MOTOR, "modelos", "revisao-modelo")


def raiz_de_trabalho():
    """Pasta onde ficam as revisões — o trabalho do usuário, não a instalação do motor.

    Ordem de resolução: a variável CIENCIOMETRIA_DIR, se definida; senão, o primeiro
    diretório (do atual para cima) que já contenha `revisoes/`; senão, o diretório atual.
    Isso permite rodar o motor instalado como plugin sobre a pasta de trabalho de quem chama,
    sem escrever nada dentro da instalação.
    """
    declarada = os.environ.get("CIENCIOMETRIA_DIR")
    if declarada:
        return os.path.abspath(os.path.expanduser(declarada))
    atual = os.path.abspath(os.getcwd())
    while True:
        if os.path.isdir(os.path.join(atual, "revisoes")):
            return atual
        pai = os.path.dirname(atual)
        if pai == atual:
            return os.path.abspath(os.getcwd())
        atual = pai


def dir_revisoes():
    return os.path.join(raiz_de_trabalho(), "revisoes")

NOMES_TESAUROS = {
    "termos": "thesauro-termos.json",
    "fontes": "thesauro-fontes.json",
    "instituicoes": "thesauro-instituicoes.json",
    "paises": "lexico-paises.json",
    "iso2": "iso2-iso3.json",
}

PADRAO = {
    "slug": "",
    "titulo": "",
    "tema": "",
    "responsavel": "",
    "janela": {"inicio": 1990, "fim": None},
    "idiomas": ["pt", "en", "es"],
    "tipos_documento": ["artigo", "revisao", "capitulo", "anais"],
    "bases": ["scopus", "wos", "scielo", "dimensions", "lens"],
    "precedencia_bases": ["scopus", "wos", "dimensions", "lens", "scielo", "manual"],
    "campo_termos": "palavras_chave",
    "semente": 42,
    "limiares": {
        "min_termo": 5,
        "min_autor": 2,
        "min_cocitacao": 5,
        "min_acoplamento": 3,
        "limite_nos": 300,
        "dedup_automatico": 0.93,
        "dedup_revisao_humana": 0.88,
        "kappa_minimo": 0.75,
    },
    "periodos": [[1990, 1999], [2000, 2009], [2010, 2019], [2020, 2100]],
    "vocabulario_temas": {},
    "proposicoes": [],
}


class Revisao:
    """Resolve caminhos e configuração de uma revisão."""

    def __init__(self, slug, base=None):
        self.slug = slug
        self.base = base or dir_revisoes()
        self.dir = os.path.join(self.base, slug)
        self.config = self._carregar_config()

    # ------------------------------------------------------------------ caminhos
    @property
    def dir_config(self):
        return os.path.join(self.dir, "config")

    @property
    def dir_bruto(self):
        return os.path.join(self.dir, "dados", "bruto")

    @property
    def dir_processado(self):
        return os.path.join(self.dir, "dados", "processado")

    @property
    def dir_saidas(self):
        return os.path.join(self.dir, "saidas")

    @property
    def corpus(self):
        return os.path.join(self.dir_processado, "corpus.csv")

    @property
    def corpus_bruto(self):
        return os.path.join(self.dir_processado, "corpus-bruto.csv")

    @property
    def triagem(self):
        return os.path.join(self.dir_processado, "triagem-preenchida.csv")

    def existe(self):
        return os.path.isdir(self.dir)

    # ------------------------------------------------------------------ config
    def _carregar_config(self):
        config = copy.deepcopy(PADRAO)
        config["slug"] = self.slug
        caminho = os.path.join(self.dir, "config", "revisao.json")
        if os.path.exists(caminho):
            with open(caminho, encoding="utf-8") as fh:
                gravado = json.load(fh)
            for chave, valor in gravado.items():
                if chave.startswith("_"):
                    continue
                if isinstance(valor, dict) and isinstance(config.get(chave), dict):
                    config[chave].update(valor)
                else:
                    config[chave] = valor
        return config

    def execucao(self):
        caminho = os.path.join(self.dir_config, "execucao.json")
        if os.path.exists(caminho):
            with open(caminho, encoding="utf-8") as fh:
                return json.load(fh)
        return {}

    def ano_corte(self):
        """Ano de corte: o declarado em execucao.json; senão, o fim da janela; senão, hoje."""
        corte = (self.execucao() or {}).get("data_de_corte", "")
        try:
            return int(str(corte)[:4])
        except (ValueError, TypeError):
            pass
        fim = (self.config.get("janela") or {}).get("fim")
        return int(fim) if fim else datetime.date.today().year

    def periodos(self):
        return [tuple(p) for p in self.config.get("periodos") or PADRAO["periodos"]]

    def limiar(self, nome):
        return self.config["limiares"].get(nome, PADRAO["limiares"].get(nome))

    def tesauros(self):
        """Tesauros do motor sobrepostos pelos da revisão (o da revisão vence)."""
        from .normalizacao import carregar_tesauro

        tesauros = {}
        for chave, arquivo in NOMES_TESAUROS.items():
            juntos = {}
            juntos.update(carregar_tesauro(os.path.join(DIR_CONFIG_MOTOR, arquivo)))
            juntos.update(carregar_tesauro(os.path.join(self.dir_config, arquivo)))
            tesauros[chave] = juntos
        return tesauros

    # ------------------------------------------------------------------ criação
    @classmethod
    def criar(cls, slug, titulo="", tema="", base=None):
        """Copia o esqueleto de modelos/revisao-modelo para revisoes/<slug>."""
        revisao = cls(slug, base=base)
        if revisao.existe():
            raise FileExistsError("já existe uma revisão em %s" % revisao.dir)
        if not os.path.isdir(DIR_MODELO):
            raise FileNotFoundError(
                "esqueleto de revisão não encontrado em %s — a instalação do motor está incompleta"
                % DIR_MODELO)
        os.makedirs(revisao.base, exist_ok=True)
        shutil.copytree(DIR_MODELO, revisao.dir)
        caminho = os.path.join(revisao.dir, "config", "revisao.json")
        with open(caminho, encoding="utf-8") as fh:
            config = json.load(fh)
        config["slug"] = slug
        config["titulo"] = titulo or slug.replace("-", " ").capitalize()
        config["tema"] = tema or config.get("tema", "")
        config["criada_em"] = datetime.date.today().isoformat()
        with open(caminho, "w", encoding="utf-8") as fh:
            json.dump(config, fh, ensure_ascii=False, indent=2)
        for pasta in ("dados/bruto", "dados/processado", "saidas"):
            destino = os.path.join(revisao.dir, pasta)
            os.makedirs(destino, exist_ok=True)
            marcador = os.path.join(destino, ".gitkeep")
            if not os.path.exists(marcador):
                open(marcador, "w").close()
        # substitui os marcadores do modelo nos documentos
        for raiz, _, arquivos in os.walk(os.path.join(revisao.dir, "docs")):
            for arquivo in arquivos:
                if not arquivo.endswith(".md"):
                    continue
                caminho_doc = os.path.join(raiz, arquivo)
                with open(caminho_doc, encoding="utf-8") as fh:
                    texto = fh.read()
                texto = (texto.replace("{{TITULO}}", config["titulo"])
                              .replace("{{TEMA}}", config["tema"] or "«definir o tema»")
                              .replace("{{SLUG}}", slug))
                with open(caminho_doc, "w", encoding="utf-8") as fh:
                    fh.write(texto)
        return cls(slug, base=base)


def listar(base=None):
    """Lista as revisões existentes, com título e situação do corpus."""
    base = base or dir_revisoes()
    if not os.path.isdir(base):
        return []
    saida = []
    for slug in sorted(os.listdir(base)):
        if slug.startswith(".") or not os.path.isdir(os.path.join(base, slug)):
            continue
        revisao = Revisao(slug, base=base)
        saida.append(
            {
                "slug": slug,
                "titulo": revisao.config.get("titulo") or slug,
                "corte": (revisao.execucao() or {}).get("data_de_corte") or "não declarada",
                "corpus": os.path.exists(revisao.corpus),
            }
        )
    return saida
