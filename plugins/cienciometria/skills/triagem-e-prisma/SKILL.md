---
name: triagem-e-prisma
description: >-
  Conduz a seleção de estudos de uma revisão: critérios de elegibilidade que decidem sozinhos,
  códigos de exclusão, triagem dupla cega por título/resumo e por texto integral, medida de
  concordância entre revisores (kappa de Cohen), resolução de divergências e montagem do fluxo
  PRISMA com as contagens reais. Use SEMPRE que o usuário falar em triagem, screening, seleção de
  artigos, critérios de inclusão e exclusão, elegibilidade, PRISMA, fluxograma da revisão, kappa,
  concordância entre avaliadores, "quantos artigos sobraram", "como justifico as exclusões",
  "preciso do diagrama da revisão" ou estiver preparando o protocolo de uma revisão sistemática,
  integrativa, de escopo ou bibliométrica. Use também quando pedirem para auditar uma triagem já
  feita ou para reconstruir o fluxo PRISMA de números já existentes.
---

# Triagem e fluxo PRISMA

A triagem é onde a revisão ganha ou perde credibilidade. O que a torna defensável não é o rigor
declarado, é a possibilidade de outra pessoa refazer o percurso e chegar ao mesmo lugar.

## 1 Critérios que decidem sozinhos

Teste cada critério assim: *dois revisores aplicam ao mesmo registro, sem conversar, e chegam à
mesma resposta?* Se não, ele está ambíguo e vai gerar divergência que nenhuma discussão resolve.

Segundo teste, igualmente útil: *dá para decidir só com título, resumo e palavras-chave?* Se não
dá, o critério pertence à triagem 2 (texto integral) — e isso precisa estar escrito, porque aplicar
na etapa errada é a causa mais comum de exclusão indevida.

Critérios de exclusão são **códigos numerados** (E1, E2, …), e cada registro excluído recebe um
único código: o de maior precedência na ordem em que estão listados. É por eles que o fluxo PRISMA
conta as perdas — sem código, a contagem não fecha e não há o que relatar.

Liste também os **casos de fronteira** com a decisão tomada de antemão. Todo tema tem zona cinzenta;
decidir depois de ver o resultado é o caminho curto para o viés de confirmação.

## 2 O procedimento

```
Identificação → Deduplicação → Triagem 1 (título/resumo) → Triagem 2 (texto integral) → Inclusão
```

- **Calibração antes de começar:** os dois revisores triam a mesma amostra de ~100 registros. Se a
  concordância já for baixa aí, o problema é o critério, e reescrevê-lo agora custa uma tarde;
  descobrir depois custa a revisão.
- **Cegueira entre revisores:** cada um preenche a sua coluna sem ver a do outro. Planilha
  compartilhada com as duas colunas visíveis não é triagem dupla, é conferência.
- **Divergências:** consenso; persistindo, um terceiro decide. Toda divergência resolvida fica
  registrada com a razão — é o que mostra que o critério foi aplicado, e não improvisado.
- **Revisor único:** quando não houver segunda pessoa (comum em pesquisa individual), diga isso ao
  usuário com franqueza e ofereça o segundo melhor: recodificar uma amostra de 20% depois de alguns
  dias e relatar a concordância intrarrevisor. Registre a escolha como limitação em vez de omiti-la.

## 3 Kappa de Cohen

O kappa corrige a concordância pelo acaso: dois revisores que incluem tudo concordam 100% do tempo
e não demonstram nada. Referência usual de leitura:

| Kappa | Leitura |
|---|---|
| < 0,20 | insignificante |
| 0,20–0,39 | sofrível |
| 0,40–0,59 | moderada |
| 0,60–0,74 | substancial |
| ≥ 0,75 | quase perfeita |

Kappa abaixo do mínimo declarado no protocolo significa **critério mal escrito**. A resposta é
reescrever o critério, registrar a emenda e refazer a rodada — não negociar registro a registro até
os números baterem. E kappa ruim relatado é limitação; kappa não medido é falha metodológica.

Com o plugin:

```bash
"$CIENCIO" triagem --revisao <slug>     # planilha cega: decisao_r1 e decisao_r2 separadas
"$CIENCIO" kappa   --revisao <slug> --triagem <arquivo preenchido>
```

O comando também aponta decisões inválidas (qualquer coisa fora de `incluido`, `excluido`,
`duvida`) e lista os registros divergentes para o desempate.

## 4 Fluxo PRISMA

```bash
"$CIENCIO" prisma --revisao <slug>
```

Gera as contagens a partir do que realmente aconteceu no pipeline — identificados por base,
duplicatas removidas (por DOI, por título e ano, por similaridade), triados, excluídos por código e
incluídos — e escreve `saidas/prisma.md`.

Duas conferências antes de publicar o diagrama:

1. **A aritmética fecha?** Identificados − duplicatas − excluídos = incluídos. Se não fecha, há
   registro sem decisão ou exclusão sem código.
2. **As perdas estão explicadas?** Cada código de exclusão com a sua contagem. Um "outros" grande
   é sinal de que faltou um critério no protocolo.

Se o usuário já tem os números de uma revisão feita fora do plugin e quer só o diagrama, monte-o com
os números dele — sem completar lacuna com estimativa. Número que ninguém contou não entra no
fluxograma.

## 5 Extração depois da inclusão

Separe o que o pipeline extrai (metadados: autoria, ano, fonte, citações) do que exige leitura
(abordagem, tema, população, país do caso). Para o que exige leitura, defina domínio fechado e
recodifique 20% em duplicata — sem isso, a codificação de conteúdo é impressão, não dado.
