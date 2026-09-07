---
description: Mostra em que etapa a pesquisa está e conduz o próximo passo
argument-hint: [slug da revisão]
---

Verifique o estado da pesquisa **$ARGUMENTS** e conduza o próximo passo, seguindo a skill
`pesquisa-cienciometrica`.

1. Se o slug não foi informado, rode `bin/cienciometria listar` e pergunte qual revisão.
2. Rode `bin/cienciometria estado --revisao <slug>` e mostre o quadro ao usuário: o que está feito,
   o que falta e qual é a etapa atual.
3. Carregue a skill que executa a etapa atual e conduza-a até o fim.
4. Rode `estado` de novo e mostre o que avançou.

Não pule etapa sem avisar o que se perde com isso. Se o usuário insistir, siga — a pesquisa é dele —
mas registre o pulo como decisão declarada.
