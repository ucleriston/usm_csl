"""Interface de linha de comando do pipeline cienciométrico.

    python -m cienciometria <comando> [opções]

Comandos: importar, dedup, triagem, kappa, indicadores, redes, relatorio, prisma, tudo.
Ver docs/06-reprodutibilidade.md.
"""

import argparse
import json
import os
import sys

from . import __version__, indicadores, parsers, redes, relatorio, triagem
from .corpus_io import (
    carregar_corpus, registrar_execucao, salvar_arestas, salvar_corpus, salvar_nos, salvar_tabela,
)
from .dedup import deduplicar
from .normalizacao import carregar_tesauros, normalizar_registro

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONFIG = os.path.join(RAIZ, "config")


def _config_execucao():
    caminho = os.path.join(CONFIG, "execucao.json")
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def _ano_corte(dados):
    corte = (dados or {}).get("data_de_corte", "")
    try:
        return int(str(corte)[:4])
    except (ValueError, TypeError):
        import datetime
        return datetime.date.today().year


# --------------------------------------------------------------------------- comandos

def cmd_importar(args):
    registros, relatorio_arquivos = parsers.ler_diretorio(args.entrada)
    tesauros = carregar_tesauros(CONFIG)
    for reg in registros:
        normalizar_registro(reg, tesauros)
    print("Arquivos lidos:")
    for caminho, n, estado in relatorio_arquivos:
        print("  %-60s %6d  %s" % (os.path.relpath(caminho, RAIZ)[-60:], n, estado))
    if not registros:
        print("\nNenhum registro encontrado em %s." % args.entrada)
        print("Exporte as bases conforme docs/03-estrategias-de-busca.md e salve em dados/bruto/.")
        return 1
    salvar_corpus(args.saida, registros)
    salvar_tabela(
        os.path.join(os.path.dirname(args.saida), "importacao.csv"),
        [{"arquivo": c, "registros": n, "estado": e} for c, n, e in relatorio_arquivos],
    )
    print("\n%d registros importados → %s" % (len(registros), args.saida))
    registrar_execucao(args.log, "importar", "entrada=%s registros=%d" % (args.entrada, len(registros)))
    return 0


def cmd_dedup(args):
    registros = carregar_corpus(args.corpus)
    corpus, revisao, estatisticas = deduplicar(registros)
    salvar_corpus(args.corpus, corpus)
    destino = os.path.join(os.path.dirname(args.corpus), "revisao-duplicatas.csv")
    salvar_tabela(destino, revisao)
    with open(os.path.join(os.path.dirname(args.corpus), "dedup.json"), "w", encoding="utf-8") as fh:
        json.dump(estatisticas, fh, ensure_ascii=False, indent=2)
    for chave, valor in estatisticas.items():
        print("  %-28s %s" % (chave, valor))
    if revisao:
        print("\n%d pares na faixa 0,88-0,93 aguardam conferência humana em %s" %
              (len(revisao), os.path.relpath(destino, RAIZ)))
    registrar_execucao(args.log, "dedup", json.dumps(estatisticas))
    return 0


def cmd_triagem(args):
    corpus = carregar_corpus(args.corpus)
    linhas = triagem.planilha_de_triagem(corpus)
    salvar_tabela(args.saida, linhas, triagem.COLUNAS_TRIAGEM)
    print("Planilha de triagem com %d registros → %s" % (len(linhas), args.saida))
    print("Preencha decisao_r1/decisao_r2 com: incluido, excluido ou duvida.")
    print("Nas exclusões, informe o código E1-E8 (ver docs/02-protocolo-prisma.md, §3.2).")
    registrar_execucao(args.log, "triagem", "registros=%d" % len(linhas))
    return 0


