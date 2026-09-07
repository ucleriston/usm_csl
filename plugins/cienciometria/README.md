# Plugin Cienciometria

Conduz revisões cienciométricas (bibliométricas) de ponta a ponta, com o motor de análise
embarcado: **não precisa de R, bibliometrix, VOSviewer nem de qualquer biblioteca Python externa.**
Só Python 3.9+.

## Instalação

```
/plugin marketplace add ucleriston/usm_csl
/plugin install cienciometria@usm-csl
```

## O que ele ativa

**Skills** (disparam sozinhas quando o assunto aparece):

| Skill | Cobre |
|---|---|
| `revisao-cienciometrica` | O fluxo inteiro: recorte, protocolo, busca, corpus, triagem, análise, interpretação |
| `estrategia-de-busca` | Strings por base, sinonímia, truncamento, teste de recall, exportação |
| `triagem-e-prisma` | Critérios, códigos de exclusão, triagem dupla cega, kappa, fluxo PRISMA |
| `interpretar-resultados` | O que cada indicador sustenta, rótulos de agrupamento, mapa temático, redação dos resultados |

**Comandos:**

| Comando | Faz |
|---|---|
| `/nova-revisao <tema>` | Conduz a delimitação e cria a revisão configurada |
| `/analisar-corpus <slug>` | Roda o pipeline e resume os achados |
| `/interpretar-mapa <slug>` | Lê as saídas e escreve a seção de resultados |

## Como as revisões ficam organizadas

As revisões são criadas **na pasta de trabalho de quem chama** — nunca dentro da instalação do
plugin:

```
seu-projeto/
└── revisoes/<slug>/
    ├── docs/       projeto, protocolo, estratégias de busca, livro de códigos
    ├── config/     revisao.json (recorte, limiares, proposições), execucao.json, tesauros
    ├── dados/
    │   ├── bruto/       exportações das bases (Scopus, WoS, SciELO, Dimensions, Lens, RIS, BibTeX)
    │   └── processado/  corpus normalizado, decisões, estatísticas
    └── saidas/     relatorio.md, tabelas CSV, redes .net/.gml, prisma.md, execucao.log
```

Para trabalhar noutra pasta, defina `CIENCIOMETRIA_DIR=/caminho/do/projeto`.

## Uso direto pela linha de comando

```bash
PLUGIN=~/.claude/plugins/cienciometria      # caminho da instalação
"$PLUGIN/bin/cienciometria" nova meu-tema --titulo "..." --tema "..."
"$PLUGIN/bin/cienciometria" analise --revisao meu-tema
```

## O que o motor calcula

**Desempenho** — produção anual e TCAC, fontes, autores (contagem integral e fracionária), países,
instituições, Lei de Lotka com teste de Kolmogorov-Smirnov, Lei de Bradford por zonas, índice de
Price, meia-vida citada, h-index, índice de colaboração e SCP/MCP por país.

**Estrutura intelectual** — co-citação de referências e acoplamento bibliográfico, normalizados por
força de associação (a mesma do VOSviewer).

**Estrutura social** — redes de coautoria entre autores, instituições e países, com componentes,
densidade e grau ponderado.

**Estrutura conceitual** — rede de co-palavras, agrupamento determinístico, mapa temático de Callon
(centralidade × densidade) e evolução por subperíodos.

**Relato** — fluxo PRISMA com contagens reais, kappa de Cohen, verificação automática das
proposições declaradas e log de auditoria de cada execução.

Saídas em Markdown, JSON, CSV e redes em Pajek (`.net`) e GML — abrem direto no VOSviewer e no
Gephi, para quem quiser refinar os mapas visualmente.

## Bases suportadas na importação

Scopus (CSV), Web of Science (*plain text* com referências citadas), SciELO (RIS/BibTeX),
Dimensions (CSV), Lens (CSV) e qualquer exportação RIS ou BibTeX de gerenciador de referências.
O parser é escolhido pelo nome do arquivo e pela extensão — daí a convenção
`scopus_AAAA-MM-DD.csv`, `wos_AAAA-MM-DD_01.txt`, `scielo_AAAA-MM-DD.ris`.

## Princípios que o plugin sustenta

1. Protocolo antes do dado; mudança posterior vira emenda datada.
2. Nenhum número digitado à mão — tudo vem do código e fica rastreável no log.
3. Decisões discricionárias (sinonímia, limiares, precedência entre bases) em arquivo versionado.
4. Critério de refutação declarado antes do resultado; proposição refutada é relatada como tal.
5. Cobertura declarada em todo indicador que dependa de campo incompleto.
6. O que o pipeline não decide, ele não finge decidir.

## Origem e atualização

O motor é mantido em `cienciometria/` neste mesmo repositório; esta pasta é uma cópia sincronizada
por `cienciometria/ferramentas/sincronizar_plugin.py`. Para alterar o comportamento, edite o motor e
rode `make plugin` — um teste automatizado falha se as duas cópias divergirem.
