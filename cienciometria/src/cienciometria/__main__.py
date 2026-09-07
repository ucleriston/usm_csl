"""Interface de linha de comando do motor cienciométrico.

    python -m cienciometria <comando> --revisao <slug>

O motor é genérico: o tema, o recorte, os tesauros, os limiares e as proposições
vêm de revisoes/<slug>/config/revisao.json. Ver docs/06-reprodutibilidade.md.
"""

import argparse
import json
import os
import sys

from . import (__version__, artigo, coleta, comparacao, estado, fichamento, indicadores,
               parsers, proposicoes, redes, relatorio, triagem)
from .corpus_io import (
    carregar_corpus, registrar_execucao, salvar_arestas, salvar_corpus, salvar_nos, salvar_tabela,
)
from .dedup import deduplicar
from .normalizacao import normalizar_registro
from .revisao import Revisao, dir_revisoes, listar


def _revisao(args):
    revisao = Revisao(args.revisao, base=getattr(args, "base_revisoes", None) or dir_revisoes())
    if not revisao.existe():
        disponiveis = ", ".join(r["slug"] for r in listar()) or "nenhuma"
        raise SystemExit(
            "Revisão '%s' não encontrada em %s.\nDisponíveis: %s\n"
            "Crie uma com: python -m cienciometria nova <slug> --titulo \"...\""
            % (args.revisao, dir_revisoes(), disponiveis)
        )
    return revisao


def _limiar(revisao, args, nome, atributo):
    """Valor de linha de comando quando informado; senão, o da revisão."""
    informado = getattr(args, atributo, None)
    return informado if informado is not None else revisao.limiar(nome)


def _semente(revisao, args):
    return args.seed if args.seed is not None else revisao.config.get("semente", 42)


# --------------------------------------------------------------------------- comandos

def cmd_nova(args):
    try:
        revisao = Revisao.criar(args.slug, titulo=args.titulo or "", tema=args.tema or "",
                                base=getattr(args, "base_revisoes", None))
    except (FileExistsError, FileNotFoundError) as erro:
        raise SystemExit(str(erro))
    print("Revisão criada em %s\n" % os.path.relpath(revisao.dir))
    print("Próximos passos:")
    print("  1. Descreva o recorte em %s" % os.path.join(revisao.dir_config, "revisao.json"))
    print("     (janela, idiomas, limiares, subperíodos e proposições com critério de refutação)")
    print("  2. Preencha os documentos em %s" % os.path.join(revisao.dir, "docs"))
    print("     projeto, protocolo, estratégias de busca e livro de códigos")
    print("  3. Monte os tesauros em %s" % revisao.dir_config)
    print("  4. Rode as buscas, salve as exportações em %s e registre execucao.json" % revisao.dir_bruto)
    print("  5. make analise REVISAO=%s" % args.slug)
    return 0


def cmd_listar(args):
    revisoes = listar()
    if not revisoes:
        print("Nenhuma revisão em %s." % dir_revisoes())
        return 0
    print("%-38s %-14s %s" % ("SLUG", "CORTE", "TÍTULO"))
    for r in revisoes:
        marca = "•" if r["corpus"] else " "
        print("%s %-36s %-14s %s" % (marca, r["slug"], r["corte"], r["titulo"]))
    print("\n(• = corpus já construído)")
    return 0


# tipos do corpus → vocabulário de cada API
TIPOS_API = {
    "openalex": {"artigo": "article", "revisao": "review", "capitulo": "book-chapter",
                 "anais": "proceedings-article"},
    "crossref": {"artigo": "journal-article", "revisao": "journal-article",
                 "capitulo": "book-chapter", "anais": "proceedings-article"},
}


def cmd_estado(args):
    """Onde a pesquisa está e qual é o próximo passo."""
    revisao = _revisao(args)
    dados = estado.resumo(revisao)
    print(estado.formatar(dados))
    if args.json:
        print()
        print(json.dumps(dados, ensure_ascii=False, indent=2))
    return 0