def cmd_kappa(args):
    linhas = triagem.ler_triagem(args.triagem)
    resultado = triagem.concordancia(linhas)
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if resultado.get("kappa") is not None and not resultado["atinge_meta_0.75"]:
        print("\nATENÇÃO: kappa abaixo de 0,75. O protocolo (§6) manda reescrever os critérios "
              "e refazer a rodada, não resolver caso a caso.")
    registrar_execucao(args.log, "kappa", json.dumps(
        {k: v for k, v in resultado.items() if k != "ids_divergentes"}))
    return 0


def cmd_indicadores(args):
    corpus = carregar_corpus(args.corpus)
    if not corpus:
        print("Corpus vazio.")
        return 1
    dados = _config_execucao()
    ano_corte = _ano_corte(dados)
    saida = args.saida
    arquivos = []

    prod = indicadores.producao_anual(corpus, ano_corte)
    arquivos.append(salvar_e_nomear(os.path.join(saida, "producao_anual.csv"), prod))

    fontes = indicadores.contagem_por_campo(
        [{"fonte": r["fonte"], "campo": [r["fonte"]] if r.get("fonte") else []} for r in corpus],
        "campo")
    arquivos.append(salvar_e_nomear(os.path.join(saida, "fontes.csv"), fontes))

    autores = indicadores.contagem_por_campo(corpus, "autores")
    arquivos.append(salvar_e_nomear(os.path.join(saida, "autores.csv"), autores))

    paises = indicadores.contagem_por_campo(corpus, "paises")
    arquivos.append(salvar_e_nomear(os.path.join(saida, "paises.csv"), paises))

    instituicoes = indicadores.contagem_por_campo(corpus, "instituicoes")
    arquivos.append(salvar_e_nomear(os.path.join(saida, "instituicoes.csv"), instituicoes))

    lotka = indicadores.lei_de_lotka(corpus)
    arquivos.append(salvar_e_nomear(os.path.join(saida, "lotka.csv"), lotka["tabela"]))

    bradford = indicadores.lei_de_bradford(corpus)
    arquivos.append(salvar_e_nomear(os.path.join(saida, "bradford.csv"), bradford["tabela"]))

    price = indicadores.indice_de_price(corpus)
    arquivos.append(salvar_e_nomear(os.path.join(saida, "price.csv"), price["detalhe"]))

    imp = indicadores.impacto(corpus, ano_corte)
    arquivos.append(salvar_e_nomear(os.path.join(saida, "mais_citados.csv"), imp["mais_citados"]))

    col = indicadores.colaboracao(corpus)
    arquivos.append(salvar_e_nomear(os.path.join(saida, "colaboracao_paises.csv"), col["por_pais"]))

    resultados = {
        "n_corpus": len(corpus),
        "ano_corte": ano_corte,
        "semente": args.seed,
        "producao_anual": prod,
        "tcac": indicadores.tcac(prod),
        "fontes": fontes,
        "autores": autores,
        "paises": paises,
        "instituicoes": instituicoes,
        "lotka": lotka,
        "bradford": bradford,
        "price": price,
        "impacto": imp,
        "colaboracao": col,
        "arquivos": [a for a in arquivos if a],
    }
    _guardar_parcial(saida, resultados)
    print("Indicadores gerados em %s (%d registros)." % (saida, len(corpus)))
    registrar_execucao(args.log, "indicadores", "n=%d ano_corte=%d" % (len(corpus), ano_corte))
    return 0


