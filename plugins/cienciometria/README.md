# Plugin Cienciometria

Conduz revisões cienciométricas (bibliométricas) de ponta a ponta, com o motor de análise
embarcado: **não precisa de R, bibliometrix, VOSviewer nem de qualquer biblioteca Python externa.**
Só Python 3.9+.

## Instalação

```
/plugin marketplace add ucleriston/usm_csl
/plugin install cienciometria@usm-csl
```

## As oito etapas do projeto

O plugin conduz a pesquisa inteira, e **mantém o estado no disco** — a pesquisa continua de onde
parou, mesmo semanas depois, em outra conversa:

```
E1 Escopo e proposições → E2 Protocolo → E3 Busca → E4 Corpus →
E5 Triagem → E6 Análise → E7 Fichamento → E8 Artigo
```

```bash
cienciometria estado --revisao <slug>    # em que etapa está e o que falta
```

## O que ele ativa

**Skills** (disparam sozinhas quando o assunto aparece):

| Skill | Etapa | Cobre |
|---|---|---|
| `pesquisa-cienciometrica` | todas | **Skill de entrada.** Sabe onde a pesquisa está, qual etapa vem e quem a executa |
| `escopo-da-pesquisa` | E1 | A conversa de delimitação: objeto, janela, perguntas, proposições refutáveis |
| `estrategia-de-busca` | E3 | Strings por base, proximidade, sinonímia, recall, coleta em fonte aberta |
| `revisao-cienciometrica` | E4–E6 | Corpus, deduplicação, indicadores, redes |
| `triagem-e-prisma` | E2, E5 | Critérios, códigos de exclusão, triagem dupla cega, kappa, fluxo PRISMA |
| `interpretar-resultados` | E6 | O que cada indicador sustenta, rótulos, mapa temático |
| `fichamento` | E7 | Fichas comparáveis dos artigos-núcleo e a matriz de lacunas |
| `relatorio-cienciometrico` | E8 | O artigo montado dos dados, adaptado ao modelo do periódico |

**Comandos:**

| Comando | Faz |
|---|---|
| `/estado-da-pesquisa <slug>` | Mostra em que etapa está e conduz o próximo passo |
| `/nova-revisao <tema>` | Conduz a delimitação e cria a revisão configurada |
| `/analisar-corpus <slug>` | Roda o pipeline e resume os achados |
| `/interpretar-mapa <slug>` | Lê as saídas e escreve a seção de resultados |
| `/fichar <slug>` | Escolhe os artigos-núcleo, cria as fichas e consolida as lacunas |
| `/escrever-artigo <slug>` | Gera o rascunho com os números no lugar e conduz a redação |

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
    ├── fichamentos/ uma ficha por artigo-núcleo lido
    └── saidas/     relatorio.md, artigo.md, matriz-de-lacunas.csv, tabelas CSV,
                    redes .net/.gml, prisma.md, execucao.log
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

**Fichamento e redação** — seleção dos artigos-núcleo por critério declarado, fichas em campos
comparáveis, matriz que confronta cada lacuna declarada pelos autores com a frequência dos seus
termos no corpus, e o rascunho do artigo com todos os números já no lugar.

Saídas em Markdown, JSON, CSV e redes em Pajek (`.net`) e GML — abrem direto no VOSviewer e no
Gephi, para quem quiser refinar os mapas visualmente.

## Bases suportadas

**Coleta direta pela API** (sem chave, sem acesso institucional): OpenAlex e Crossref —
`cienciometria coletar --revisao <slug> --fonte openalex --busca "..." --email voce@exemplo.org`.
A resposta crua é salva e a execução, registrada automaticamente.

**Importação de exportações:** Scopus (CSV), Web of Science (*plain text* com referências citadas),
SciELO (RIS/BibTeX), Dimensions (CSV), Lens (CSV) e qualquer exportação RIS ou BibTeX de gerenciador
de referências.
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
