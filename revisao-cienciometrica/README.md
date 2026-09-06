# Revisão cienciométrica — federalismo fiscal dos entes subnacionais

Projeto acadêmico completo para mapear, por métodos cienciométricos, a produção científica sobre
federalismo fiscal dos entes subnacionais (1990–2026): estrutura intelectual, social e conceitual do
campo, com atenção à posição da produção brasileira e latino-americana.

Reúne **o projeto de pesquisa**, **o protocolo da revisão** e **o pipeline de análise** — código que
gera todos os indicadores a partir das exportações das bases, sem manipulação manual de planilha e
sem dependências externas.

---

## Documentos

| # | Documento | O que traz |
|---|---|---|
| 1 | [Projeto de pesquisa](docs/01-projeto-de-pesquisa.md) | Tema, problema, perguntas, proposições, objetivos, justificativa, referencial, cronograma, riscos, referências |
| 2 | [Protocolo PRISMA](docs/02-protocolo-prisma.md) | Elegibilidade, fontes, triagem dupla, kappa, extração, fluxo, lista de verificação |
| 3 | [Estratégias de busca](docs/03-estrategias-de-busca.md) | Strings prontas para Scopus, WoS, SciELO, Dimensions e Lens; teste de recall; decisões terminológicas |
| 4 | [Livro de códigos](docs/04-livro-de-codigos.md) | Variáveis, domínios, tesauros, precedência entre bases |
| 5 | [Plano de análise](docs/05-plano-de-analise.md) | Indicadores, fórmulas, redes, limiares, critérios de refutação, robustez |
| 6 | [Reprodutibilidade](docs/06-reprodutibilidade.md) | Pipeline, versionamento, licenças, auditoria |

---

## Começando

```bash
cd revisao-cienciometrica

# 1) veja o pipeline funcionando com a amostra sintética (não são dados reais)
make exemplo
less saidas/exemplo/relatorio.md

# 2) rode os testes
make teste
```

Requisito: Python 3.9+. **Nenhuma biblioteca externa é necessária.**

---

## Fluxo de trabalho da pesquisa

```
docs/03  →  buscar nas bases        →  dados/bruto/*.csv|.txt|.ris|.bib
            (registrar em config/execucao.json)
                    ↓
make importar    →  corpus normalizado (tesauros de config/)
make dedup       →  duplicatas removidas + pares ambíguos para conferência humana
make triagem     →  planilha cega para os dois revisores
make kappa       →  concordância (meta ≥ 0,75)
make indicadores →  Lotka, Bradford, Price, impacto, colaboração
make redes       →  co-citação, acoplamento, coautoria, co-palavras, mapa temático
make prisma      →  contagens e diagrama do fluxo
make relatorio   →  saidas/relatorio.md
```

Ou, de uma vez: `make analise`.

### Depois das buscas

1. Salve as exportações em `dados/bruto/` com o nome da base no arquivo
   (`scopus_2026-03-15.csv`, `wos_2026-03-15_01.txt`, `scielo_2026-03-15.ris`) — o parser é escolhido
   pelo nome e pela extensão.
2. Preencha `config/execucao.json` com data de corte, strings, filtros e contagens. **O pipeline
   avisa no relatório quando a data de corte não está declarada.**
3. Ajuste os tesauros em `config/` conforme os dados forem revelando variantes.

---

## O que o pipeline produz

| Saída | Conteúdo |
|---|---|
| `saidas/relatorio.md` | Relatório completo, com todas as tabelas e a verificação das proposições |
| `saidas/resultados.json` | Todos os números em formato legível por máquina |
| `saidas/*.csv` | Produção anual, fontes, autores, países, instituições, Lotka, Bradford, Price, mais citados, mapa temático, evolução temática |
| `saidas/*.net`, `saidas/*.gml` | Redes para abrir no VOSviewer ou no Gephi |
| `saidas/prisma.md` | Diagrama do fluxo PRISMA com as contagens reais |
| `saidas/execucao.log` | Auditoria: comando, data, commit e contagens de cada execução |

---

## Estrutura

```
revisao-cienciometrica/
├── docs/               projeto, protocolo, buscas, códigos, análise, reprodutibilidade
├── config/             tesauros, léxico de países, sementes, registro de execução
├── dados/
│   ├── bruto/          exportações das bases (não versionadas — ver docs/06)
│   ├── exemplo/        amostra SINTÉTICA para testar o pipeline
│   └── processado/     corpus, decisões, estatísticas de deduplicação
├── src/cienciometria/  parsers, normalização, dedup, indicadores, redes, triagem, relatório
├── modelos/            planilha de triagem, ficha de extração, registro de decisões
├── saidas/             tudo o que o pipeline gera
└── testes/             testes automatizados e gerador da amostra sintética
```

---

## Princípios que o projeto adota

1. **Protocolo antes do dado.** Critérios e strings ficam registrados antes da busca; mudança
   posterior vira emenda datada, não ajuste silencioso.
2. **Nada à mão.** Todo número do relatório vem do código e é rastreável em `saidas/execucao.log`.
3. **Decisão fora do código.** Sinonímia, limiares e precedência entre bases ficam em `config/`,
   versionados e reversíveis.
4. **Proposição refutada é relatada como refutada.** Os critérios de refutação estão fixados no
   plano de análise, §6, antes de haver resultado.
5. **Cobertura declarada.** Todo indicador que depende de campo incompleto (referências, afiliação)
   vem acompanhado da sua cobertura.

---

## Relação com a linha de pesquisa deste repositório

O projeto de doutorado em `../output.md` investiga capacidade estatal municipal e receita de
referência na transição ao IBS. Esta revisão fornece o **estado da arte estruturado** dessa
investigação: em vez de um levantamento narrativo do que se conhece sobre federalismo fiscal
subnacional, um mapa verificável de onde o campo se concentra e do que ele deixou de fora —
inclusive a literatura sobre capacidade fiscal e transição tributária (temas T05 e T10 do livro de
códigos), diretamente ligados àquela tese.
