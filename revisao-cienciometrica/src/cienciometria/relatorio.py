"""Montagem do relatório cienciométrico em Markdown."""

import datetime
import json
import os


def _tabela(linhas, colunas, limite=20):
    if not linhas:
        return "_sem dados_\n"
    saida = ["| " + " | ".join(colunas) + " |",
             "|" + "|".join("---" for _ in colunas) + "|"]
    for linha in linhas[:limite]:
        saida.append("| " + " | ".join(str(linha.get(c, "")) for c in colunas) + " |")
    return "\n".join(saida) + "\n"


def montar(resultados, dir_saida, dados_execucao=None):
    r = resultados
    corte = r.get("ano_corte")
    partes = []
    add = partes.append

    add("# Relatório cienciométrico — federalismo fiscal dos entes subnacionais\n")
    add("**Gerado em:** %s  " % datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
    add("**Data de corte declarada:** %s  " % (
        (dados_execucao or {}).get("data_de_corte") or "NÃO DECLARADA — preencher config/execucao.json"))
    add("**Semente:** %s  " % r.get("semente"))
    add("**Registros no corpus:** %d\n" % r["n_corpus"])
    add("> Números deste relatório são gerados por `python -m cienciometria`. "
        "Nenhum valor é digitado à mão. A rastreabilidade de cada saída está em `saidas/execucao.log`.\n")

    add("## 1 Desempenho\n")
    prod = r.get("producao_anual", [])
    if prod:
        add("**Janela observada:** %d–%d. **TCAC:** %s%%.\n" % (
            prod[0]["ano"], prod[-1]["ano"],
            r.get("tcac") if r.get("tcac") is not None else "não calculável"))
        add("### 1.1 Produção anual\n")
        add(_tabela(prod, ["ano", "publicacoes", "acumulado", "citacoes",
                           "citacoes_por_publicacao"], limite=60))

    imp = r.get("impacto", {})
    add("### 1.2 Impacto\n")
    add("- Citações totais: **%s**\n- Média por trabalho: **%s**\n- Trabalhos sem citação: **%s%%**\n"
        "- h-index do corpus: **%s**\n" % (
            imp.get("citacoes_totais"), imp.get("media_por_trabalho"),
            imp.get("sem_citacao_%"), imp.get("h_index")))
    add("\n**Trabalhos mais citados**\n")
    add(_tabela(imp.get("mais_citados", []),
                ["autores", "ano", "titulo", "fonte", "citacoes", "citacoes_por_ano"], limite=25))

    add("### 1.3 Fontes e Lei de Bradford\n")
    brad = r.get("bradford", {})
    add(_tabela(brad.get("zonas", []), ["zona", "fontes", "artigos", "artigos_%"]))
    add("\nMultiplicador médio entre zonas: **%s** (padrão de Bradford: aproximadamente constante).\n"
        % brad.get("multiplicador"))
    add("\n**Fontes da zona 1**\n")
    add(_tabela([l for l in brad.get("tabela", []) if l["zona"] == 1],
                ["posicao", "fonte", "artigos", "acumulado"], limite=25))

    add("### 1.4 Autores e Lei de Lotka\n")
    lotka = r.get("lotka", {})
    if lotka.get("alpha") is not None and lotka["alpha"] <= 0:
        add("> **Alerta:** expoente α não positivo. A distribuição observada não tem a forma de lei "
            "de potência decrescente — verificar desambiguação de autores antes de interpretar.\n")
    add("- Autores distintos: **%s**\n- Expoente α estimado: **%s**\n- Constante C: **%s**\n"
        "- KS = %s (crítico a 5%% = %s) → **%s**\n" % (
            lotka.get("n_autores"), lotka.get("alpha"), lotka.get("c"), lotka.get("ks"),
            lotka.get("ks_critico_5%"),
            "adere à Lei de Lotka" if lotka.get("adere") else "não adere à Lei de Lotka"))
    add(_tabela(lotka.get("tabela", []),
                ["trabalhos_por_autor", "autores_observado", "autores_esperado",
                 "proporcao_observada", "proporcao_esperada"], limite=12))
    add("\n**Autores mais produtivos**\n")
    add(_tabela(r.get("autores", []),
                ["item", "publicacoes", "publicacoes_fracionarias", "participacao_%"], limite=20))

    add("### 1.5 Colaboração\n")
    col = r.get("colaboracao", {})
    add("- Autores por trabalho: **%s**\n- Índice de colaboração: **%s**\n"
        "- Trabalhos de autor único: **%s%%**\n- Coautoria internacional: **%s%%**\n"
        "- SCP: %s | MCP: %s\n" % (
            col.get("autores_por_trabalho"), col.get("indice_colaboracao"),
            col.get("trabalhos_com_um_autor_%"), col.get("coautoria_internacional_%"),
            col.get("scp"), col.get("mcp")))
    add(_tabela(col.get("por_pais", []), ["pais", "total", "scp", "mcp", "mcp_%"], limite=25))

    add("### 1.6 Obsolescência (índice de Price)\n")
    price = r.get("price", {})
    add("- Índice de Price do corpus: **%s%%** das referências com até 5 anos\n"
        "- Meia-vida citada (mediana): **%s anos**\n"
        "- Cobertura: %s%% dos registros têm campo de referências (%s referências datadas)\n" % (
            price.get("indice_price_corpus"), price.get("meia_vida_citada"),
            price.get("cobertura_%"), price.get("referencias_datadas")))

    add("\n## 2 Estrutura intelectual\n")
    cocit = r.get("cocitacao", {})
    add("Co-citação de referências — cobertura do subcorpus: **%s%%** (%s documentos).\n" % (
        cocit.get("cobertura_%"), cocit.get("documentos_com_referencias")))
    add(_metricas(cocit.get("metricas", {})))
    add("\n**Referências mais co-citadas**\n")
    add(_tabela(cocit.get("top", []), ["item", "frequencia", "agrupamento"], limite=25))
    acop = r.get("acoplamento", {})
    add("\nAcoplamento bibliográfico:\n")
    add(_metricas(acop.get("metricas", {})))

    add("\n## 3 Estrutura social\n")
    for nome, chave in (("Coautoria (autores)", "coautoria"),
                        ("Colaboração institucional", "instituicoes_rede"),
                        ("Colaboração entre países", "paises_rede")):
        rede = r.get(chave, {})
        if rede:
            add("\n### %s\n" % nome)
            add(_metricas(rede.get("metricas", {})))

    add("\n## 4 Estrutura conceitual\n")
    cop = r.get("copalavras", {})
    add(_metricas(cop.get("metricas", {})))
    add("\n**Mapa temático (Callon)**\n")
    add(_tabela(cop.get("mapa", []),
                ["agrupamento", "itens", "centralidade", "densidade", "quadrante",
                 "termos_representativos"], limite=20))
    add("\n> Os rótulos dos agrupamentos são provisórios e automáticos. Conforme o plano de análise, "
        "só entram no texto final após leitura dos 10 itens de maior força de ligação de cada um.\n")
    add("\n**Evolução temática por subperíodo**\n")
    for periodo in cop.get("periodos", []):
        add("\n- **%s** (%d documentos): %s" % (
            periodo["periodo"], periodo["documentos"],
            "; ".join("%s (%d)" % (t, n) for t, n in periodo["termos"][:10]) or "_sem termos_"))
    add("\n\n**Fluxo entre subperíodos**\n")
    add(_tabela(cop.get("fluxos", []),
                ["de", "para", "termos_mantidos", "indice_inclusao", "novos", "abandonados"]))

    add("\n## 5 Verificação das proposições\n")
    add(_tabela(r.get("proposicoes", []), ["proposicao", "indicador", "valor", "situacao"]))
    add("\n> A situação é atribuída automaticamente pelos critérios do plano de análise, §6. "
        "Ela é insumo para a interpretação — não a substitui.\n")

    add("\n## 6 Arquivos gerados\n")
    for arquivo in sorted(r.get("arquivos", [])):
        add("- `%s`" % arquivo)
    add("")

    texto = "\n".join(partes)
    os.makedirs(dir_saida, exist_ok=True)
    caminho = os.path.join(dir_saida, "relatorio.md")
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write(texto)
    with open(os.path.join(dir_saida, "resultados.json"), "w", encoding="utf-8") as fh:
        json.dump(_limpar(r), fh, ensure_ascii=False, indent=2)
    return caminho


def _metricas(m):
    if not m:
        return "_rede não gerada (dados insuficientes)_\n"
    return ("- Nós: **%s** | Arestas: **%s** | Densidade: **%s**\n"
            "- Componentes: **%s** | Componente gigante: **%s** (%s%% dos nós)\n"
            "- Grau médio ponderado: **%s**\n" % (
                m.get("nos"), m.get("arestas"), m.get("densidade"), m.get("componentes"),
                m.get("componente_gigante"), m.get("componente_gigante_%"),
                m.get("grau_medio_ponderado")))


def _limpar(obj):
    """Converte estruturas não serializáveis (tuplas em chaves, sets) para JSON."""
    if isinstance(obj, dict):
        return {str(k): _limpar(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_limpar(v) for v in obj]
    if isinstance(obj, set):
        return sorted(str(v) for v in obj)
    return obj
