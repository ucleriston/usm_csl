# Cienciometria — motor de revisões bibliométricas

Um pipeline reprodutível para mapear a produção científica **de qualquer tema**: estrutura
intelectual, social e conceitual de um campo, a partir das exportações de Scopus, Web of Science,
SciELO, Dimensions, Lens ou de qualquer gerenciador de referências.

O motor não sabe de tema nenhum. Cada revisão é uma pasta em `revisoes/<slug>/` com o seu recorte,
as suas strings, os seus tesauros e as suas proposições. Trocar de tema é criar outra revisão — não
mexer no código.

```bash
python -m cienciometria nova capacidade-estatal-municipal \
    --titulo "Capacidade estatal municipal: mapeamento da produção" \
    --tema "Capacidades administrativas dos governos locais"

make analise REVISAO=capacidade-estatal-municipal
```

Requisito: Python 3.9+. **Nenhuma dependência externa.**

> Para usar isto dentro do Claude (Cowork, Claude Code ou app), há um plugin que embarca este motor
> e adiciona as skills que conduzem a revisão: [`plugins/cienciometria`](../plugins/cienciometria/README.md).
> Instalação: `/plugin marketplace add ucleriston/usm_csl` e `/plugin install cienciometria@usm-csl`.

---

## Comece por aqui

```bash
make exemplo    # roda o fluxo inteiro sobre a revisão de demonstração (dados sintéticos)
less revisoes/exemplo-sintetico/saidas/relatorio.md
make teste
```

---

## Revisões neste repositório

| Revisão | Situação |
|---|---|
| [`federalismo-fiscal-subnacional`](revisoes/federalismo-fiscal-subnacional/LEIA-ME.md) | Projeto, protocolo e strings prontos; buscas por executar |
| [`exemplo-sintetico`](revisoes/exemplo-sintetico/LEIA-ME.md) | Demonstração com dados fabricados — não é pesquisa |

`make listar` mostra todas, com data de corte e situação do corpus.

---

## Guias do motor

| Documento | Para quê |
|---|---|
| [Guia do fluxo](docs/01-guia-do-fluxo.md) | O caminho completo, da pergunta ao relatório |
| [Guia do protocolo](docs/02-guia-do-protocolo.md) | O que precisa estar decidido antes da primeira busca |
| [Guia de buscas](docs/03-guia-de-buscas.md) | Como montar a string, calibrar o recall e exportar cada base |
| [Livro de códigos do motor](docs/04-livro-de-codigos.md) | Variáveis comuns a qualquer revisão |
| [Plano de análise](docs/05-plano-de-analise.md) | Indicadores, redes, limiares e como declarar proposições |
| [Reprodutibilidade](docs/06-reprodutibilidade.md) | Estrutura, comandos, licenças e auditoria |

---

## O que o pipeline calcula

**Desempenho** — produção anual, TCAC, fontes, autores (contagem integral e fracionária), países,
instituições, Lei de Lotka com teste de Kolmogorov-Smirnov, Lei de Bradford por zonas, índice de
Price, meia-vida citada, h-index, índice de colaboração, SCP/MCP por país.

**Estrutura intelectual** — co-citação de referências e acoplamento bibliográfico, com força de
associação (a mesma normalização do VOSviewer).

**Estrutura social** — redes de coautoria entre autores, instituições e países, com componentes,
densidade e grau ponderado.

**Estrutura conceitual** — rede de co-palavras, agrupamento determinístico, mapa temático de Callon
(centralidade × densidade, quatro quadrantes) e evolução temática por subperíodos.

**Relato** — fluxo PRISMA com contagens reais, kappa de Cohen entre revisores, verificação
automática das proposições e log de auditoria de cada execução.

Saídas: `relatorio.md`, `resultados.json`, tabelas CSV e redes em Pajek (`.net`) e GML para abrir no
VOSviewer ou no Gephi.

---

## Fluxo de trabalho

```
nova <slug>            cria a revisão a partir do esqueleto
   ↓
docs/ + revisao.json   recorte, protocolo, strings, proposições com critério de refutação
   ↓
buscar nas bases       exportações em revisoes/<slug>/dados/bruto/ + registro em execucao.json
   ou coletar          OpenAlex/Crossref pela API aberta, com registro automático da execução
   ↓
importar → dedup       corpus normalizado; faixa de dúvida separada para conferência humana
   ↓
triagem → kappa        dois revisores independentes, concordância medida
   ↓
indicadores → redes    desempenho, estrutura intelectual, social e conceitual
   ↓
prisma → relatorio     fluxo, verificação das proposições, relatório final
```

---

## Estrutura

```
cienciometria/
├── docs/                 guias do motor
├── config/               configuração comum a todas as revisões (léxico de países)
├── src/cienciometria/    parsers, normalização, dedup, indicadores, redes, triagem, relatório
├── modelos/revisao-modelo/  esqueleto copiado ao criar uma revisão
├── revisoes/<slug>/      docs/, config/, dados/, saidas/ de cada revisão
├── ferramentas/          sincronização do plugin
└── testes/               testes automatizados e gerador da amostra sintética
```

O plugin em `../plugins/cienciometria/` é uma **cópia sincronizada** deste motor (`make plugin`),
para que possa ser instalado e usado fora daqui. O motor é a fonte de verdade; um teste falha se as
cópias divergirem.

---

## Princípios

1. **Protocolo antes do dado.** Critérios e strings ficam registrados antes da busca; mudança
   posterior vira emenda datada.
2. **Nada à mão.** Todo número do relatório vem do código e é rastreável em `saidas/execucao.log`.
3. **Decisão fora do código.** Sinonímia, limiares, subperíodos e precedência entre bases ficam em
   `config/revisao.json`, versionados e reversíveis.
4. **Critério de refutação declarado antes do resultado.** As proposições trazem a condição que as
   derruba; o relatório aplica e informa — inclusive quando o veredicto contraria a expectativa.
5. **Cobertura declarada.** Todo indicador que depende de campo incompleto vem acompanhado da sua
   cobertura.
6. **O que o pipeline não decide, ele não finge decidir.** Proposição que depende de leitura é
   relatada como pendente, e rótulo automático de agrupamento é provisório até a leitura do núcleo.