def cmd_fichar(args):
    """Cria fichas de leitura, ou sugere quais artigos fichar."""
    revisao = _revisao(args)
    corpus = carregar_corpus(revisao.corpus) if os.path.exists(revisao.corpus) else []
    if not corpus:
        print("Corpus vazio: construa o corpus antes de decidir o que ler.")
        return 1

    if args.sugerir:
        resultados = _ler_parcial(revisao.dir_saidas)
        sugestoes = fichamento.sugerir_leitura(corpus, resultados, args.quantidade)
        destino = os.path.join(revisao.dir_processado, "leitura-sugerida.csv")
        salvar_tabela(destino, sugestoes)
        print("Sugestão de leitura (%d artigos) → %s\n" % (len(sugestoes), os.path.relpath(destino)))
        for i, s in enumerate(sugestoes, 1):
            print("%2d. [%s] %s (%s cit.)" % (i, s["ano"], (s["titulo"] or "")[:72], s["citacoes"]))
            print("    %s | %s" % (s["motivo"], s["id"]))
        print("\nA escolha final é sua: estes são candidatos por critério declarado, não veredicto.")
        print("Para criar as fichas: cienciometria fichar --revisao %s --id <id> [--id <id> ...]"
              % revisao.slug)
        print("Ou todas as sugeridas de uma vez: cienciometria fichar --revisao %s --sugeridas"
              % revisao.slug)
        return 0

    alvos = list(args.id or [])
    if args.sugeridas:
        caminho = os.path.join(revisao.dir_processado, "leitura-sugerida.csv")
        if not os.path.exists(caminho):
            raise SystemExit("Rode antes: cienciometria fichar --revisao %s --sugerir" % revisao.slug)
        import csv as _csv
        with open(caminho, encoding="utf-8-sig", newline="") as fh:
            alvos += [linha["id"] for linha in _csv.DictReader(fh)]
    if not alvos:
        raise SystemExit("Informe --id <id do registro>, --sugeridas, ou use --sugerir para ver "
                         "quais artigos valem a leitura.")

    indice = {r["id"]: r for r in corpus}
    criadas, existentes, ausentes = [], [], []
    for alvo in alvos:
        registro = indice.get(alvo)
        if not registro:
            ausentes.append(alvo)
            continue
        caminho, nova = fichamento.criar_ficha(revisao, registro)
        (criadas if nova else existentes).append(os.path.basename(caminho))
    print("%d ficha(s) criada(s) em %s" % (len(criadas), os.path.relpath(fichamento.dir_fichas(revisao))))
    for nome in criadas:
        print("  " + nome)
    if existentes:
        print("%d já existiam e foram preservadas." % len(existentes))
    if ausentes:
        print("Não encontrados no corpus: %s" % ", ".join(ausentes))
    print("\nTítulo, referência e palavras-chave vêm do corpus. O resto exige a leitura do texto "
          "integral — resumo não basta para dizer qual lacuna os autores declararam.")
    registrar_execucao(revisao.dir_saidas, "fichar", "criadas=%d" % len(criadas))
    return 0


def cmd_fichamentos(args):
    """Consolida as fichas e confronta as lacunas declaradas com o corpus."""
    revisao = _revisao(args)
    fichas = fichamento.listar_fichas(revisao)
    if not fichas:
        print("Nenhuma ficha em %s." % os.path.relpath(fichamento.dir_fichas(revisao)))
        print("Comece por: cienciometria fichar --revisao %s --sugerir" % revisao.slug)
        return 1
    corpus = carregar_corpus(revisao.corpus) if os.path.exists(revisao.corpus) else []
    saida = args.saida or revisao.dir_saidas

    tabela = [dict({"ficha": f["arquivo"], "completa": "sim" if f["completa"] else "não",
                    "faltando": "; ".join(f["faltando"])},
                   **{k: " ".join(v.split())[:300] for k, v in f["campos"].items()})
              for f in fichas]
    salvar_tabela(os.path.join(saida, "fichamentos.csv"), tabela)

    lacunas = fichamento.matriz_de_lacunas(revisao, corpus)
    salvar_tabela(os.path.join(saida, "matriz-de-lacunas.csv"), lacunas)

    completas = [f for f in fichas if f["completa"]]
    print("%d ficha(s); %d completa(s)." % (len(fichas), len(completas)))
    for f in fichas:
        if not f["completa"]:
            print("  incompleta: %s — falta %s" % (f["arquivo"], "; ".join(f["faltando"])))
    print("\n%d lacuna(s) declarada(s) pelos autores → %s"
          % (len(lacunas), os.path.relpath(os.path.join(saida, "matriz-de-lacunas.csv"))))
    for linha in lacunas[:8]:
        print("  [%s] %s" % (linha["ano"], linha["lacuna_declarada"][:96]))
        if linha["ocorrencias_no_corpus"]:
            print("        no corpus: %s" % linha["ocorrencias_no_corpus"])
    if lacunas:
        print("\nLacuna cujo termo já aparece em boa parte do corpus foi preenchida depois daquela "
              "publicação. Confira antes de usá-la como justificativa.")
    registrar_execucao(revisao.dir_saidas, "fichamentos",
                       "fichas=%d completas=%d lacunas=%d" % (len(fichas), len(completas), len(lacunas)))
    return 0