def cmd_redes(args):
    corpus = carregar_corpus(args.corpus)
    if not corpus:
        print("Corpus vazio.")
        return 1
    saida = args.saida
    os.makedirs(saida, exist_ok=True)
    parcial = _ler_parcial(saida)
    arquivos = list(parcial.get("arquivos", []))

    def exportar(prefixo, nos, arestas, agrupamentos=None):
        if not nos:
            return {}
        normalizados = redes.normalizar_associacao(nos, arestas)
        salvar_nos(os.path.join(saida, "%s_nos.csv" % prefixo), nos, agrupamentos)
        salvar_arestas(os.path.join(saida, "%s_arestas.csv" % prefixo), arestas, normalizados)
        redes.exportar_pajek(os.path.join(saida, "%s.net" % prefixo), nos, arestas)
        redes.exportar_gml(os.path.join(saida, "%s.gml" % prefixo), nos, arestas, agrupamentos)
        for sufixo in ("_nos.csv", "_arestas.csv", ".net", ".gml"):
            arquivos.append(os.path.join(saida, prefixo + sufixo))
        return redes.metricas_da_rede(nos, arestas)

    # co-palavras + mapa temático
    nos_cp, arestas_cp = redes.rede_copalavras(corpus, minimo=args.min_termo)
    grupos_cp = redes.propagacao_de_rotulos(nos_cp, arestas_cp, semente=args.seed)
    metricas_cp = exportar("copalavras", nos_cp, arestas_cp, grupos_cp)
    mapa = redes.mapa_tematico(nos_cp, arestas_cp, grupos_cp)
    salvar_tabela(os.path.join(saida, "mapa_tematico.csv"), mapa)
    periodos, fluxos = redes.evolucao_tematica(corpus)
    salvar_tabela(os.path.join(saida, "evolucao_tematica.csv"), fluxos)

    # coautoria, instituições, países
    nos_ca, arestas_ca = redes.rede_coautoria(corpus, "autores", minimo=args.min_autor)
    metricas_ca = exportar("coautoria", nos_ca, arestas_ca,
                           redes.propagacao_de_rotulos(nos_ca, arestas_ca, semente=args.seed))
    nos_in, arestas_in = redes.rede_coautoria(corpus, "instituicoes", minimo=2)
    metricas_in = exportar("instituicoes", nos_in, arestas_in)
    nos_pa, arestas_pa = redes.rede_coautoria(corpus, "paises", minimo=1)
    metricas_pa = exportar("paises", nos_pa, arestas_pa)

    # co-citação e acoplamento
    nos_cc, arestas_cc, cobertura = redes.rede_cocitacao(corpus, minimo=args.min_cocitacao)
    grupos_cc = redes.propagacao_de_rotulos(nos_cc, arestas_cc, semente=args.seed)
    metricas_cc = exportar("cocitacao", nos_cc, arestas_cc, grupos_cc)
    nos_ac, arestas_ac = redes.acoplamento_bibliografico(corpus, minimo=args.min_acoplamento)
    metricas_ac = exportar("acoplamento", nos_ac, arestas_ac)

    parcial.update(
        {
            "copalavras": {
                "metricas": metricas_cp,
                "mapa": mapa,
                "periodos": periodos,
                "fluxos": fluxos,
                "top": _topo(nos_cp, grupos_cp),
            },
            "coautoria": {"metricas": metricas_ca},
            "instituicoes_rede": {"metricas": metricas_in},
            "paises_rede": {"metricas": metricas_pa},
            "cocitacao": dict(cobertura, metricas=metricas_cc, top=_topo(nos_cc, grupos_cc)),
            "acoplamento": {"metricas": metricas_ac},
            "arquivos": sorted(set(arquivos)),
            "n_corpus": len(corpus),
            "semente": args.seed,
        }
    )
    _guardar_parcial(saida, parcial)
    print("Redes geradas em %s." % saida)
    registrar_execucao(args.log, "redes", "n=%d seed=%d" % (len(corpus), args.seed))
    return 0


def cmd_relatorio(args):
    resultados = _ler_parcial(args.saida)
    if not resultados:
        print("Nada a relatar: execute 'indicadores' e 'redes' antes.")
        return 1
    resultados["proposicoes"] = _avaliar_proposicoes(resultados)
    caminho = relatorio.montar(resultados, args.saida, _config_execucao())
    print("Relatório → %s" % caminho)
    registrar_execucao(args.log, "relatorio", caminho)
    return 0


