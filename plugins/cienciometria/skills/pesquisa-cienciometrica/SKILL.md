---
name: pesquisa-cienciometrica
description: >-
  Conduz o projeto inteiro de pesquisa cienciométrica, do primeiro "quero pesquisar isso" até o
  artigo pronto, coordenando as demais etapas: escopo e proposições, protocolo, busca, corpus,
  triagem, análise, fichamento dos artigos-núcleo e redação do relatório final. Mantém o estado no
  disco, então a pesquisa continua de onde parou mesmo semanas depois, em outra conversa. Use SEMPRE
  que alguém quiser começar, retomar, acompanhar ou concluir uma pesquisa cienciométrica,
  bibliométrica ou um estado da arte sistemático — inclusive em pedidos como "quero pesquisar sobre
  X, por onde começo", "em que pé está minha revisão", "o que falta para eu escrever o artigo",
  "retoma aquele levantamento", "monta meu projeto de pesquisa a partir da literatura" ou "preciso
  achar a lacuna para justificar minha tese". É a skill de entrada: as demais são etapas dela.
---

# Pesquisa cienciométrica — condução do projeto inteiro

Esta é a skill mãe. Ela não faz o trabalho de cada etapa: ela sabe **onde a pesquisa está**, qual é
a próxima etapa e qual skill executa aquela etapa. As demais são especialistas convocados por ela.

## Por que o estado mora no disco

Uma revisão leva meses e atravessa dezenas de conversas. Se o estado morar na conversa, ele se perde
no primeiro dia seguinte. Por isso o estado é **inferido dos artefatos** da pasta da revisão: o que
está feito é o que existe no disco, não o que alguém lembra de ter feito. Isso tem uma consequência
prática que vale ouro: você pode retomar qualquer projeto, de qualquer usuário, sem precisar que
ele conte a história toda.

**A primeira coisa a fazer, sempre — inclusive quando o usuário só faz uma pergunta solta:**

```bash
CIENCIO="<raiz do plugin>/bin/cienciometria"     # ou "$CLAUDE_PLUGIN_ROOT/bin/cienciometria"
"$CIENCIO" listar                                # que revisões existem nesta pasta
"$CIENCIO" estado --revisao <slug>               # em que etapa está e o que falta
```

`estado` responde com as oito etapas, o que falta em cada uma, a etapa atual e o próximo passo
concreto. Comece por ele e termine por ele: rodar `estado` de novo ao fim de cada etapa mostra ao
usuário o que avançou.

## As oito etapas

| # | Etapa | Skill que executa | Está cumprida quando |
|---|---|---|---|
| E1 | Escopo e proposições | `escopo-da-pesquisa` | `config/revisao.json` tem tema, janela e proposições com critério de refutação; `docs/01` escrito |
| E2 | Protocolo | `triagem-e-prisma` | elegibilidade, códigos de exclusão e procedimento de triagem definidos |
| E3 | Busca | `estrategia-de-busca` | strings documentadas, conjunto-semente montado, execuções registradas com data de corte |
| E4 | Corpus | `revisao-cienciometrica` | registros importados e deduplicados |
| E5 | Triagem | `triagem-e-prisma` | decisões preenchidas e concordância medida |
| E6 | Análise | `interpretar-resultados` | indicadores, redes e relatório gerados |
| E7 | Fichamento | `fichamento` | artigos-núcleo lidos e fichados, lacunas declaradas consolidadas |
| E8 | Artigo | `relatorio-cienciometrico` | rascunho gerado com os números da análise e escrito pelo autor |

Para executar uma etapa, carregue a skill correspondente (ela traz o detalhe que esta não repete) e
volte para cá ao terminar.

## A ordem importa, e o motivo de cada dependência

Não é burocracia de fluxo: cada etapa produz a matéria-prima da seguinte, e pular uma faz a seguinte
sair oca.

- **Escopo antes de busca.** String de busca é a tradução operacional de um recorte. Sem recorte
  decidido, a string é chute, e o corpus vira o que o acaso trouxe.
- **Protocolo antes de corpus.** Critério escrito depois de ver os resultados não é critério, é
  racionalização — e é o primeiro ponto que um parecerista testa.
- **Análise antes de fichamento.** É a análise que diz *quais* artigos ler: os mais citados, os mais
  centrais em cada agrupamento, os recentes que já circulam. Ler por conveniência reproduz o cânone
  que a pessoa já conhecia.
- **Fichamento antes do artigo.** Aqui está o ponto que a maioria dos projetos erra. A cienciometria
  mostra a *forma* do campo — quem publica, com quem, sobre o quê. Ela não diz o que os trabalhos
  afirmam nem o que eles próprios apontam como não resolvido. **A lacuna que justifica uma pesquisa
  nova sai da leitura**, e o fichamento é o que torna essa leitura comparável entre artigos. Escrever
  a introdução sem fichamento produz o parágrafo genérico que todo parecerista reconhece: "poucos
  estudos abordam o tema", sem dizer quem disse isso, quando, e se continua verdade.

Quando o usuário quiser pular uma etapa, diga o que ele perde e siga se ele confirmar — é a pesquisa
dele. Registre o pulo como decisão declarada, não como omissão.

## Começando do zero

```bash
"$CIENCIO" nova <slug> --titulo "..." --tema "..."
```

Rode a partir da pasta de trabalho do usuário: a revisão é criada em `./revisoes/<slug>/`, nunca
dentro da instalação do plugin. Depois vá para a skill `escopo-da-pesquisa` — a conversa de
delimitação é a etapa mais determinante do projeto inteiro, e a que menos tolera pressa.

## Retomando

Se o usuário volta depois de semanas, não pergunte o que ele fez: `estado --revisao <slug>` conta.
Mostre o quadro, diga qual é a etapa atual e ofereça o próximo passo. Se houver mais de uma revisão,
`listar` mostra todas com a data de corte e se o corpus já existe.

## Regras que valem em todas as etapas

- **Dado inventado, nunca.** Nem registro bibliográfico, nem contagem de base, nem data de corte,
  nem kappa, nem citação. Se falta, falta — e dizer isso é a resposta certa.
- **Número do relatório vem do motor.** O rascunho do artigo é gerado por `artigo`, que lê
  `saidas/resultados.json`. Número digitado à mão no texto é erro esperando para acontecer.
- **Cobertura declarada.** Todo indicador que dependa de campo incompleto sai com a cobertura ao
  lado.
- **Critério antes do resultado.** As proposições, com a condição que as refuta, ficam escritas em
  `config/revisao.json` antes de existir análise.
- **Exemplo com número fabricado nunca sai em formato de entrega.** Se precisar demonstrar um
  formato, o aviso vai dentro do próprio arquivo.
- **Não afirme verificação que não fez.** "Conferi que roda" só vale se você rodou e viu a saída.

## Quando o pedido não é este

Se o usuário quer saber **o que a literatura concluiu** sobre um tema, ele quer revisão sistemática
ou integrativa de conteúdo, não cienciometria. Diga a diferença logo no início: aqui o corpus e a
triagem ajudam, mas a síntese dos achados é leitura, não indicador. Muita gente pede "estado da
arte" querendo a primeira coisa, e descobrir isso na etapa 8 custa meses.