def cmd_artigo(args):
    """Monta o rascunho do artigo com os números da análise."""
    revisao = _revisao(args)
    saida = args.saida or revisao.dir_saidas
    resultados = _ler_parcial(saida)
    if not resultados:
        print("Análise não encontrada: rode `cienciometria analise --revisao %s` antes." % revisao.slug)
        return 1
    if not resultados.get("proposicoes"):
        resultados["proposicoes"] = proposicoes.avaliar(revisao.config.get("proposicoes"), resultados)

    prisma_json = os.path.join(saida, "prisma.json")
    prisma = None
    if os.path.exists(prisma_json):
        with open(prisma_json, encoding="utf-8") as fh:
            prisma = json.load(fh)

    corpus = carregar_corpus(revisao.corpus) if os.path.exists(revisao.corpus) else []
    fichas = fichamento.listar_fichas(revisao)
    lacunas = fichamento.matriz_de_lacunas(revisao, corpus) if fichas else []

    texto = artigo.montar(revisao, resultados, prisma=prisma, lacunas=lacunas, fichas=fichas)
    caminho = artigo.salvar(os.path.join(saida, "artigo.md"), texto)
    pendencias = artigo.pendencias(texto)

    print("Rascunho → %s" % os.path.relpath(caminho))
    print("  %d trecho(s) marcado(s) [ESCREVER] e %d [SEM DADO]."
          % (pendencias["escrever"], pendencias["sem_dado"]))
    if not fichas:
        print("\nATENÇÃO: nenhum fichamento. A introdução e a discussão dependem da leitura dos "
              "artigos-núcleo — é de lá que sai a lacuna que justifica a pesquisa.")
    if pendencias["sem_dado"]:
        print("Cada [SEM DADO] aponta uma etapa que não foi executada. Reexecute-a em vez de "
              "preencher o valor à mão.")
    registrar_execucao(revisao.dir_saidas, "artigo", json.dumps(pendencias))
    return 0


def cmd_coletar(args):
    """Baixa registros de fontes abertas (OpenAlex, Crossref) para dados/bruto."""
    import datetime

    revisao = _revisao(args)
    if not args.busca:
        raise SystemExit("Informe o que buscar: --busca \"termos da consulta\"")
    janela = revisao.config.get("janela") or {}
    de = args.de if args.de is not None else janela.get("inicio")
    ate = args.ate if args.ate is not None else janela.get("fim")
    tipos = sorted({TIPOS_API[args.fonte].get(t) for t in revisao.config.get("tipos_documento") or []
                    if TIPOS_API[args.fonte].get(t)})
    idiomas = revisao.config.get("idiomas") or []

    hoje = datetime.date.today().isoformat()
    destino = os.path.join(revisao.dir_bruto, "%s_%s" % (args.fonte, hoje))
    os.makedirs(destino, exist_ok=True)

    def progresso(baixados, total):
        print("  %d registros baixados%s" % (baixados, " de %s" % total if total else ""))

    print("Consultando %s: %s" % (args.fonte, args.busca))
    try:
        resultado = coleta.coletar(
            args.fonte, busca=args.busca, destino=destino, de=de, ate=ate, tipos=tipos,
            idiomas=idiomas if args.fonte == "openalex" else None, email=args.email,
            limite=args.limite, extra=args.filtro_extra if args.fonte == "openalex" else None,
            ao_avancar=progresso,
        )
    except coleta.ColetaBloqueada as erro:
        print("\nColeta interrompida: %s" % erro)
        print("Nada foi gravado além das páginas já baixadas. Não há como contornar um bloqueio "
              "de política de rede a partir daqui — use outra rede ou exporte pela interface da base.")
        return 1
    except ValueError as erro:
        raise SystemExit(str(erro))

    if not resultado["registros"]:
        print("A consulta não devolveu resultados. Reveja os termos antes de concluir que a "
              "literatura não existe.")
        return 1

    # o registro da execução é o que torna a coleta repetível (PRISMA-S)
    caminho_execucao = os.path.join(revisao.dir_config, "execucao.json")
    dados = revisao.execucao() or {}
    dados.setdefault("execucoes", []).append({
        "base": args.fonte,
        "string_id": "API",
        "data": hoje,
        "hora": datetime.datetime.now().strftime("%H:%M"),
        "filtros": resultado["filtro"],
        "resultados": resultado["registros"],
        "arquivo": os.path.relpath(destino, revisao.dir),
        "consulta": args.busca,
        "limite_aplicado": args.limite,
    })
    if not dados.get("data_de_corte"):
        dados["data_de_corte"] = hoje
    with open(caminho_execucao, "w", encoding="utf-8") as fh:
        json.dump(dados, fh, ensure_ascii=False, indent=2)

    print("\n%d registros salvos em %s (%d páginas)" % (
        resultado["registros"], os.path.relpath(destino), len(resultado["paginas"])))
    print("Execução registrada em %s" % os.path.relpath(caminho_execucao))
    if resultado["registros"] >= args.limite:
        print("ATENÇÃO: o limite de %d foi atingido — a consulta provavelmente tem mais resultados. "
              "Refine a busca ou aumente --limite, e registre a decisão." % args.limite)
    print("Próximo passo: %s importar --revisao %s" % ("cienciometria", revisao.slug))
    registrar_execucao(revisao.dir_saidas, "coletar", "fonte=%s registros=%d busca=%s" % (
        args.fonte, resultado["registros"], args.busca))
    return 0


