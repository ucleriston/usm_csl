---
description: Cria e configura uma nova revisão cienciométrica, conduzindo a delimitação do recorte
argument-hint: [tema da revisão]
---

O usuário quer iniciar uma revisão cienciométrica sobre: **$ARGUMENTS**

Siga a skill `revisao-cienciometrica`. Nesta etapa, especificamente:

1. Confirme antes de tudo se ele quer mapear **o campo** (cienciometria) ou sintetizar **o que a
   literatura concluiu** (revisão de conteúdo) — são coisas diferentes e a confusão entre elas é o
   erro mais caro no começo.
2. Converse para delimitar o recorte: o que caracteriza um trabalho como pertencente ao tema, o que
   fica de fora, a janela temporal e a razão dela, os idiomas, e **quais bases ele efetivamente
   acessa** (não presuma Scopus e Web of Science). Peça exemplos de trabalhos que claramente entram
   e de trabalhos parecidos que não entram — é o teste mais rápido do recorte.
3. Crie a revisão com `bin/cienciometria nova <slug> --titulo "..." --tema "..."`, rodando a partir
   da pasta de trabalho do usuário.
4. Preencha `config/revisao.json` com o recorte acordado e escreva as proposições com o critério que
   as refuta — antes de existir qualquer resultado.
5. Preencha `docs/01-projeto-de-pesquisa.md` com o mesmo recorte em prosa.

Ao final, mostre o que ficou configurado e diga qual é o próximo passo (montar as strings de busca,
com a skill `estrategia-de-busca`). Não invente dados nem preencha datas de corte ou contagens que
o usuário ainda não tem.
