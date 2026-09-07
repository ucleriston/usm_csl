---
name: revisao-cienciometrica
description: >-
  Conduz revisões cienciométricas e bibliométricas de ponta a ponta — recorte, protocolo PRISMA,
  strings de busca, coleta em fontes abertas, deduplicação, triagem com kappa, indicadores (Lotka,
  Bradford, Price, h-index), redes de co-citação, coautoria e co-palavras, mapa temático e relatório
  reprodutível — com motor de análise embarcado, sem R nem VOSviewer. Use SEMPRE que aparecer
  revisão bibliométrica, cienciometria, análise bibliométrica, mapeamento da literatura ou do campo
  científico, estado da arte sistemático, revisão de escopo, bibliometrix, VOSviewer, CiteSpace,
  co-citação, acoplamento bibliográfico, co-palavras ou mapa temático. Use TAMBÉM em pedidos como
  "quero mapear o que já se publicou sobre X", "preciso do estado da arte da minha tese", "quem são
  os autores centrais desse campo", "exportei da Scopus e não sei o que fazer", "tenho um .bib/.ris
  para analisar" ou "quais as lacunas da literatura sobre Y" — mesmo sem a palavra bibliometria.
---

# Revisão cienciométrica

Esta skill conduz a revisão inteira: da pergunta ao relatório. O trabalho pesado (parsers,
deduplicação, indicadores, redes) é feito pelo motor embarcado no plugin — você orquestra,
decide com o usuário e interpreta.

## O que a revisão entrega — e o que ela não entrega

Cienciometria descreve **o campo que estuda um tema**: quem publica, onde, com quem, sobre o quê,
citando quem, desde quando. Ela não responde o que a literatura *concluiu* sobre o tema.

Antes de qualquer coisa, confirme com o usuário qual dos dois ele quer:

- "O que se sabe sobre X?" → é revisão sistemática ou integrativa de conteúdo. Esta skill ajuda só
  na etapa de identificação e triagem; a síntese dos achados é leitura, não indicador.
- "Como o conhecimento sobre X está organizado, quem o produz e o que ficou de fora?" → é aqui.

Muita gente pede "estado da arte" querendo a primeira coisa. Perguntar isso no início evita
entregar um mapa quando o que se queria era um resumo.

## O motor

O plugin traz o motor embarcado. O lançador está em `bin/cienciometria`, na raiz do plugin — a
pasta que contém o diretório `skills/` de onde esta SKILL.md foi carregada. Defina uma variável no
início da sessão e use sempre ela:

```bash
CIENCIO="<raiz do plugin>/bin/cienciometria"     # ex.: .../plugins/cienciometria/bin/cienciometria
"$CIENCIO" --version
```

Se `CLAUDE_PLUGIN_ROOT` estiver definida no ambiente, use `"$CLAUDE_PLUGIN_ROOT/bin/cienciometria"`.

**As revisões são criadas na pasta de trabalho do usuário**, em `./revisoes/<slug>/` — nunca dentro
da instalação do plugin. Rode os comandos a partir da pasta do projeto dele, ou defina
`CIENCIOMETRIA_DIR=/caminho/do/projeto`. Requisito: Python 3.9+, sem dependências externas.