def cmd_comparar(args):
    """Mede o que uma alteração na string de busca derrubou e o que ela trouxe."""
    if not args.antes or not args.depois:
        raise SystemExit("Informe as duas exportações: --antes <arquivo|pasta> --depois <arquivo|pasta>")
    revisao = _revisao(args)
    resultado = comparacao.comparar(args.antes, args.depois)
    saida = args.saida or revisao.dir_saidas
    salvar_tabela(os.path.join(saida, "comparacao_perdidos.csv"), resultado["tabela_perdidos"])
    salvar_tabela(os.path.join(saida, "comparacao_ganhos.csv"), resultado["tabela_ganhos"])
    salvar_tabela(os.path.join(saida, "comparacao_fontes_perdidas.csv"), resultado["fontes_dos_perdidos"])

    print("antes: %d registros | depois: %d" % (resultado["antes"], resultado["depois"]))
    print("mantidos: %d (%.2f%% do conjunto anterior)" % (resultado["mantidos"], resultado["retencao_%"]))
    print("perdidos: %d | ganhos: %d" % (resultado["perdidos"], resultado["ganhos"]))
    if resultado["fontes_dos_perdidos"]:
        print("\nDe onde vêm os registros perdidos:")
        for linha in resultado["fontes_dos_perdidos"][:8]:
            print("  %-52s %d" % (linha["fonte"][:52], linha["registros"]))
    if resultado["mais_citado_perdido"]:
        maior = resultado["mais_citado_perdido"]
        print("\nMais citado entre os perdidos (%s citações): %s" % (
            maior["citacoes"], maior["titulo"][:80]))
    print("\nA contagem sozinha não decide nada: leia comparacao_perdidos.csv e julgue se o que "
          "saiu era ruído ou literatura pertinente. Um único perdido relevante já condena o filtro.")
    registrar_execucao(revisao.dir_saidas, "comparar", "perdidos=%d ganhos=%d retencao=%s" % (
        resultado["perdidos"], resultado["ganhos"], resultado["retencao_%"]))
    return 0


def cmd_importar(args):
    revisao = _revisao(args)
    entrada = args.entrada or revisao.dir_bruto
    registros, relatorio_arquivos = parsers.ler_diretorio(entrada)
    tesauros = revisao.tesauros()
    for reg in registros:
        normalizar_registro(reg, tesauros)
    print("Arquivos lidos:")
    for caminho, n, estado in relatorio_arquivos:
        print("  %-58s %6d  %s" % (os.path.basename(caminho)[:58], n, estado))
    if not registros:
        print("\nNenhum registro encontrado em %s." % entrada)
        print("Exporte as bases conforme os documentos de busca da revisão e salve os arquivos lá.")
        return 1
    salvar_corpus(revisao.corpus, registros)
    salvar_corpus(revisao.corpus_bruto, registros)
    salvar_tabela(
        os.path.join(revisao.dir_processado, "importacao.csv"),
        [{"arquivo": c, "registros": n, "estado": e} for c, n, e in relatorio_arquivos],
    )
    print("\n%d registros importados → %s" % (len(registros), os.path.relpath(revisao.corpus)))
    registrar_execucao(revisao.dir_saidas, "importar",
                       "revisao=%s entrada=%s registros=%d" % (revisao.slug, entrada, len(registros)))
    return 0