def cmd_prisma(args):
    brutos = carregar_corpus(args.brutos) if os.path.exists(args.brutos) else []
    dedup_json = os.path.join(os.path.dirname(args.corpus), "dedup.json")
    estatisticas = {}
    if os.path.exists(dedup_json):
        with open(dedup_json, encoding="utf-8") as fh:
            estatisticas = json.load(fh)
    linhas = triagem.ler_triagem(args.triagem) if os.path.exists(args.triagem) else None
    if not brutos:
        brutos = carregar_corpus(args.corpus)
        estatisticas.setdefault("saida", len(brutos))
    fluxo = triagem.contagens_prisma(brutos, estatisticas, linhas)
    os.makedirs(args.saida, exist_ok=True)
    with open(os.path.join(args.saida, "prisma.json"), "w", encoding="utf-8") as fh:
        json.dump(fluxo, fh, ensure_ascii=False, indent=2)
    diagrama = triagem.diagrama_prisma(fluxo)
    with open(os.path.join(args.saida, "prisma.md"), "w", encoding="utf-8") as fh:
        fh.write("# Fluxo PRISMA\n\n" + diagrama + "\n")
    print(diagrama)
    registrar_execucao(args.log, "prisma", json.dumps(
        {k: v for k, v in fluxo.items() if not isinstance(v, dict)}))
    return 0


def cmd_tudo(args):
    for funcao in (cmd_importar, cmd_dedup):
        codigo = funcao(args)
        if codigo:
            return codigo
    cmd_indicadores(args)
    cmd_redes(args)
    cmd_prisma(args)
    return cmd_relatorio(args)


# --------------------------------------------------------------------------- auxiliares

def salvar_e_nomear(caminho, linhas):
    salvar_tabela(caminho, linhas)
    return caminho


def _topo(nos, grupos, limite=30):
    return [
        {"item": no, "frequencia": freq, "agrupamento": grupos.get(no, "")}
        for no, freq in sorted(nos.items(), key=lambda kv: -kv[1])[:limite]
    ]


def _caminho_parcial(saida):
    return os.path.join(saida, "resultados.json")


def _guardar_parcial(saida, dados):
    os.makedirs(saida, exist_ok=True)
    with open(_caminho_parcial(saida), "w", encoding="utf-8") as fh:
        json.dump(relatorio._limpar(dados), fh, ensure_ascii=False, indent=2)


def _ler_parcial(saida):
    caminho = _caminho_parcial(saida)
    if not os.path.exists(caminho):
        return {}
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def _avaliar_proposicoes(r):
    """Aplica os critérios de refutação do plano de análise, §6."""
    linhas = []
    lotka = r.get("lotka", {})
    alpha = lotka.get("alpha")
    linhas.append({
        "proposicao": "P1 — produtividade segue Lotka",
        "indicador": "α e KS",
        "valor": "α=%s; KS=%s" % (alpha, lotka.get("ks")),
        "situacao": "sustentada" if (alpha is not None and 1.7 <= alpha <= 2.3
                                     and lotka.get("adere")) else "refutada",
    })
    brad = r.get("bradford", {})
    zonas = brad.get("zonas", [])
    linhas.append({
        "proposicao": "P2 — dispersão segue Bradford",
        "indicador": "multiplicador entre zonas",
        "valor": str(brad.get("multiplicador")),
        "situacao": "sustentada" if zonas and zonas[0]["fontes"] and zonas[0]["artigos_%"] >= 25
                    else "verificar manualmente",
    })
    cocit = r.get("cocitacao", {})
    linhas.append({
        "proposicao": "P3 — base intelectual anglófona",
        "indicador": "origem das referências mais co-citadas",
        "valor": "cobertura do subcorpus: %s%%" % cocit.get("cobertura_%"),
        "situacao": "exige codificação manual da origem das 50 referências mais co-citadas",
    })
    coaut = (r.get("coautoria") or {}).get("metricas", {})
    col = r.get("colaboracao", {})
    gigante = coaut.get("componente_gigante_%", 0) or 0
    linhas.append({
        "proposicao": "P4 — rede fragmentada por região",
        "indicador": "componente gigante e MCP",
        "valor": "gigante=%s%%; coautoria internacional=%s%%" % (
            gigante, col.get("coautoria_internacional_%")),
        "situacao": "refutada" if gigante > 60 and (col.get("coautoria_internacional_%") or 0) > 40
                    else "sustentada",
    })
    mapa = (r.get("copalavras") or {}).get("mapa", [])
    emergentes = [l for l in mapa if l.get("quadrante") == "emergente_ou_declinio"]
    linhas.append({
        "proposicao": "P5 — núcleo maduro e temas emergentes",
        "indicador": "quadrantes do mapa temático",
        "valor": "%d agrupamentos; %d no quadrante emergente/declínio" % (len(mapa), len(emergentes)),
        "situacao": "sustentada" if emergentes else "refutada",
    })
    linhas.append({
        "proposicao": "P6 — isolamento da produção brasileira",
        "indicador": "matriz de citação cruzada",
        "valor": "requer identificação do citado nas referências",
        "situacao": "exige etapa manual (plano de análise, §5)",
    })
    return linhas


