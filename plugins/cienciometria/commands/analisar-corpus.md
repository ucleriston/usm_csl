---
description: Roda o pipeline cienciométrico sobre uma revisão e resume os achados
argument-hint: [slug da revisão]
---

Rode a análise da revisão **$ARGUMENTS** (se o slug não foi informado, liste as revisões
disponíveis com `bin/cienciometria listar` e pergunte qual).

1. Confira antes se há exportações em `revisoes/<slug>/dados/bruto/` e se `config/execucao.json`
   traz a data de corte declarada. Faltando a data, avise: o relatório sai marcado como não
   declarada, e isso precisa ser corrigido antes de qualquer uso do resultado.
2. Rode `bin/cienciometria analise --revisao <slug>`.
3. Confira as três coisas que costumam esconder problema: registros por arquivo em
   `dados/processado/importacao.csv`, os pares ambíguos em `revisao-duplicatas.csv` e a cobertura do
   subcorpus com referências (afeta toda a análise de co-citação).
4. Leia `saidas/relatorio.md` e resuma para o usuário, em poucos parágrafos: tamanho e janela do
   corpus, concentração de fontes e autores, o que as redes mostram, quantos agrupamentos temáticos
   surgiram e como ficaram as proposições.

Seja explícito sobre o que os números **não** sustentam, e trate os rótulos automáticos de
agrupamento como provisórios — eles só valem depois da leitura dos itens centrais, com a skill
`interpretar-resultados`.
