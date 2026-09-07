---
description: Gera o rascunho do artigo com os números da análise e conduz a redação
argument-hint: [slug da revisão]
---

Monte o relatório final da revisão **$ARGUMENTS**, seguindo a skill `relatorio-cienciometrico`.

1. Antes de tudo, `bin/cienciometria estado --revisao <slug>`. Se o fichamento não estiver feito,
   diga por que ele vem antes: a introdução e a discussão dependem da leitura dos artigos-núcleo, e
   sem ela a justificativa sai genérica.
2. `bin/cienciometria artigo --revisao <slug>` gera `saidas/artigo.md` com todos os números no
   lugar, `[ESCREVER: ...]` no que depende do autor e `[SEM DADO: ...]` no que o pipeline não
   produziu.
3. Conduza a escrita seção por seção. Todo número vem das saídas; nenhum é digitado à mão. Cada
   `[SEM DADO]` é uma etapa a reexecutar, não um valor a estimar.
4. Pergunte pelo modelo do periódico ou do programa antes de formatar, e adapte a estrutura. Para
   entregar em Word, use a skill `docx` a partir do Markdown já escrito.

Feche pela lista de verificação da skill — marcações resolvidas, rótulos validados por leitura,
proposições refutadas relatadas, limitações declaradas.