def cmd_dedup(args):
    revisao = _revisao(args)
    registros = carregar_corpus(revisao.corpus)
    corpus, revisao_manual, estatisticas = deduplicar(
        registros,
        limiar_auto=revisao.limiar("dedup_automatico"),
        limiar_revisao=revisao.limiar("dedup_revisao_humana"),
        precedencia=revisao.config.get("precedencia_bases"),
    )
    salvar_corpus(revisao.corpus, corpus)
    destino = os.path.join(revisao.dir_processado, "revisao-duplicatas.csv")
    salvar_tabela(destino, revisao_manual)
    with open(os.path.join(revisao.dir_processado, "dedup.json"), "w", encoding="utf-8") as fh:
        json.dump(estatisticas, fh, ensure_ascii=False, indent=2)
    for chave, valor in estatisticas.items():
        print("  %-28s %s" % (chave, valor))
    if revisao_manual:
        print("\n%d pares na faixa de dúvida aguardam conferência humana em %s"
              % (len(revisao_manual), os.path.relpath(destino)))
    registrar_execucao(revisao.dir_saidas, "dedup", json.dumps(estatisticas))
    return 0


def cmd_triagem(args):
    revisao = _revisao(args)
    corpus = carregar_corpus(revisao.corpus)
    linhas = triagem.planilha_de_triagem(corpus)
    destino = args.saida or os.path.join(revisao.dir_processado, "triagem.csv")
    salvar_tabela(destino, linhas, triagem.COLUNAS_TRIAGEM)
    print("Planilha de triagem com %d registros → %s" % (len(linhas), os.path.relpath(destino)))
    print("Preencha decisao_r1/decisao_r2 com: incluido, excluido ou duvida.")
    print("Nas exclusões, informe o código de exclusão declarado no protocolo da revisão.")
    registrar_execucao(revisao.dir_saidas, "triagem", "registros=%d" % len(linhas))
    return 0


def cmd_kappa(args):
    revisao = _revisao(args)
    caminho = args.triagem or revisao.triagem
    if not os.path.exists(caminho):
        raise SystemExit("Planilha de triagem não encontrada: %s" % caminho)
    linhas = triagem.ler_triagem(caminho)
    resultado = triagem.concordancia(linhas)
    minimo = revisao.limiar("kappa_minimo")
    resultado["minimo_da_revisao"] = minimo
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    if resultado.get("kappa") is not None and resultado["kappa"] < minimo:
        print("\nATENÇÃO: kappa abaixo de %s. O protocolo manda reescrever os critérios e refazer "
              "a rodada, não resolver caso a caso." % minimo)
    registrar_execucao(revisao.dir_saidas, "kappa", json.dumps(
        {k: v for k, v in resultado.items() if k != "ids_divergentes"}))
    return 0


def cmd_indicadores(args):
    revisao = _revisao(args)
    corpus = carregar_corpus(revisao.corpus)
    if not corpus:
        print("Corpus vazio: rode 'importar' antes.")
        return 1
    ano_corte = revisao.ano_corte()
    saida = args.saida or revisao.dir_saidas
    arquivos = []

    def guardar(nome, linhas):
        caminho = os.path.join(saida, nome)
        salvar_tabela(caminho, linhas)
        arquivos.append(caminho)

    prod = indicadores.producao_anual(corpus, ano_corte)
    guardar("producao_anual.csv", prod)
    fontes = indicadores.contagem_por_campo(
        [{"campo": [r["fonte"]] if r.get("fonte") else []} for r in corpus], "campo")
    guardar("fontes.csv", fontes)
    autores = indicadores.contagem_por_campo(corpus, "autores")
    guardar("autores.csv", autores)
    paises = indicadores.contagem_por_campo(corpus, "paises")
    guardar("paises.csv", paises)
    instituicoes = indicadores.contagem_por_campo(corpus, "instituicoes")
    guardar("instituicoes.csv", instituicoes)
    lotka = indicadores.lei_de_lotka(corpus)
    guardar("lotka.csv", lotka["tabela"])
    bradford = indicadores.lei_de_bradford(corpus)
    guardar("bradford.csv", bradford["tabela"])
    price = indicadores.indice_de_price(corpus)
    guardar("price.csv", price["detalhe"])
    imp = indicadores.impacto(corpus, ano_corte)
    guardar("mais_citados.csv", imp["mais_citados"])
    col = indicadores.colaboracao(corpus)
    guardar("colaboracao_paises.csv", col["por_pais"])

    parcial = _ler_parcial(saida)
    parcial.update({
        "revisao": {"slug": revisao.slug, "titulo": revisao.config.get("titulo"),
                    "tema": revisao.config.get("tema")},
        "n_corpus": len(corpus),
        "ano_corte": ano_corte,
        "semente": _semente(revisao, args),
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
        "arquivos": sorted(set(list(parcial.get("arquivos", [])) + arquivos)),
    })
    _guardar_parcial(saida, parcial)
    print("Indicadores gerados em %s (%d registros, corte %d)."
          % (os.path.relpath(saida), len(corpus), ano_corte))
    registrar_execucao(revisao.dir_saidas, "indicadores",
                       "revisao=%s n=%d ano_corte=%d" % (revisao.slug, len(corpus), ano_corte))
    return 0