| Comando | O que faz |
|---|---|
| `"$CIENCIO" nova <slug> --titulo "..." --tema "..."` | Cria a revisão a partir do esqueleto |
| `"$CIENCIO" listar` | Lista as revisões da pasta e a situação de cada uma |
| `"$CIENCIO" coletar --revisao <slug> --fonte openalex --busca "..."` | Baixa registros das APIs abertas (OpenAlex, Crossref) |
| `"$CIENCIO" importar --revisao <slug>` | Lê as exportações e monta o corpus normalizado |
| `"$CIENCIO" comparar --revisao <slug> --antes a.csv --depois b.csv` | Mede o que uma alteração na busca derrubou e o que trouxe |
| `"$CIENCIO" dedup --revisao <slug>` | Deduplica; separa pares ambíguos para conferência humana |
| `"$CIENCIO" triagem --revisao <slug>` | Gera a planilha cega de triagem |
| `"$CIENCIO" kappa --revisao <slug> --triagem <arquivo>` | Concordância entre revisores |
| `"$CIENCIO" indicadores --revisao <slug>` | Produção, Lotka, Bradford, Price, impacto, colaboração |
| `"$CIENCIO" redes --revisao <slug>` | Co-citação, acoplamento, coautoria, co-palavras, mapa temático |
| `"$CIENCIO" prisma --revisao <slug>` | Contagens e diagrama do fluxo PRISMA |
| `"$CIENCIO" relatorio --revisao <slug>` | Monta `saidas/relatorio.md` |
| `"$CIENCIO" analise --revisao <slug>` | Tudo, na ordem |

## O fluxo

### 1. Criar a revisão

```bash
"$CIENCIO" nova <slug> --titulo "..." --tema "..."
```

O slug é curto e em minúsculas (`capacidade-estatal-municipal`). Isso cria `revisoes/<slug>/` com
os documentos-modelo, a configuração e as pastas de dados e saídas.

### 2. Delimitar antes de buscar

Esta é a etapa que decide a qualidade de tudo o que vem depois, e é conversa, não formulário.
O que você precisa saber:

- **O objeto.** O que caracteriza um trabalho como pertencente ao tema? E o que, sendo parecido,
  fica de fora? Peça dois ou três exemplos de trabalhos que claramente entram e dois que claramente
  não entram — é o teste mais rápido para descobrir se o recorte está claro.
- **A janela temporal e a razão dela.** Um marco legal, uma virada teórica, um evento. Janela sem
  razão declarada vira pergunta na banca.
- **Idiomas e bases disponíveis.** Isso depende do acesso institucional do usuário — pergunte, não
  presuma. Duas coisas que costumam passar batido: o Portal de Periódicos da CAPES é meio de acesso,
  não base de busca (busca-se *dentro* de Scopus, WoS, SciELO por ele); e, em temas brasileiros, as
  bases nacionais decidem o resultado — SciELO, SPELL na administração, LILACS e BVS na saúde, BDTD
  e o Catálogo de Teses da CAPES, além da literatura cinzenta institucional (IPEA, Fiocruz, Embrapa,
  ministérios). Elas exigem exportação manual, e deixá-las de fora é decisão a declarar, não
  omissão neutra.
- **A pergunta que só esta revisão faz.** As cinco primeiras perguntas (volume, distribuição,
  estrutura intelectual, social e conceitual) servem a qualquer revisão. A sexta é a do usuário.

Registre o resultado em dois lugares que precisam concordar entre si:

- `revisoes/<slug>/docs/01-projeto-de-pesquisa.md` — o texto, para humanos e para a banca;
- `revisoes/<slug>/config/revisao.json` — o mesmo recorte em forma de máquina: `janela`, `idiomas`,
  `tipos_documento`, `bases`, `limiares`, `periodos`, `codigos_exclusao`, `vocabulario_temas` e
  as `proposicoes`.

**As proposições merecem atenção.** Cada uma traz o critério que a refuta, escrito antes de existir
resultado, e o relatório aplica esse critério automaticamente. É o que separa descrever um campo de
confirmar a própria expectativa. O formato está em `docs/05-plano-de-analise.md`, §6; proposição que
depende de leitura entra como `"tipo": "manual"` e é relatada como pendente — nunca como sustentada.

### 3. Protocolo e strings

Preencha `docs/02-protocolo-prisma.md` (elegibilidade, códigos de exclusão, procedimento de
triagem) e `docs/03-estrategias-de-busca.md` (blocos e strings por base).

