# Livro de códigos

Define cada variável do corpus: nome, tipo, origem, domínio e regra de codificação. Colunas com
origem **automática** são preenchidas pelo pipeline; **manual**, por revisor humano.

---

## 1 Identificação

| Variável | Tipo | Origem | Domínio / regra |
|---|---|---|---|
| `id` | texto | automática | Chave interna estável: `<base>:<n>` na importação; preservada após a deduplicação (vence o registro da base de maior prioridade) |
| `doi` | texto | automática | Normalizado para minúsculas, sem prefixo `https://doi.org/`. Vazio se ausente |
| `base_origem` | categórica | automática | `scopus`, `wos`, `scielo`, `dimensions`, `lens`, `manual` |
| `bases_todas` | texto | automática | Lista, separada por `;`, de todas as bases em que o registro apareceu (preenchida na deduplicação) |
| `titulo` | texto | automática | Como no registro, sem alteração de caixa |
| `titulo_norm` | texto | automática | Minúsculas, sem acentos, sem pontuação, espaços colapsados — usada apenas para deduplicação |

## 2 Autoria e afiliação

| Variável | Tipo | Origem | Domínio / regra |
|---|---|---|---|
| `autores` | lista | automática | `Sobrenome, I.` separados por `;`. Partículas (`de`, `da`, `van`, `del`) mantidas no sobrenome |
| `n_autores` | inteiro | automática | Contagem de `autores` |
| `orcid` | lista | automática | Quando disponível; base da desambiguação |
| `afiliacoes` | texto | automática | Íntegra do campo da base |
| `instituicoes` | lista | automática | Instituição normalizada pelo tesauro `config/thesauro-instituicoes.json` |
| `paises` | lista | automática | Extraídos das afiliações via `config/lexico-paises.json`; sem repetição |
| `colab_internacional` | booleana | automática | `1` se `paises` tem 2 ou mais países distintos |

## 3 Publicação

| Variável | Tipo | Origem | Domínio / regra |
|---|---|---|---|
| `ano` | inteiro | automática | 1990–corte. Registro fora da janela é excluído na triagem |
| `fonte` | texto | automática | Periódico/livro/anais, normalizado por `config/thesauro-fontes.json` |
| `issn` | texto | automática | Sem hífen |
| `tipo_documento` | categórica | automática | `artigo`, `revisao`, `capitulo`, `anais` |
| `idioma` | categórica | automática | `pt`, `en`, `es` |
| `editora` | texto | automática | — |
| `acesso_aberto` | booleana | automática | Quando informado pela base ou pelo Unpaywall |

## 4 Impacto

| Variável | Tipo | Origem | Domínio / regra |
|---|---|---|---|
| `citacoes` | inteiro | automática | Contagem da base de origem na data de corte. Em registro deduplicado, prevalece o **maior** valor entre as bases, com a base registrada em `fonte_citacoes` |
| `fonte_citacoes` | categórica | automática | Base de onde veio `citacoes` |
| `citacoes_por_ano` | decimal | automática | `citacoes / (ano_corte - ano + 1)` |
| `referencias` | lista | automática | Referências citadas, separadas por `;`. Vazio quando a base não fornece |
| `n_referencias` | inteiro | automática | — |

## 5 Conteúdo (codificação manual)

| Variável | Tipo | Domínio | Regra |
|---|---|---|---|
| `nivel_ente` | categórica múltipla | `estadual`, `municipal`, `regional`, `provincial`, `multiple`, `nao_especificado` | Nível de governo que é a unidade de análise. `multiple` quando dois ou mais são tratados simetricamente |
| `abordagem` | categórica | `teorica`, `empirica_quant`, `empirica_qual`, `mista`, `normativa_juridica`, `revisao` | `normativa_juridica` para análise dogmática de normas; `teorica` para modelagem sem dados |
| `tema_declarado` | categórica múltipla | ver §6 | Até 3 temas por registro, em ordem de centralidade no resumo |
| `pais_do_caso` | lista | ISO 3166-1 alfa-3 | País(es) objeto da análise empírica. `XXX` se puramente teórico; `MUL` se comparação de mais de 5 países |
| `forma_estado` | categórica | `federacao`, `unitario_descentralizado`, `misto`, `na` | Do caso analisado, não do país do autor |
| `periodo_analisado` | texto | `AAAA-AAAA` | Do dado empírico, não da publicação |
| `metodo_principal` | texto | livre controlado | Ex.: `painel`, `diff-in-diff`, `estudo de caso`, `dogmática`, `simulação`, `survey` |
| `decisao_triagem` | categórica | `incluido`, `excluido`, `duvida` | — |
| `codigo_exclusao` | categórica | `E1`–`E8` | Preenchido apenas quando `decisao_triagem = excluido`; um único código, o de maior precedência |
| `revisor` | texto | iniciais | — |
| `nota` | texto | livre | Justificativa obrigatória para `duvida` e para toda divergência resolvida |

