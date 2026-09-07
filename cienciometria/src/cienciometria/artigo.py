"""Rascunho do artigo cienciométrico, com os números vindos da análise.

A estrutura segue o formato consolidado de artigo cienciométrico: introdução em
funil, material e métodos com o fluxo PRISMA, resultados divididos por tipo de
análise (temporal e autoria, periódicos, estrutura e parcerias, citação, países),
discussão, conclusão.

O gerador preenche o que é fato do corpus e marca o que exige escrita humana.
Duas marcações aparecem no rascunho e não podem sobrar na versão final:

    [ESCREVER: ...]   o que depende de interpretação, leitura ou decisão do autor
    [SEM DADO: ...]   o que o pipeline não produziu — nunca preencha de memória

Números só entram aqui vindos de saidas/resultados.json. Nada é estimado.
"""

import json
import os


def _n(valor, sufixo="", casas=None):
    if valor is None or valor == "":
        return "[SEM DADO]"
    if casas is not None:
        try:
            return ("%%.%df%s" % (casas, sufixo)) % float(valor)
        except (TypeError, ValueError):
            return str(valor) + sufixo
    return "%s%s" % (valor, sufixo)


def _tabela(linhas, colunas, rotulos=None, limite=10):
    if not linhas:
        return "[SEM DADO: tabela não gerada pela análise]\n"
    rotulos = rotulos or colunas
    saida = ["| " + " | ".join(rotulos) + " |", "|" + "|".join("---" for _ in colunas) + "|"]
    for linha in linhas[:limite]:
        saida.append("| " + " | ".join(str(linha.get(c, "")) for c in colunas) + " |")
    return "\n".join(saida) + "\n"


