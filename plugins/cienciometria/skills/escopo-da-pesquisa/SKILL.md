---
name: escopo-da-pesquisa
description: >-
  Conduz a conversa de delimitação que abre uma pesquisa cienciométrica ou uma revisão de
  literatura: descobre o que a pessoa quer investigar de fato, transforma isso em objeto delimitado,
  janela temporal justificada, perguntas de pesquisa e proposições com critério de refutação escrito
  antes de existir resultado, e grava tudo em config/revisao.json e no projeto de pesquisa. Use
  SEMPRE no começo de um projeto de revisão, e sempre que o usuário disser "quero pesquisar sobre
  X", "não sei delimitar meu tema", "meu orientador disse que o tema está amplo demais", "qual seria
  minha pergunta de pesquisa", "como transformo isso num projeto", "preciso definir os critérios de
  inclusão" ou trouxer um tema ainda vago para virar pesquisa. Use também para revisar um recorte já
  escrito que ficou largo, ambíguo ou sem hipótese verificável.
---

# Escopo da pesquisa

Esta é a etapa que decide a qualidade de todas as outras. String de busca, corpus, análise e
lacuna são consequências do recorte; recorte mal feito não se conserta depois, refaz-se.

E é conversa, não formulário. Quem chega com um tema costuma trazer um interesse, não um objeto —
o trabalho aqui é ajudar a pessoa a descobrir o que ela realmente quer saber.

## 1 Primeiro, o desvio mais caro

Antes de qualquer delimitação, descubra se o que a pessoa quer é **mapear o campo** (cienciometria:
quem publica, com quem, sobre o quê, citando quem) ou **saber o que a literatura concluiu** (revisão
sistemática ou integrativa de conteúdo). "Estado da arte" é dito com os dois sentidos, e descobrir
o engano na etapa da redação custa meses. Pergunte com um exemplo de resposta de cada tipo, não com
o nome dos métodos.

## 2 O objeto

O teste mais rápido para saber se o objeto está claro: peça **dois trabalhos que claramente entram**
e **dois que são parecidos mas ficam de fora**. Quem consegue dar os quatro tem objeto; quem não
consegue ainda tem um assunto.

Perguntas que fazem o recorte aparecer:

- Qual é a unidade de análise — pessoas, organizações, países, normas, tecnologias?
- O que caracteriza um trabalho como pertencente ao tema? A menção ao termo basta, ou é preciso que
  ele seja objeto e não contexto?
- Que vizinhanças ficam de fora, e por quê? (Toda delimitação é uma exclusão declarada.)
- O tema tem nome estável na literatura, ou várias tradições o chamam de coisas diferentes? Isso
  determina a estratégia de busca inteira.

## 3 A janela temporal

Toda janela precisa de razão declarada: um marco legal, uma virada teórica, um evento, a criação de
um periódico ou de uma política. "Últimos dez anos" não é razão, é hábito — e é a primeira coisa
que se pergunta numa banca. Se o marco é nacional e o corpus é internacional, diga isso: a janela
justificada num contexto pode ser arbitrária no outro.

## 4 Idiomas, bases e o que o usuário efetivamente acessa

Pergunte, não presuma. Duas armadilhas comuns:

- O **Portal de Periódicos da CAPES é meio de acesso, não base de busca** — busca-se *dentro* de
  Scopus, Web of Science ou SciELO por ele.
- Em temas brasileiros, as **bases nacionais decidem o resultado**: SciELO, SPELL (administração),
  LILACS e BVS (saúde), BDTD e o Catálogo de Teses da CAPES, e a literatura cinzenta institucional
  (IPEA, Fiocruz, Embrapa, ministérios). Sem acesso institucional a base paga, ainda dá para fazer
  pesquisa séria com OpenAlex, Crossref e as nacionais — o que muda é a cobertura, e isso vira
  limitação declarada, não segredo.

## 5 As perguntas

Cinco perguntas servem a qualquer revisão cienciométrica — volume e ritmo, distribuição de autores e
fontes, estrutura intelectual, estrutura social, estrutura conceitual. **A pergunta que interessa é a
sexta**: a que só esta pesquisa faz. Ela costuma nascer do incômodo que trouxe a pessoa até aqui —
uma suspeita sobre o campo, uma ausência que ela nota, uma comparação que ninguém fez. Vale insistir
até ela aparecer; sem ela, a revisão descreve o campo sem dizer nada que já não se soubesse.

## 6 As proposições

Cada proposição é uma afirmação verificável **com o critério que a derruba escrito antes de existir
resultado**. É isso que separa descrever um campo de confirmar a própria expectativa — e é o que
permite ao relatório dizer sozinho o que se sustentou.

No arquivo `config/revisao.json`:

```json
{"id": "P1",
 "enunciado": "A produtividade dos autores segue a Lei de Lotka",
 "indicador": "expoente α e teste KS",
 "criterio": {"tipo": "todos", "condicoes": [
    {"campo": "lotka.alpha", "operador": "entre", "valor": [1.7, 2.3]},
    {"campo": "lotka.adere", "operador": "==", "valor": true}]}}
```

Tipos de critério: `condicao`, `todos`, `algum` e `manual` (o que depende de leitura — relatado como
pendente, nunca como sustentado). Campos disponíveis: qualquer caminho de `saidas/resultados.json`,
como `bradford.zonas.0.artigos_%`, `colaboracao.coautoria_internacional_%`,
`coautoria.metricas.componente_gigante_%`, `copalavras.quadrantes.emergente_ou_declinio`. O formato
completo está em `docs/05-plano-de-analise.md`, §6.

Escreva de três a seis. Proposição que você não sabe como refutar não é proposição: é expectativa.

## 7 O que fica gravado

Dois lugares que precisam concordar entre si:

- `config/revisao.json` — o recorte em forma de máquina: `tema`, `janela`, `idiomas`,
  `tipos_documento`, `bases`, `periodos`, `codigos_exclusao`, `vocabulario_temas`, `proposicoes`.
- `docs/01-projeto-de-pesquisa.md` — o mesmo recorte em prosa, para humanos e para a banca.

Ao terminar, rode `cienciometria estado --revisao <slug>`: ele confirma se a etapa fechou e aponta a
seguinte. Enquanto os documentos ainda tiverem os marcadores «assim», a etapa continua aberta — e
o motor sabe disso.