Os documentos vêm de um esqueleto, e esqueleto não sabe do caso: **adapte-os à situação real do
usuário antes de entregar**. Um protocolo que prescreve "dois revisores independentes e kappa a cada
rodada" para quem está sozinho não é rigor, é um documento que contradiz o próprio pacote — e é
pior que documento nenhum, porque a contradição aparece na banca.

Para montar as strings, use a skill **estrategia-de-busca**. Para o desenho da triagem, a skill
**triagem-e-prisma**.

### 4. Buscar

Há dois caminhos, e a escolha depende do acesso que o usuário tem.

**Bases proprietárias (Scopus, Web of Science).** Você não tem o login dele: quem executa é o
usuário. Entregue as strings prontas para copiar e colar, diga exatamente como exportar cada base —
no caso da WoS, *Full Record and Cited References*, senão não há co-citação — e onde salvar
(`revisoes/<slug>/dados/bruto/`, com o nome da base no arquivo). Depois peça que registre cada
execução em `config/execucao.json`: string, filtros, data, hora, contagem.

**Fontes abertas (OpenAlex, Crossref).** Aqui você mesmo pode coletar, e o comando já registra a
execução:

```bash
"$CIENCIO" coletar --revisao <slug> --fonte openalex --busca "termos" --email <e-mail do usuário> --limite 3000
```

Peça o e-mail: as duas APIs pedem contato e dão fila mais rápida a quem o informa. Se o comando
falhar com HTTP 403, a rede do usuário bloqueia o host — reporte isso e siga pela interface da base,
sem tentar rotas alternativas. Vale saber, para relatar como limitação: as palavras-chave do
OpenAlex são conceitos inferidos por máquina, não termos de autor, e o Crossref raramente traz
afiliação, o que enfraquece as redes de colaboração.

**Nunca invente registros bibliográficos, contagens de resultados ou datas de corte.** Um corpus
fabricado destrói a revisão inteira e é indefensável. Se faltar dado, o certo é dizer que falta.

### 5. Construir o corpus

```bash
"$CIENCIO" importar --revisao <slug>
"$CIENCIO" dedup    --revisao <slug>
```

Depois de deduplicar, três conferências que valem o tempo:

1. `dados/processado/revisao-duplicatas.csv` — os pares que o programa não teve segurança de fundir.
   Decida um a um com o usuário.
2. `dados/processado/importacao.csv` — quantos registros vieram de cada arquivo. Um arquivo com zero
   registros costuma ser exportação incompleta ou formato errado, não base vazia.
3. Proporção de registros com DOI e com campo de referências. Sem referências não há co-citação, e
   isso precisa aparecer no relatório como cobertura, não ser varrido para baixo do tapete.

### 6. Triar

```bash
"$CIENCIO" triagem --revisao <slug>
```

Gera a planilha cega. Dois revisores preenchem colunas separadas sem ver a do outro; depois:

```bash
"$CIENCIO" kappa --revisao <slug> --triagem revisoes/<slug>/dados/processado/triagem-preenchida.csv
```

Kappa abaixo do mínimo da revisão significa critério mal escrito — a resposta é reescrever o
critério e refazer a rodada, não negociar registro a registro. Detalhes na skill
**triagem-e-prisma**.

Quando o usuário for revisor único (comum em pesquisa individual), diga com franqueza que a dupla
triagem é o padrão e ofereça alternativas: recodificar uma amostra de 20% depois de um intervalo,
ou pedir a um colega que faça só a amostra. Registre a escolha como limitação.

### 7. Analisar

```bash
"$CIENCIO" analise --revisao <slug>
```

Saídas em `revisoes/<slug>/saidas/`: `relatorio.md`, `resultados.json`, tabelas CSV, redes em
`.net` (Pajek) e `.gml` para VOSviewer ou Gephi, `prisma.md` e o log de auditoria.

### 8. Interpretar e escrever

