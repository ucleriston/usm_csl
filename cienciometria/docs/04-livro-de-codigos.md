# Livro de códigos do motor — variáveis comuns a qualquer revisão

As variáveis abaixo são preenchidas automaticamente pelo pipeline e existem em toda revisão. O que
é específico do tema — variáveis de conteúdo, vocabulário temático e tesauros — fica no livro de
códigos da própria revisão.

## 1 Identificação

| Variável | Origem | Regra |
|---|---|---|
| `id` | automática | `<base>:<arquivo>:<n>`, estável após a deduplicação |
| `doi` | automática | Minúsculas, sem prefixo de URL |
| `base_origem` | automática | Base de onde vieram os metadados que prevaleceram |
| `bases_todas` | automática | Todas as bases em que o registro apareceu |
| `id_externo` | automática | Identificador na fonte aberta (`openalex:W123`, `doi:10.x/y`). Torna a co-citação exata quando a fonte entrega referências por identificador, em vez de casá-las por autor e ano |
| `titulo`, `titulo_norm` | automática | O normalizado (sem acento e pontuação) serve só à deduplicação |

## 2 Autoria e afiliação

| Variável | Regra |
|---|---|
| `autores` | `Sobrenome, I.`; partículas (`de`, `da`, `van`, `del`) integram o sobrenome |
| `n_autores` | Contagem |
| `orcid` | Quando disponível — base da desambiguação |
| `afiliacoes` | Texto íntegro da base |
| `instituicoes` | Normalizadas pelo tesauro de instituições |
| `paises` | ISO-3, extraídos da afiliação pelo léxico de países (comum a todas as revisões) |
| `colab_internacional` | 1 quando há dois ou mais países distintos |

## 3 Publicação e impacto

| Variável | Regra |
|---|---|
| `ano`, `fonte`, `issn`, `tipo_documento`, `idioma`, `editora`, `volume`, `numero`, `paginas` | Da base; `fonte` normalizada pelo tesauro |
| `citacoes` | Maior valor entre as bases; a origem fica em `fonte_citacoes` |
| `citacoes_por_ano` | `citacoes / (ano_corte - ano + 1)` |
| `referencias`, `n_referencias` | Vazio quando a base não fornece — a cobertura é declarada no relatório |

## 4 Triagem

| Variável | Domínio |
|---|---|
| `decisao_triagem` | `incluido`, `excluido`, `duvida` |
| `codigo_exclusao` | Um código de `codigos_exclusao` da revisão |
| `revisor`, `nota` | Justificativa obrigatória em dúvidas e divergências |

## 5 Precedência entre bases na deduplicação

Quando o mesmo trabalho aparece em mais de uma base, os metadados seguem a ordem declarada em
`precedencia_bases`, com quatro exceções fixas:

- `citacoes`: prevalece o **maior** valor;
- `referencias`: prevalece a lista **mais longa**;
- `resumo`: prevalece o **mais longo**;
- registro de base regional em português ou espanhol: prevalecem `idioma` e `fonte` dela, cujos
  metadados nativos são mais fiéis.

## 6 Tesauros

| Arquivo | Escopo |
|---|---|
| `config/lexico-paises.json` (raiz) | Comum a todas as revisões |
| `revisoes/<slug>/config/thesauro-termos.json` | Palavras-chave do tema |
| `revisoes/<slug>/config/thesauro-fontes.json` | Periódicos |
| `revisoes/<slug>/config/thesauro-instituicoes.json` | Afiliações |

O motor carrega o da raiz e sobrepõe o da revisão. Chaves em minúsculas e sem acento; valor é a
forma canônica. **Nenhuma normalização é feita direto no dado** — assim toda unificação fica
auditável e reversível.