def cmd_redes(args):
    revisao = _revisao(args)
    corpus = carregar_corpus(revisao.corpus)
    if not corpus:
        print("Corpus vazio: rode 'importar' antes.")
        return 1
    saida = args.saida or revisao.dir_saidas
    os.makedirs(saida, exist_ok=True)
    semente = _semente(revisao, args)
    campo_termos = revisao.config.get("campo_termos", "palavras_chave")
    limite_nos = revisao.limiar("limite_nos")
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

    nos_cp, arestas_cp = redes.rede_copalavras(
        corpus, campo=campo_termos, minimo=_limiar(revisao, args, "min_termo", "min_termo"),
        limite_nos=limite_nos)
    grupos_cp = redes.propagacao_de_rotulos(nos_cp, arestas_cp, semente=semente)
    metricas_cp = exportar("copalavras", nos_cp, arestas_cp, grupos_cp)
    mapa = redes.mapa_tematico(nos_cp, arestas_cp, grupos_cp)
    salvar_tabela(os.path.join(saida, "mapa_tematico.csv"), mapa)
    periodos, fluxos = redes.evolucao_tematica(corpus, cortes=revisao.periodos(), campo=campo_termos)
    salvar_tabela(os.path.join(saida, "evolucao_tematica.csv"), fluxos)

    nos_ca, arestas_ca = redes.rede_coautoria(
        corpus, "autores", minimo=_limiar(revisao, args, "min_autor", "min_autor"),
        limite_nos=limite_nos)
    metricas_ca = exportar("coautoria", nos_ca, arestas_ca,
                           redes.propagacao_de_rotulos(nos_ca, arestas_ca, semente=semente))
    nos_in, arestas_in = redes.rede_coautoria(corpus, "instituicoes", minimo=2, limite_nos=limite_nos)
    metricas_in = exportar("instituicoes", nos_in, arestas_in)
    nos_pa, arestas_pa = redes.rede_coautoria(corpus, "paises", minimo=1, limite_nos=limite_nos)
    metricas_pa = exportar("paises", nos_pa, arestas_pa)

    nos_cc, arestas_cc, cobertura = redes.rede_cocitacao(
        corpus, minimo=_limiar(revisao, args, "min_cocitacao", "min_cocitacao"),
        limite_nos=limite_nos)
    grupos_cc = redes.propagacao_de_rotulos(nos_cc, arestas_cc, semente=semente)
    metricas_cc = exportar("cocitacao", nos_cc, arestas_cc, grupos_cc)
    nos_ac, arestas_ac = redes.acoplamento_bibliografico(
        corpus, minimo=_limiar(revisao, args, "min_acoplamento", "min_acoplamento"),
        limite_nos=limite_nos)
    metricas_ac = exportar("acoplamento", nos_ac, arestas_ac)

    parcial.update({
        "copalavras": {"metricas": metricas_cp, "mapa": mapa, "periodos": periodos,
                       "fluxos": fluxos, "top": _topo(nos_cp, grupos_cp),
                       "agrupamentos": len(mapa), "quadrantes": _quadrantes(mapa)},
        "coautoria": {"metricas": metricas_ca},
        "instituicoes_rede": {"metricas": metricas_in},
        "paises_rede": {"metricas": metricas_pa},
        "cocitacao": dict(cobertura, metricas=metricas_cc, top=_topo(nos_cc, grupos_cc)),
        "acoplamento": {"metricas": metricas_ac},
        "arquivos": sorted(set(arquivos)),
        "n_corpus": len(corpus),
        "semente": semente,
    })
    _guardar_parcial(saida, parcial)
    print("Redes geradas em %s." % os.path.relpath(saida))
    registrar_execucao(revisao.dir_saidas, "redes",
                       "revisao=%s n=%d seed=%d" % (revisao.slug, len(corpus), semente))
    return 0