def montar(revisao, resultados, prisma=None, lacunas=None, fichas=None):
    """Devolve o rascunho do artigo em Markdown."""
    config = revisao.config
    execucao = revisao.execucao()
    r = resultados or {}
    prod = r.get("producao_anual") or []
    imp = r.get("impacto") or {}
    col = r.get("colaboracao") or {}
    lotka = r.get("lotka") or {}
    brad = r.get("bradford") or {}
    price = r.get("price") or {}
    cop = r.get("copalavras") or {}
    cocit = r.get("cocitacao") or {}
    coaut = (r.get("coautoria") or {}).get("metricas") or {}
    tema = config.get("tema") or "[ESCREVER: tema]"
    corte = execucao.get("data_de_corte") or "[SEM DADO: data de corte não declarada]"
    n = r.get("n_corpus")

    p = []
    a = p.append

    a("# %s\n" % (config.get("titulo") or "[ESCREVER: título conciso e informativo]"))
    a("[ESCREVER: autores, afiliações, autor para correspondência]\n")
    a("> Rascunho gerado por `cienciometria artigo` em %s, a partir de `saidas/resultados.json`. "
      "Cada `[ESCREVER: ...]` exige a sua escrita; cada `[SEM DADO: ...]` significa que a análise "
      "não produziu aquele valor — reexecute a etapa correspondente em vez de preencher de "
      "memória.\n" % corte)

    # ------------------------------------------------------------------ resumos
    a("## Resumo\n")
    a("**Objetivo.** [ESCREVER: uma frase com o objetivo, retomando o problema.]\n")
    a("**Métodos.** A análise cienciométrica cobriu %s registros recuperados em %s, com data de "
      "corte em %s, no período de %s a %s. [ESCREVER: bases, strings e critérios em uma frase.]\n"
      % (_n(n), ", ".join(config.get("bases") or []) or "[SEM DADO: bases]", corte,
         prod[0]["ano"] if prod else "[SEM DADO]", prod[-1]["ano"] if prod else "[SEM DADO]"))
    a("**Resultados.** [ESCREVER: dois a três achados centrais, com os números das seções 3.x.]\n")
    a("**Conclusão.** [ESCREVER: o que os achados significam e a lacuna que sustentam.]\n")
    a("**Palavras-chave:** [ESCREVER: cinco termos, evitando repetir os do título].\n")
    a("## Abstract\n\n[ESCREVER: versão em inglês do resumo, na mesma estrutura.]\n")

    # ------------------------------------------------------------------ introdução
    a("## 1 Introdução\n")
    a("[ESCREVER — parágrafo 1: o tema e por que ele importa, com citações.]\n")
    a("[ESCREVER — parágrafo 2: o que já se sabe, apoiado nos artigos fichados.]\n")
    if lacunas:
        a("[ESCREVER — parágrafo 3: o que falta. As lacunas declaradas pelos próprios autores do "
          "campo, extraídas do fichamento, estão abaixo — escolha as que a sua pesquisa enfrenta e "
          "escreva em prosa, sem colar a tabela.]\n")
        a(_tabela(lacunas, ["ficha", "ano", "lacuna_declarada", "ocorrencias_no_corpus"],
                  ["Ficha", "Ano", "Lacuna declarada pelos autores", "Ocorrência no corpus"],
                  limite=12))
        a("> Confira antes de usar: lacuna cujo termo já aparece em boa parte do corpus foi "
          "preenchida depois daquela publicação, e usá-la como se estivesse aberta é o erro que o "
          "parecerista encontra primeiro.\n")
    else:
        a("[SEM DADO: nenhuma lacuna consolidada. Ficha os artigos-núcleo antes de escrever esta "
          "seção — é dela que sai a justificativa da pesquisa.]\n")
    a("[ESCREVER — parágrafo 4: revisões e estudos cienciométricos anteriores sobre o tema, e o "
      "que este estudo faz de diferente.]\n")
    a("[ESCREVER — parágrafo 5: objetivo e perguntas de pesquisa, na ordem em que a discussão vai "
      "respondê-las.]\n")

    # ------------------------------------------------------------------ métodos
    a("## 2 Material e Métodos\n")
    a("### 2.1 Busca e seleção\n")
    execucoes = execucao.get("execucoes") or []
    if any(e.get("resultados") for e in execucoes):
        a(_tabela([{"base": e.get("base", ""), "data": e.get("data", ""),
                    "filtros": (e.get("filtros") or "")[:60],
                    "resultados": e.get("resultados", "")} for e in execucoes if e.get("resultados")],
                  ["base", "data", "filtros", "resultados"],
                  ["Base", "Data", "Filtros", "Registros"], limite=20))
    else:
        a("[SEM DADO: nenhuma execução de busca registrada em config/execucao.json]\n")
    a("As strings completas estão em `docs/03-estrategias-de-busca.md` e devem ser reproduzidas no "
      "apêndice ou no material suplementar. [ESCREVER: critérios de inclusão e exclusão em prosa, "
      "a partir do protocolo.]\n")
    if prisma:
        a("\n**Figura 1 — Fluxo de identificação e seleção (PRISMA 2020).** Fonte: `saidas/prisma.md`.\n")
        a("```\n%s\n```\n" % _prisma_texto(prisma))
    else:
        a("[SEM DADO: fluxo PRISMA não gerado — rode `cienciometria prisma`]\n")
    a("### 2.2 Análises cienciométricas\n")
    a("Foram calculadas: produção anual e taxa de crescimento; produtividade de autores pela Lei de "
      "Lotka, com teste de Kolmogorov-Smirnov; dispersão por fontes pela Lei de Bradford; índice de "
      "Price e meia-vida citada; impacto por citações e h-index; índice de colaboração e coautoria "
      "internacional; e as redes de co-citação de referências, acoplamento bibliográfico, coautoria "
      "entre autores, instituições e países, e coocorrência de palavras-chave, com agrupamento por "
      "propagação de rótulos (semente %s) e mapa temático de centralidade e densidade.\n"
      % _n(r.get("semente")))
    a("[ESCREVER: cite aqui o software e a versão usados, e declare a semente e os limiares — sem "
      "isso a análise não é reproduzível.]\n")

    # ------------------------------------------------------------------ resultados
    a("## 3 Resultados\n")
    a("### 3.1 Tendências temporais e autoria\n")
    if prod:
        a("A busca resultou em %s registros publicados entre %s e %s. A taxa de crescimento anual "
          "composta foi de %s%%. [ESCREVER: descreva o formato da série — em que ano a produção "
          "cresce, se há inflexão, e a que ela pode corresponder; a explicação vai na discussão.]\n"
          % (_n(n), prod[0]["ano"], prod[-1]["ano"], _n(r.get("tcac"))))
        a("\n**Figura 2 — Produção anual.** Dados em `saidas/producao_anual.csv`.\n")
    else:
        a("[SEM DADO: série anual não gerada]\n")
    a("\nO conjunto reúne %s autores distintos, com %s autores por trabalho e índice de "
      "colaboração de %s; %s%% dos trabalhos são de autoria única e %s%% têm coautoria "
      "internacional.\n"
      % (_n(lotka.get("n_autores")), _n(col.get("autores_por_trabalho")),
         _n(col.get("indice_colaboracao")), _n(col.get("trabalhos_com_um_autor_%")),
         _n(col.get("coautoria_internacional_%"))))
    if lotka.get("alpha") is not None:
        if lotka["alpha"] <= 0:
            a("[SEM DADO: o expoente estimado (α = %s) não é positivo, de modo que a distribuição "
              "observada não tem a forma da Lei de Lotka. Verifique a desambiguação de autores "
              "antes de escrever esta passagem.]\n" % _n(lotka.get("alpha")))
        else:
            a("A distribuição de produtividade ajusta-se a uma lei de potência com expoente α = %s "
              "(KS = %s; crítico a 5%% = %s), o que %s a Lei de Lotka.\n"
              % (_n(lotka.get("alpha")), _n(lotka.get("ks")), _n(lotka.get("ks_critico_5%")),
                 "sustenta" if lotka.get("adere") else "não sustenta"))
    a("\n**Tabela 1 — Autores mais produtivos.**\n")
    a(_tabela(r.get("autores") or [], ["item", "publicacoes", "publicacoes_fracionarias"],
              ["Autor", "Publicações", "Contagem fracionária"]))

    a("### 3.2 Periódicos\n")
    zonas = brad.get("zonas") or []
    if zonas:
        a("A dispersão por fontes segue o padrão de Bradford: a zona 1 reúne %s periódicos e %s%% "
          "dos artigos; o multiplicador médio entre zonas é %s.\n"
          % (_n(zonas[0].get("fontes")), _n(zonas[0].get("artigos_%")), _n(brad.get("multiplicador"))))
    a("\n**Tabela 2 — Periódicos da zona 1.**\n")
    a(_tabela([l for l in (brad.get("tabela") or []) if l.get("zona") == 1],
              ["fonte", "artigos", "acumulado"], ["Periódico", "Artigos", "Acumulado"]))

    a("### 3.3 Estrutura do campo e parcerias\n")
    a("A rede de coocorrência de palavras-chave reúne %s nós e %s ligações (densidade %s), "
      "distribuídos em %s agrupamentos. A rede de coautoria tem %s nós em %s componentes, com o "
      "maior deles cobrindo %s%% dos autores.\n"
      % (_n((cop.get("metricas") or {}).get("nos")), _n((cop.get("metricas") or {}).get("arestas")),
         _n((cop.get("metricas") or {}).get("densidade")), _n(cop.get("agrupamentos")),
         _n(coaut.get("nos")), _n(coaut.get("componentes")),
         _n(coaut.get("componente_gigante_%"))))
    a("\n**Tabela 3 — Mapa temático (centralidade e densidade de Callon).**\n")
    a(_tabela(cop.get("mapa") or [],
              ["agrupamento", "itens", "centralidade", "densidade", "quadrante",
               "termos_representativos"],
              ["Agrupamento", "Itens", "Centralidade", "Densidade", "Quadrante", "Termos"]))
    a("[ESCREVER: rotule cada agrupamento depois de ler os dez itens mais centrais — o rótulo "
      "automático acima é provisório. Antes de chamar algum de emergente, confira o ano médio do "
      "agrupamento e a série por subperíodo.]\n")

    a("### 3.4 Padrões de citação\n")
    a("O corpus acumula %s citações, média de %s por trabalho, com h-index de %s; %s%% dos "
      "trabalhos não receberam citação. O índice de Price é de %s%% e a meia-vida citada, de %s "
      "anos (cobertura de %s%% do corpus com referências).\n"
      % (_n(imp.get("citacoes_totais")), _n(imp.get("media_por_trabalho")), _n(imp.get("h_index")),
         _n(imp.get("sem_citacao_%")), _n(price.get("indice_price_corpus")),
         _n(price.get("meia_vida_citada")), _n(price.get("cobertura_%"))))
    a("\n**Tabela 4 — Trabalhos mais citados.**\n")
    a(_tabela(imp.get("mais_citados") or [],
              ["autores", "ano", "titulo", "fonte", "citacoes", "citacoes_por_ano"],
              ["Autores", "Ano", "Título", "Periódico", "Citações", "Citações/ano"]))
    # a cobertura do subcorpus com referências qualifica tudo o que se afirmar sobre a
    # estrutura intelectual, e por isso é relatada mesmo quando a tabela sai vazia
    a("\nA análise de co-citação apoia-se no subcorpus com campo de referências, que cobre %s%% "
      "dos registros.\n" % _n(cocit.get("cobertura_%")))
    if cocit.get("top"):
        a("\n**Tabela 5 — Referências mais co-citadas** (base intelectual do campo).\n")
        a(_tabela(cocit["top"], ["item", "frequencia", "agrupamento"],
                  ["Referência", "Co-citações", "Agrupamento"]))
    else:
        a("[SEM DADO: rede de co-citação não gerada ou sem referências suficientes]\n")

    a("### 3.5 Países e colaboração\n")
    a(_tabela(col.get("por_pais") or [], ["pais", "total", "scp", "mcp", "mcp_%"],
              ["País", "Total", "SCP", "MCP", "MCP %"]))

    # ------------------------------------------------------------------ discussão
    a("## 4 Discussão\n")
    a("[ESCREVER — parágrafo 1: retome o objetivo e diga o que os resultados significam.]\n")
    a("[ESCREVER — um parágrafo por pergunta de pesquisa, na ordem da introdução.]\n")
    if fichas:
        a("Compare com o que os artigos fichados afirmam. Fichas disponíveis: %s.\n"
          % ", ".join(f["arquivo"] for f in fichas[:12]))
    a("[ESCREVER: limitações — cobertura das bases, campos incompletos, homonímia de autores, "
      "limiares adotados. Toda revisão tem; a que não declara nenhuma é a menos confiável.]\n")
    props = r.get("proposicoes") or []
    if props:
        a("\n**Verificação das proposições declaradas antes da análise.**\n")
        a(_tabela(props, ["proposicao", "valor", "situacao"],
                  ["Proposição", "Indicador", "Situação"], limite=12))
        a("[ESCREVER: discuta o que foi refutado. Refutação relatada é sinal de desenho honesto.]\n")

    a("## 5 Conclusão\n")
    a("[ESCREVER: retome o objetivo, diga o que foi encontrado e qual lacuna a pesquisa seguinte "
      "enfrenta — esta é a ponte para o seu projeto.]\n")

    a("## Referências\n")
    a("[ESCREVER: monte a lista a partir do corpus e das fichas; confira cada entrada no registro "
      "da base. Inclua as fontes de método efetivamente usadas.]\n")
    a("## Apêndice A — Corpus analisado\n")
    a("Tabela completa dos registros incluídos: `dados/processado/corpus.csv`.\n")
    a("## Declarações\n")
    a("[ESCREVER: contribuições dos autores, financiamento, conflito de interesse, "
      "disponibilidade de dados.]\n")
    return "\n".join(p)


def _prisma_texto(prisma):
    if isinstance(prisma, str):
        return prisma
    linhas = []
    for chave, valor in (prisma or {}).items():
        if isinstance(valor, dict):
            continue
        linhas.append("%-38s %s" % (chave.replace("_", " "), valor))
    return "\n".join(linhas)


def salvar(caminho, texto):
    os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(texto)
    return caminho


def pendencias(texto):
    """Conta o que ainda falta no rascunho, para o relatório não sair pela metade."""
    return {
        "escrever": texto.count("[ESCREVER:"),
        "sem_dado": texto.count("[SEM DADO"),
    }