## 6 Vocabulário de temas (`tema_declarado`)

| Código | Tema | Abrange |
|---|---|---|
| T01 | Competência e atribuição tributária | Quem tributa o quê; desenho de bases; autonomia normativa |
| T02 | Transferências intergovernamentais | Incondicionais, condicionais, desenho de fórmulas |
| T03 | Equalização e desigualdade territorial | Capacidade fiscal, necessidade de gasto, redistribuição regional |
| T04 | Endividamento subnacional e restrição orçamentária | Bailout, regras de dívida, insolvência |
| T05 | Esforço e capacidade fiscal | Arrecadação própria, administração tributária, dependência de transferências |
| T06 | Competição e coordenação horizontal | Guerra fiscal, competição tributária, cooperação, consórcios |
| T07 | Descentralização de despesa e serviços | Saúde, educação, infraestrutura sob responsabilidade subnacional |
| T08 | Regras fiscais e governança | Responsabilidade fiscal, controle, transparência, contabilidade |
| T09 | Economia política do federalismo | Eleições, partidos, barganha federativa, ciclos políticos |
| T10 | Reformas tributárias e transição | Reformas do consumo, regimes de transição, mudanças constitucionais |
| T11 | Efeitos econômicos da descentralização | Crescimento, tamanho do governo, eficiência, corrupção |
| T12 | Dogmática e jurisdição constitucional fiscal | Decisão judicial sobre partilha, competência, imunidades |

Um tema novo só é criado se pelo menos **5** registros não couberem nos existentes; a criação é
registrada como emenda ao protocolo.

---

## 7 Tesauros de normalização

Arquivos em `config/`, formato JSON `{"variante": "FORMA CANÔNICA"}`, chaves em minúsculas.

| Arquivo | Função | Exemplo |
|---|---|---|
| `thesauro-termos.json` | Unifica palavras-chave entre idiomas e grafias | `"fiscal decentralisation" → "FISCAL DECENTRALIZATION"`; `"descentralização fiscal" → "FISCAL DECENTRALIZATION"` |
| `thesauro-fontes.json` | Unifica nomes de periódicos | `"nat tax j" → "NATIONAL TAX JOURNAL"` |
| `thesauro-instituicoes.json` | Unifica afiliações | `"univ fed pernambuco" → "UNIVERSIDADE FEDERAL DE PERNAMBUCO"` |
| `lexico-paises.json` | Mapeia topônimos de afiliação para país | `"brazil" → "BRA"`, `"brasil" → "BRA"` |

**Regra de ouro:** nenhuma normalização é feita direto no dado. Toda unificação passa pelo tesauro,
que é versionado — assim a decisão é auditável e reversível.

---

## 8 Precedência entre bases na deduplicação

Quando o mesmo trabalho aparece em mais de uma base, prevalecem os metadados na ordem:
**Scopus → Web of Science → Dimensions → Lens → SciELO**, exceto para:

- `citacoes`: prevalece o maior valor (com `fonte_citacoes` registrando a origem);
- `referencias`: prevalece a lista mais longa;
- `resumo`: prevalece o mais longo;
- `idioma` e `fonte` de registro lusófono: prevalece SciELO, cujos metadados nativos são mais fiéis.

A ordem é justificada pela completude do campo de referências e não implica juízo sobre a qualidade
das bases.