def cmd_relatorio(args):
    revisao = _revisao(args)
    saida = args.saida or revisao.dir_saidas
    resultados = _ler_parcial(saida)
    if not resultados:
        print("Nada a relatar: execute 'indicadores' e 'redes' antes.")
        return 1
    resultados["proposicoes"] = proposicoes.avaliar(
        revisao.config.get("proposicoes"), resultados)
    resultados["revisao"] = {
        "slug": revisao.slug,
        "titulo": revisao.config.get("titulo"),
        "tema": revisao.config.get("tema"),
    }
    caminho = relatorio.montar(resultados, saida, revisao.execucao())
    print("Relatório → %s" % os.path.relpath(caminho))
    registrar_execucao(revisao.dir_saidas, "relatorio", caminho)
    return 0


def cmd_prisma(args):
    revisao = _revisao(args)
    saida = args.saida or revisao.dir_saidas
    brutos = carregar_corpus(revisao.corpus_bruto) if os.path.exists(revisao.corpus_bruto) else []
    estatisticas = {}
    dedup_json = os.path.join(revisao.dir_processado, "dedup.json")
    if os.path.exists(dedup_json):
        with open(dedup_json, encoding="utf-8") as fh:
            estatisticas = json.load(fh)
    caminho_triagem = args.triagem or revisao.triagem
    linhas = triagem.ler_triagem(caminho_triagem) if os.path.exists(caminho_triagem) else None
    if not brutos:
        brutos = carregar_corpus(revisao.corpus)
        estatisticas.setdefault("saida", len(brutos))
    fluxo = triagem.contagens_prisma(brutos, estatisticas, linhas,
                                     codigos=revisao.config.get("codigos_exclusao"))
    os.makedirs(saida, exist_ok=True)
    with open(os.path.join(saida, "prisma.json"), "w", encoding="utf-8") as fh:
        json.dump(fluxo, fh, ensure_ascii=False, indent=2)
    diagrama = triagem.diagrama_prisma(fluxo)
    with open(os.path.join(saida, "prisma.md"), "w", encoding="utf-8") as fh:
        fh.write("# Fluxo PRISMA — %s\n\n%s\n" % (revisao.config.get("titulo", revisao.slug), diagrama))
    print(diagrama)
    registrar_execucao(revisao.dir_saidas, "prisma", json.dumps(
        {k: v for k, v in fluxo.items() if not isinstance(v, dict)}))
    return 0


def cmd_analise(args):
    for funcao in (cmd_importar, cmd_dedup):
        codigo = funcao(args)
        if codigo:
            return codigo
    cmd_indicadores(args)
    cmd_redes(args)
    cmd_prisma(args)
    return cmd_relatorio(args)


# --------------------------------------------------------------------------- auxiliares

def _quadrantes(mapa):
    """Conta os agrupamentos por quadrante do mapa temático (referenciável nas proposições)."""
    contagem = {}
    for linha in mapa:
        quadrante = linha.get("quadrante", "indefinido")
        contagem[quadrante] = contagem.get(quadrante, 0) + 1
    return contagem


def _topo(nos, grupos, limite=30):
    return [{"item": no, "frequencia": freq, "agrupamento": grupos.get(no, "")}
            for no, freq in sorted(nos.items(), key=lambda kv: -kv[1])[:limite]]


def _guardar_parcial(saida, dados):
    os.makedirs(saida, exist_ok=True)
    with open(os.path.join(saida, "resultados.json"), "w", encoding="utf-8") as fh:
        json.dump(relatorio._limpar(dados), fh, ensure_ascii=False, indent=2)


def _ler_parcial(saida):
    caminho = os.path.join(saida, "resultados.json")
    if not os.path.exists(caminho):
        return {}
    with open(caminho, encoding="utf-8") as fh:
        return json.load(fh)


