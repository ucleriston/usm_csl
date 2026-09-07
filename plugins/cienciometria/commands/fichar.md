---
description: Escolhe os artigos-núcleo, cria as fichas de leitura e consolida as lacunas
argument-hint: [slug da revisão]
---

Conduza o fichamento da revisão **$ARGUMENTS**, seguindo a skill `fichamento`.

1. `bin/cienciometria fichar --revisao <slug> --sugerir` — mostre a lista com o critério de cada
   escolha e pergunte se o usuário quer acrescentar ou tirar algo. Os critérios cobrem pontos cegos
   diferentes: mais citados, recentes que já circulam, e um representante por agrupamento temático.
2. Crie as fichas (`--sugeridas`, ou `--id` uma a uma). Título, referência e palavras-chave já vêm
   do corpus; o resto exige a leitura do texto integral.
3. Se o usuário fornecer os PDFs ou os textos, ajude a preencher — mas resultados e contribuições
   escritos com as palavras dele, e o campo de lacunas extraído das páginas finais, que é onde os
   autores dizem o que falta. Nunca preencha a partir do resumo apenas.
4. `bin/cienciometria fichamentos --revisao <slug>` — consolide e leia a matriz de lacunas com o
   usuário: as que o corpus mostra já preenchidas saem da justificativa, e dizer isso no texto é
   sinal de domínio do campo.

O objetivo desta etapa não é resumir artigos: é chegar à lacuna que sustenta a pesquisa dele.
