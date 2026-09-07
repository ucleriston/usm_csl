# Protocolo da revisão — {{TITULO}}

**Versão:** 1.0 **Data:** _____ **Registro:** «depositar em OSF antes das buscas e anotar o DOI»

> O protocolo é escrito **antes** da coleta. Alteração posterior vira emenda datada na seção 10.

## 1 Tipo de revisão

Revisão cienciométrica, com identificação e triagem relatadas conforme PRISMA 2020 e buscas
conforme PRISMA-S. Não avalia risco de viés dos estudos primários: a unidade de análise é o
registro bibliográfico.

## 2 Perguntas

QP1 a QP6 do [projeto](01-projeto-de-pesquisa.md), §2.

## 3 Elegibilidade

### 3.1 Inclusão

| Dimensão | Critério |
|---|---|
| Objeto | «o que caracteriza o trabalho como pertencente ao tema» |
| Escopo temático | «subtemas que integram o objeto» |
| Período | Conforme `janela` em `config/revisao.json` |
| Tipo documental | Conforme `tipos_documento` |
| Idioma | Conforme `idiomas` |
| Revisão por pares | Veículo com revisão por pares declarada |

### 3.2 Exclusão

Os códigos abaixo devem ser os mesmos de `codigos_exclusao` em `config/revisao.json` — é por eles
que o fluxo PRISMA é contado.

| # | Critério |
|---|---|
| E1 | «fora do objeto — dimensão diversa» |
| E2 | «fora do objeto — unidade de análise diversa» |
| E3 | «fora do objeto — sem o componente central do tema» |
| E4 | Editorial, resenha, errata, carta, entrevista |
| E5 | Metadado insuficiente |
| E6 | Duplicata |
| E7 | Menção marginal ou metafórica |
| E8 | Texto integral indisponível |

### 3.3 Casos de fronteira — decisão pré-fixada

> Liste aqui as situações ambíguas que você já sabe que vão aparecer, com a decisão tomada de
> antemão. É o que evita decidir caso a caso depois de ver o resultado.

## 4 Fontes

| Base | Papel | Justificativa |
|---|---|---|
| «base» | principal / complementar | «por que entra» |

Fontes adicionais: *snowballing* sobre os mais citados; *hand search* nos periódicos da zona 1 de
Bradford; literatura institucional em corpus auxiliar, se pertinente ao tema.

## 5 Estratégia de busca

Ver [03-estrategias-de-busca.md](03-estrategias-de-busca.md). Regras invariáveis: busca em título,
resumo e palavras-chave; blocos combinados por `AND` e sinônimos por `OR`; data de corte única;
registro de cada execução em `config/execucao.json`; teste de recall do conjunto-semente antes da
execução definitiva.

## 6 Seleção

```
Identificação → Deduplicação → Triagem 1 (título/resumo) → Triagem 2 (texto integral) → Inclusão
```

Deduplicação automática com conferência humana da faixa de dúvida; triagem por dois revisores
independentes e cegos; kappa de Cohen ao fim de cada rodada, com o mínimo declarado em
`limiares.kappa_minimo`; divergência resolvida por consenso e, persistindo, por terceiro revisor;
calibração prévia em amostra de 100 registros.

## 7 Extração

Ver [04-livro-de-codigos.md](04-livro-de-codigos.md). Metadados por pipeline; variáveis de conteúdo
por leitura, com dupla codificação de 20% da amostra.

## 8 Fluxo PRISMA

Gerado por `python -m cienciometria prisma --revisao {{SLUG}}`.

## 9 Análise

Ver [plano de análise](../../../docs/05-plano-de-analise.md) e as proposições em
`config/revisao.json`.

## 10 Emendas

| Data | Seção | Alteração | Justificativa | Responsável |
|---|---|---|---|---|

## 11 Papéis

| Papel | Responsabilidade |
|---|---|
| Coordenação | Protocolo, escopo, redação final |
| Revisor 1 / Revisor 2 | Triagem independente, extração de conteúdo |
| Terceiro revisor | Desempate |
| Processamento | Pipeline, versionamento, integridade das saídas |

## 12 Verificação antes de fechar o corpus

- [ ] Data de corte em `config/execucao.json`
- [ ] Strings arquivadas com contagem de resultados
- [ ] Recall do conjunto-semente no mínimo exigido
- [ ] Kappa de calibração e das rodadas registrados
- [ ] Exclusões da triagem 2 com código
- [ ] Faixa de dúvida da deduplicação conferida
- [ ] Tesauros revisados
- [ ] Contagens do PRISMA fechando aritmeticamente