def principal(argv=None):
    p = argparse.ArgumentParser(
        prog="cienciometria",
        description="Motor de revisões cienciométricas: um pipeline, muitas revisões",
    )
    p.add_argument("--version", action="version", version="cienciometria %s" % __version__)
    sub = p.add_subparsers(dest="comando", required=True)

    nova = sub.add_parser("nova", help="cria uma revisão a partir do esqueleto")
    nova.add_argument("slug", help="identificador da revisão (ex.: capacidade-estatal-municipal)")
    nova.add_argument("--titulo", default="")
    nova.add_argument("--tema", default="")
    nova.add_argument("--base-revisoes", default=None,
                      help="pasta onde criar a revisão (padrão: ./revisoes)")
    nova.set_defaults(funcao=cmd_nova)

    lst = sub.add_parser("listar", help="lista as revisões existentes")
    lst.set_defaults(funcao=cmd_listar)

    ajuda = {
        "estado": "mostra em que etapa a pesquisa está e qual é o próximo passo",
        "fichar": "cria fichas de leitura (ou sugere quais artigos fichar)",
        "fichamentos": "consolida as fichas e confronta as lacunas com o corpus",
        "artigo": "monta o rascunho do artigo com os números da análise",
        "coletar": "baixa registros de fontes abertas (OpenAlex, Crossref)",
        "comparar": "mede o que mudou entre duas exportações de busca",
        "importar": "lê as exportações e monta o corpus",
        "dedup": "deduplica e separa os pares ambíguos para conferência humana",
        "triagem": "gera a planilha cega de triagem",
        "kappa": "calcula a concordância entre revisores",
        "indicadores": "produção, Lotka, Bradford, Price, impacto, colaboração",
        "redes": "co-citação, acoplamento, coautoria, co-palavras e mapa temático",
        "prisma": "contagens e diagrama do fluxo PRISMA",
        "relatorio": "monta o relatório em Markdown",
        "analise": "importar → dedup → indicadores → redes → prisma → relatorio",
    }
    funcoes = {
        "estado": cmd_estado,
        "fichar": cmd_fichar,
        "fichamentos": cmd_fichamentos,
        "artigo": cmd_artigo,
        "coletar": cmd_coletar,
        "comparar": cmd_comparar,
        "importar": cmd_importar, "dedup": cmd_dedup, "triagem": cmd_triagem, "kappa": cmd_kappa,
        "indicadores": cmd_indicadores, "redes": cmd_redes, "prisma": cmd_prisma,
        "relatorio": cmd_relatorio, "analise": cmd_analise,
    }
    for nome, funcao in funcoes.items():
        sp = sub.add_parser(nome, help=ajuda[nome])
        sp.add_argument("--revisao", required=True, help="slug da revisão (ver 'listar')")
        sp.add_argument("--entrada", default=None, help="pasta das exportações (padrão: dados/bruto da revisão)")
        sp.add_argument("--saida", default=None, help="pasta de saída (padrão: saidas/ da revisão)")
        sp.add_argument("--triagem", default=None, help="planilha de triagem preenchida")
        sp.add_argument("--base-revisoes", default=None, help="pasta que contém as revisões")
        sp.add_argument("--seed", type=int, default=None, help="semente (padrão: a da revisão)")
        for limiar in ("min-termo", "min-autor", "min-cocitacao", "min-acoplamento"):
            sp.add_argument("--" + limiar, type=int, default=None,
                            help="sobrepõe o limiar declarado na revisão")
        if nome == "estado":
            sp.add_argument("--json", action="store_true", help="também imprime o estado em JSON")
        if nome == "fichar":
            sp.add_argument("--id", action="append", help="id do registro no corpus (repetível)")
            sp.add_argument("--sugerir", action="store_true",
                            help="propõe quais artigos fichar, com o critério de cada escolha")
            sp.add_argument("--sugeridas", action="store_true",
                            help="cria fichas para toda a lista sugerida")
            sp.add_argument("--quantidade", type=int, default=fichamento.MINIMO_SUGERIDO)
        if nome == "comparar":
            sp.add_argument("--antes", default=None, help="exportação da busca anterior")
            sp.add_argument("--depois", default=None, help="exportação da busca alterada")
        if nome == "coletar":
            sp.add_argument("--fonte", choices=("openalex", "crossref"), default="openalex")
            sp.add_argument("--busca", default=None, help="termos da consulta (título e resumo)")
            sp.add_argument("--de", type=int, default=None, help="ano inicial (padrão: o da revisão)")
            sp.add_argument("--ate", type=int, default=None, help="ano final (padrão: o da revisão)")
            sp.add_argument("--email", default=None,
                            help="e-mail de contato: as duas APIs pedem, e dá acesso à fila rápida")
            sp.add_argument("--limite", type=int, default=5000, help="teto de registros")
            sp.add_argument("--filtro-extra", default=None,
                            help="filtro adicional do OpenAlex, ex.: 'is_oa:true'")
        sp.set_defaults(funcao=funcao)

    args = p.parse_args(argv)
    return args.funcao(args)


if __name__ == "__main__":
    sys.exit(principal())