O relatório entrega números e agrupamentos; ele não entrega leitura. Use a skill
**interpretar-resultados** para rotular agrupamentos, ler o mapa temático e redigir a seção de
resultados sem extrapolar o que os indicadores sustentam.

Quando o usuário for de fora da academia — gestão pública, terceiro setor, empresa —, pergunte que
decisão está em jogo. O mapa ganha outro uso quando é cruzado com dado do próprio domínio: onde a
produção científica se concentra *versus* onde está o problema (déficit de serviço, gasto,
população afetada). Esse cruzamento não é indicador bibliométrico, e sim a razão pela qual alguém
fora da universidade encomendaria a revisão.

## Integridade

Estas regras não são burocracia: são o que faz a revisão sobreviver à revisão por pares.

- **Dado inventado, nunca.** Nem registro, nem contagem, nem data de corte, nem kappa.
- **Cobertura declarada.** Todo indicador que dependa de campo incompleto (referências, afiliação)
  vem com a sua cobertura ao lado.
- **Proposição refutada é relatada como refutada.** O resultado que contraria a expectativa é o
  achado mais valioso da revisão, não um problema a contornar.
- **Rótulo automático é provisório.** Os nomes de agrupamento que o motor sugere valem como pista;
  o rótulo definitivo sai da leitura dos itens mais centrais.
- **Decisão discricionária vai para arquivo versionado**, não para o meio do código nem para a
  memória de quem executou.
- **Não afirme verificação que você não fez.** "Conferi que o motor lê a configuração" só vale se
  você rodou o comando e viu a saída; caso contrário, diga o que fez e o que ficou por conferir.
- **Exemplo com número fabricado nunca sai em formato de entrega.** Se precisar demonstrar um
  formato, o aviso de que os dados são fictícios vai dentro do próprio arquivo — um relatório ou
  fluxograma renderizado se separa da pasta em que nasceu, e o aviso ao lado não o acompanha.

## Quando algo dá errado

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| `importar` não encontra registros | Nome do arquivo sem a base, ou formato não exportado | Renomear (`scopus_*.csv`, `wos_*.txt`, `scielo_*.ris`, `openalex_*.json`); reexportar |
| `coletar` devolve HTTP 403 | Política de rede bloqueia a API | Reportar o host bloqueado; usar outra rede ou a interface da base — nunca contornar |
| Muitos registros sem ano ou sem autor | Exportação parcial de campos | Reexportar com todos os campos marcados |
| Co-citação vazia ou quase | Base sem campo de referências | Declarar a cobertura; usar acoplamento e co-palavras como estrutura principal |
| α de Lotka negativo ou absurdo | Homonímia ou corpus pequeno demais | Conferir a desambiguação dos autores mais produtivos antes de interpretar |
| Um único agrupamento no mapa temático | Limiar de termos alto demais para o corpus | Baixar `min_termo` em `config/revisao.json` e reexecutar `redes` |
| Kappa baixo | Critério ambíguo | Reescrever o critério, registrar a emenda no protocolo, refazer a rodada |

## Documentação de apoio

Na raiz do plugin, `docs/` traz os guias completos do motor — leia o que a etapa exigir, em vez de
carregar tudo:

- `docs/01-guia-do-fluxo.md` — o caminho completo, com o detalhe de cada etapa
- `docs/02-guia-do-protocolo.md` — o que precisa estar decidido antes da primeira busca
- `docs/03-guia-de-buscas.md` — construção de strings, calibração de recall, exportação por base
- `docs/04-livro-de-codigos.md` — variáveis do corpus e regras de normalização
- `docs/05-plano-de-analise.md` — indicadores, fórmulas, limiares e formato das proposições
- `docs/06-reprodutibilidade.md` — estrutura, comandos, licenças e auditoria

E `references/exemplo-revisao.md`, nesta skill, mostra uma revisão real já configurada — útil como
referência de preenchimento quando o usuário não souber por onde começar.
