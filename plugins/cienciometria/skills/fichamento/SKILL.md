---
name: fichamento
description: >-
  Ficha artigos científicos em campos fixos e comparáveis — referência, objetivos, conceitos,
  autores do referencial, método (estratégia, contexto, amostra, coleta, análise), resultados,
  contribuições, lacunas apontadas pelos autores e citações extraídas — e consolida as lacunas
  declaradas num quadro que as confronta com o corpus, mostrando quais continuam abertas. Use SEMPRE
  que o usuário disser fichar, fichamento, ficha de leitura, resumo estruturado de artigo, "li esses
  artigos e preciso organizar", "preciso extrair a lacuna da literatura", "como justifico minha
  pesquisa a partir do que já existe", "monta a matriz de leitura", "quais artigos eu leio primeiro"
  ou estiver preparando a introdução, o referencial teórico ou a justificativa de um projeto,
  dissertação, tese ou artigo. É a etapa entre a análise cienciométrica e a redação do relatório.
---

# Fichamento

A análise cienciométrica mostra a **forma** do campo: quem publica, com quem, sobre o quê, citando
quem. Ela não diz o que os trabalhos afirmam, nem o que eles próprios apontam como não resolvido.
A lacuna que justifica uma pesquisa nova sai da leitura — e o fichamento é o que torna essa leitura
comparável entre artigos, em vez de virar um monte de anotações que só quem leu entende.

## 1 Quais artigos ler

Ler por conveniência reproduz o cânone que a pessoa já conhecia. O motor propõe uma lista com o
critério de cada escolha:

```bash
"$CIENCIO" fichar --revisao <slug> --sugerir
```

Três critérios, porque cada um cobre o ponto cego do outro: **os mais citados** (o que o campo
consagrou), **os recentes que já circulam** (o que está em curso e ainda não acumulou citação) e
**um representante por agrupamento temático** (o que a leitura por citação esconderia, porque
comunidades periféricas citam pouco).

A escolha final é do pesquisador. Acrescente o que ele souber ser central mesmo sem aparecer na
lista, e diga por quê — isso vira uma linha do método.

Dez a quinze fichas costumam bastar para sustentar uma introdução. Menos que isso não mostra padrão;
mais que isso, sem novidade nas últimas fichas, é sinal de saturação — e saturação é um resultado
a relatar, não um trabalho a continuar.

```bash
"$CIENCIO" fichar --revisao <slug> --sugeridas      # cria as fichas de toda a lista
"$CIENCIO" fichar --revisao <slug> --id <id>        # ou uma a uma
```

Cada ficha nasce com título, referência e palavras-chave já preenchidos a partir do corpus. O resto
exige leitura.

## 2 Os campos, e o que cada um cobra

| Campo | O que registrar | Erro comum |
|---|---|---|
| Objetivos | O que o artigo se propôs a fazer, na formulação dele | Confundir objetivo com tema |
| Conceitos | Os conceitos que ele mobiliza e como os define | Listar palavras-chave em vez de conceitos |
| Autores do referencial | Em quem ele se apoia | Copiar a lista de referências inteira |
| Método | Estratégia, contexto, amostra, coleta e análise | Escrever "qualitativo" e parar |
| Resultados | O que ele encontrou, **com suas palavras** | Colar o resumo do artigo |
| Contribuições | O que ele acrescenta ao campo, com suas palavras | Repetir os resultados |
| Lacunas | O que os próprios autores dizem que falta, em geral no fim do texto | Pular — é o campo que mais importa aqui |
| Termos da lacuna | Dois a quatro termos que a nomeiam | Deixar em branco: sem isso a lacuna não é conferível |
| Citações | Trechos que você vai citar, **com página** | Anotar sem página e ter de reler depois |

Duas exigências que fazem a ficha valer:

**Com suas palavras.** Resultados e contribuições reescritos por você mostram se você entendeu; o
resumo colado só mostra que o arquivo foi aberto. Quando for citar literalmente, use aspas e página.

**Da leitura do texto, não do resumo.** As lacunas costumam estar nas últimas páginas, e o resumo
quase nunca as traz. Ficha feita a partir do resumo produz uma justificativa genérica, que é
exatamente o que se quer evitar.

## 3 Consolidar e conferir

```bash
"$CIENCIO" fichamentos --revisao <slug>
```

Gera `saidas/fichamentos.csv` (todas as fichas em tabela, com o que falta em cada uma) e
`saidas/matriz-de-lacunas.csv` — o quadro que faz o trabalho pesado.

**A ideia central da matriz:** quando um autor escreve "faltam estudos sobre X", ele fez uma
afirmação verificável. O motor conta em quantos registros do corpus os termos daquela lacuna
aparecem. Se X está em 40% do corpus, a lacuna foi preenchida depois daquela publicação — e usá-la
como justificativa é o erro que o parecerista encontra primeiro. Se X aparece em 2%, você tem
evidência, não impressão.

É por isso que o campo "termos da lacuna" existe e não pode ficar vazio.

## 4 Da matriz para a justificativa

O que a matriz entrega é matéria-prima, não texto. O caminho:

1. **Agrupe** lacunas que dizem a mesma coisa com palavras diferentes — a repetição entre autores é
   o que dá força ao argumento.
2. **Descarte** as que o corpus mostra preenchidas, e diga isso no texto: "X foi apontado como
   lacuna por Fulano (2015), mas passou a ser tratado em N trabalhos desde então" é uma frase forte,
   que mostra domínio do campo.
3. **Cruze** o que sobrou com o mapa temático da análise. Lacuna declarada por autores **e** situada
   num quadrante periférico é o achado mais defensável que uma revisão produz.
4. **Prefira a lacuna relacional.** "Ninguém estudou X" é frágil e quase sempre falso. "X é estudado
   no agrupamento A, Y no agrupamento B, e os dois não se citam" é verificável no próprio dado.

## 5 Onde isso desemboca

As lacunas consolidadas entram no rascunho do artigo automaticamente, no parágrafo 3 da introdução
(`cienciometria artigo`), com a conferência ao lado. A redação continua sendo sua — o que o motor
faz é impedir que a justificativa seja escrita sem lastro.