def principal(argv=None):
    p = argparse.ArgumentParser(
        prog="cienciometria",
        description="Pipeline da revisão cienciométrica sobre federalismo fiscal subnacional",
    )
    p.add_argument("--version", action="version", version="cienciometria %s" % __version__)
    sub = p.add_subparsers(dest="comando", required=True)

    def comuns(sp, **padroes):
        sp.add_argument("--corpus", default=padroes.get("corpus", "dados/processado/corpus.csv"))
        sp.add_argument("--saida", default=padroes.get("saida", "saidas/"))
        sp.add_argument("--log", default="saidas/")
        sp.add_argument("--seed", type=int, default=42)
        sp.add_argument("--min-termo", type=int, default=5)
        sp.add_argument("--min-autor", type=int, default=2)
        sp.add_argument("--min-cocitacao", type=int, default=5)
        sp.add_argument("--min-acoplamento", type=int, default=3)
        sp.add_argument("--entrada", default="dados/bruto")
        sp.add_argument("--triagem", default="dados/processado/triagem-preenchida.csv")
        sp.add_argument("--brutos", default="dados/processado/corpus-bruto.csv")

    funcoes = {
        "importar": cmd_importar, "dedup": cmd_dedup, "triagem": cmd_triagem,
        "kappa": cmd_kappa, "indicadores": cmd_indicadores, "redes": cmd_redes,
        "relatorio": cmd_relatorio, "prisma": cmd_prisma, "tudo": cmd_tudo,
    }
    ajuda = {
        "importar": "lê dados/bruto e monta o corpus",
        "dedup": "deduplica o corpus e separa pares para revisão humana",
        "triagem": "gera a planilha cega de triagem",
        "kappa": "calcula a concordância entre revisores",
        "indicadores": "calcula os indicadores de desempenho",
        "redes": "constrói e exporta as redes e o mapa temático",
        "relatorio": "monta o relatório em Markdown",
        "prisma": "gera as contagens e o diagrama do fluxo PRISMA",
        "tudo": "executa importar → dedup → indicadores → redes → prisma → relatorio",
    }
    for nome, funcao in funcoes.items():
        sp = sub.add_parser(nome, help=ajuda[nome])
        if nome == "importar":
            comuns(sp, corpus="dados/processado/corpus.csv")
            sp.set_defaults(saida="dados/processado/corpus.csv")
        elif nome == "triagem":
            comuns(sp)
            sp.set_defaults(saida="modelos/triagem.csv")
        else:
            comuns(sp)
        sp.set_defaults(funcao=funcao)

    args = p.parse_args(argv)
    return args.funcao(args)


if __name__ == "__main__":
    sys.exit(principal())
