# Protocolo da revisão cienciométrica

**Título:** Federalismo fiscal dos entes subnacionais: estrutura e evolução da produção científica (1990–2026)
**Versão do protocolo:** 1.0
**Data:** _preencher na primeira execução_
**Registro:** recomenda-se depósito em OSF (https://osf.io) antes da execução das buscas; anotar o DOI aqui.
**Configuração correspondente:** `revisoes/federalismo-fiscal-subnacional/config/revisao.json`

> O protocolo é escrito **antes** da coleta. Qualquer alteração posterior é registrada na seção 10
> (Emendas), com data e justificativa. Não se altera critério depois de ver o resultado sem registrar
> a alteração.

---

## 1 Tipo de revisão

Revisão cienciométrica (bibliometria + mapeamento de ciência), com relato do processo de
identificação e triagem conforme PRISMA 2020 e relato das buscas conforme PRISMA-S. Não é revisão
sistemática de efeitos: não há avaliação de risco de viés dos estudos primários nem síntese de
estimativas, porque a unidade de análise é o registro bibliográfico, não o achado empírico.

---

## 2 Perguntas

QP1 a QP6, conforme a seção 2 do [projeto de pesquisa](01-projeto-de-pesquisa.md).

---

## 3 Critérios de elegibilidade

### 3.1 Inclusão

| Dimensão | Critério |
|---|---|
| **Objeto** | Trata de relações fiscais entre níveis de governo em que o ente subnacional (estado, província, região, município, governo local) é unidade de análise, de decisão ou de impacto |
| **Escopo temático** | Competência tributária subnacional; transferências intergovernamentais; partilha de receita; equalização; endividamento subnacional; restrição orçamentária branda; esforço/capacidade fiscal; autonomia financeira; descentralização fiscal; regras fiscais subnacionais; guerra fiscal e competição tributária horizontal; efeitos distributivos territoriais |
| **Período** | Publicado entre 1990 e a data de corte |
| **Tipo documental** | Artigo, revisão, capítulo de livro indexado, trabalho completo em anais indexado |
| **Idioma** | Português, inglês ou espanhol |
| **Revisão por pares** | Publicado em veículo com revisão por pares declarada |

### 3.2 Exclusão

| # | Critério | Justificativa |
|---|---|---|
| E1 | Federalismo tratado apenas em dimensão política, sem componente fiscal ou orçamentário | Fora do objeto |
| E2 | Finanças públicas exclusivamente do governo central, sem recorte subnacional | Fora do objeto |
| E3 | Descentralização administrativa ou política sem componente de receita ou despesa | Fora do objeto |
| E4 | Editorial, resenha, errata, carta, entrevista, apresentação de dossiê | Sem conteúdo de pesquisa |
| E5 | Registro sem autoria, sem ano ou sem título identificável | Metadado insuficiente |
| E6 | Duplicata de registro já incluído | Deduplicação |
| E7 | Uso de "federalismo fiscal" apenas como metáfora ou como contexto marginal (menção única, sem análise) | Falso positivo terminológico |
| E8 | Texto integral indisponível quando a decisão de triagem depender dele | Não avaliável |

### 3.3 Casos de fronteira — decisão pré-fixada

- **Federalismo fiscal em federações e em Estados unitários descentralizados.** Ambos incluídos. O
  objeto é a relação fiscal entre níveis, não a forma de Estado. A forma é registrada como variável
  (`forma_estado`) para permitir recorte posterior.
- **Trabalhos sobre um único município ou estado.** Incluídos, desde que o argumento se refira à
  posição do ente no arranjo fiscal intergovernamental. Estudo de gestão orçamentária interna, sem
  essa referência, é excluído por E2.
- **Trabalhos de direito tributário sobre competência.** Incluídos quando discutem repartição de
  competência ou de receita entre entes; excluídos quando tratam de relação fisco-contribuinte.
- **Modelos teóricos sem aplicação territorial.** Incluídos se o modelo tiver níveis de governo
  explícitos.

---

## 4 Fontes de informação

| Base | Papel | Justificativa |
|---|---|---|
| **Scopus** | Principal | Maior cobertura em ciências sociais entre as bases de citação com campo de referências |
| **Web of Science (Core Collection)** | Principal | Referência histórica, essencial para co-citação e comparabilidade |
| **SciELO** | Principal | Corrige a sub-representação da produção lusófona e hispânica |
| **Dimensions** | Complementar | Amplia cobertura de capítulos e de literatura recente |
| **Lens.org** | Complementar | Agregador aberto; auxilia na recuperação de DOI e no controle de cobertura |
| **Crossref / OpenAlex (API)** | Enriquecimento | Completar DOI, ISSN, afiliação e referências ausentes |
| **Google Scholar** | Apenas verificação | Usado só no teste de recall do conjunto-semente; não integra o corpus (resultados não exportáveis de forma reprodutível) |

Fontes adicionais: (a) *snowballing* para trás sobre as 30 obras mais citadas do corpus; (b) *hand
search* nos últimos 3 volumes dos periódicos da primeira zona de Bradford; (c) corpus auxiliar de
literatura institucional (Banco Mundial, FMI, OCDE, BID, IPEA, CEPAL), catalogado separadamente.

---

## 5 Estratégia de busca

Ver [03-estrategias-de-busca.md](03-estrategias-de-busca.md). Regras invariáveis:

1. Busca em título, resumo e palavras-chave (`TITLE-ABS-KEY` no Scopus; `TS=` na WoS).
2. Três blocos conceituais combinados por `AND`: **(fiscal/tributário) AND (federalismo/relações
   intergovernamentais/descentralização) AND (ente subnacional)**, com bloco 3 opcional quando o
   bloco 2 já o implica — a variante é declarada e executada separadamente.
3. Sinônimos em português, inglês e espanhol dentro de cada bloco, combinados por `OR`.
4. Data de corte única para todas as bases, registrada em `config/execucao.json`.
5. Cada execução salva: string exata, base, filtros, data, hora, número de resultados e arquivo
   exportado. Sem esse registro, a execução é descartada.
6. **Teste de recall:** antes da execução definitiva, a string deve recuperar pelo menos 22 dos 25
   trabalhos do conjunto-semente (`config/sementes.csv`). Abaixo disso, a string é revista.

---

## 6 Seleção dos estudos

```
Identificação → Deduplicação → Triagem 1 (título/resumo) → Triagem 2 (texto integral) → Inclusão
```

- **Deduplicação:** automática (DOI exato → título normalizado + ano → similaridade de título ≥ 0,93
  no mesmo ano), com conferência manual dos pares no intervalo 0,88–0,93.
- **Triagem 1:** dois revisores, independentes e cegos entre si, sobre título, resumo e
  palavras-chave. Decisão: incluir / excluir / dúvida.
- **Triagem 2:** texto integral, apenas para os registros aprovados na triagem 1 e para todas as
  dúvidas.
- **Concordância:** kappa de Cohen calculado ao final de cada rodada. Meta ≥ 0,75. Abaixo disso, os
  critérios são reescritos e a rodada é refeita — não se resolve baixa concordância por discussão
  caso a caso.
- **Divergências:** resolvidas por consenso; persistindo, decide um terceiro revisor. Toda
  divergência resolvida é registrada em `dados/processado/decisoes.csv` com a razão.
- **Calibração prévia:** ambos os revisores triam a mesma amostra aleatória de 100 registros antes
  do início; a rodada só começa com kappa ≥ 0,75 nessa amostra.

Cada exclusão na triagem 2 recebe **um** código de exclusão (E1–E8), o de maior precedência na ordem
listada. O relato PRISMA apresenta a contagem por código.

---

## 7 Extração de dados

Variáveis, domínios e regras: [04-livro-de-codigos.md](04-livro-de-codigos.md).

Extração automática (metadados) por `src/cienciometria`; extração manual apenas para as variáveis
de conteúdo (`abordagem`, `nivel_ente`, `tema_declarado`, `pais_do_caso`, `forma_estado`), com dupla
codificação de 20% da amostra e kappa por variável.

---

## 8 Fluxo PRISMA

A contagem é gerada pelo pipeline
(`python -m cienciometria prisma --revisao federalismo-fiscal-subnacional`) e preenche o diagrama:

```
Identificação
  Registros identificados nas bases .................... n = ____
    Scopus ............................................. n = ____
    Web of Science ..................................... n = ____
    SciELO ............................................. n = ____
    Dimensions ......................................... n = ____
    Lens ............................................... n = ____
  Registros identificados por outros métodos ........... n = ____
Triagem
  Duplicatas removidas ................................. n = ____
  Registros triados (título/resumo) .................... n = ____
    Excluídos .......................................... n = ____
  Textos integrais avaliados ........................... n = ____
    Excluídos por código E1–E8 ......................... n = ____
Inclusão
  Registros incluídos no corpus final .................. n = ____
    Com campo de referências (subcorpus de co-citação) .. n = ____
```

---

## 9 Análise

Ver [05-plano-de-analise.md](../../../docs/05-plano-de-analise.md).

---

## 10 Emendas ao protocolo

| Data | Seção | Alteração | Justificativa | Responsável |
|---|---|---|---|---|
| | | | | |

---

## 11 Papéis

| Papel | Responsabilidade |
|---|---|
| Coordenação | Protocolo, decisões de escopo, redação final |
| Revisor 1 / Revisor 2 | Triagem independente, extração de conteúdo |
| Terceiro revisor | Desempate |
| Processamento de dados | Execução do pipeline, versionamento, integridade das saídas |

---

## 12 Lista de verificação antes de fechar o corpus

- [ ] Data de corte registrada em `config/execucao.json`
- [ ] Strings de todas as bases arquivadas com contagem de resultados
- [ ] Teste de recall do conjunto-semente ≥ 22/25
- [ ] Kappa de calibração ≥ 0,75 registrado
- [ ] Kappa das triagens 1 e 2 registrado
- [ ] Todos os excluídos da triagem 2 com código E1–E8
- [ ] Deduplicação conferida manualmente na faixa 0,88–0,93
- [ ] Corpus com DOI verificado para ao menos 90% dos registros
- [ ] Tesauros de fontes, autores e termos revisados
- [ ] Contagens do fluxo PRISMA fechando aritmeticamente
