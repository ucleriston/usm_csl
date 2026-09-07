---
name: interpretar-resultados
description: >-
  Interpreta e redige os resultados de uma análise bibliométrica: o que Lotka, Bradford, índice de
  Price, h-index e índice de colaboração realmente dizem, como rotular agrupamentos de co-citação e
  de co-palavras, como ler o mapa temático de Callon (motores, básicos, nicho, emergentes), o que
  cada rede sustenta e o que não sustenta, e como escrever a seção de resultados sem extrapolar.
  Use SEMPRE que o usuário perguntar o que significam os clusters, o mapa, os quadrantes, o alfa de
  Lotka, as zonas de Bradford ou os números do relatório bibliométrico; quando pedir para escrever,
  revisar ou discutir a seção de resultados de uma revisão bibliométrica; quando disser "o
  VOSviewer me deu esses grupos e não sei o que fazer", "como transformo isso em texto de artigo",
  "quais lacunas isso mostra" ou "o revisor pediu para eu interpretar melhor os achados".
---

# Interpretar e escrever os resultados

Indicadores bibliométricos descrevem padrões de publicação e citação. Quase todo erro grave de
interpretação nasce de tratá-los como medida de qualidade, de influência causal ou de concordância
intelectual. Esta skill existe para manter a leitura no que os dados sustentam — que já é bastante.

## 1 O que cada indicador diz, e o que não diz

| Indicador | Diz | Não diz |
|---|---|---|
| Produção anual, TCAC | Ritmo de crescimento da literatura indexada | Que o campo amadureceu ou se consolidou |
| Lei de Lotka (α) | Concentração da produtividade: núcleo pequeno, franja larga | Quem são os autores importantes |
| Lei de Bradford | Onde a literatura se concentra; onde publicar e onde procurar | Que os periódicos da zona 1 sejam os melhores |
| Citações, h-index | Visibilidade e circulação dentro do que a base indexa | Qualidade, correção ou impacto social |
| Índice de Price, meia-vida | Quanto o campo se apoia em literatura recente | Se o campo é inovador ou datado |
| Coautoria internacional (MCP) | Integração das comunidades | Qualidade da colaboração |
| Co-citação | Que dois trabalhos são lidos juntos pela comunidade | Que concordem entre si — pares em disputa aberta são co-citados o tempo todo |
| Acoplamento bibliográfico | Que dois trabalhos partem da mesma base de leitura | Que cheguem a conclusões parecidas |
| Co-palavras | Vizinhança de vocabulário declarado pelos autores | Vizinhança conceitual real, se a terminologia for instável |

Duas advertências que valem para o texto inteiro. **Ausência não é inexistência:** o que não aparece
pode não estar indexado, sobretudo produção não anglófona, livros e literatura institucional.
E **citação recente é sempre subestimada:** trabalhos dos últimos dois anos ainda não acumularam
citações, então rankings puros por citação premiam a idade — relate também citações por ano.

## 2 Rotular agrupamentos

O motor nomeia cada agrupamento pelo item mais frequente. Isso é pista, não rótulo. Para nomear de
verdade:

1. Abra `saidas/<rede>_nos.csv`, ordene pelo agrupamento e pegue os 10 itens de maior frequência.
2. Leia os títulos e resumos desses itens no corpus (`dados/processado/corpus.csv`).
3. Pergunte o que os une: um objeto, um método, uma tradição teórica, um recorte geográfico? O
   rótulo deve responder a isso em três a cinco palavras.
4. Confira o contraexemplo: existe item central que o rótulo não cobre? Então o rótulo está largo
   demais, ou o agrupamento mistura duas coisas — e isso também é achado.

Agrupamento com menos de ~5 itens em geral não sustenta rótulo próprio; trate como periferia ou
funda-o ao vizinho, dizendo que fez isso.

## 3 Ler o mapa temático

O mapa cruza **centralidade** (quanto o tema se liga aos outros) com **densidade** (quanto ele é
internamente coeso). Os quatro quadrantes:

| Quadrante | Centralidade | Densidade | Leitura |
|---|:-:|:-:|---|
| Motor | alta | alta | Tema desenvolvido e conectado — o núcleo do campo |
| Básico ou transversal | alta | baixa | Tema que atravessa tudo, ainda pouco estruturado em si |
| Nicho | baixa | alta | Comunidade coesa e isolada — especialidade que não conversa |
| Emergente ou em declínio | baixa | baixa | Ambíguo por natureza: só a série temporal distingue |

O último quadrante é onde mais se erra. Emergente e em declínio ocupam o mesmo lugar no mapa; para
separá-los, olhe a evolução por subperíodo (`saidas/evolucao_tematica.csv`): termo que cresce entre
os dois últimos períodos é emergente; termo que encolhe está saindo de cena. Sem essa checagem, não
afirme nem uma coisa nem outra.

## 4 Lacunas: as que existem e as que não existem

Lacuna é a afirmação mais forte de uma revisão e a mais fácil de errar. Antes de declarar uma:

- **Confira se é lacuna ou é cegueira da busca.** Tema ausente pode significar string que não o
  alcança, base que não o cobre ou idioma fora do recorte. Teste rápido: uma busca direta pelo tema
  na base; se aparecer literatura que o corpus não pegou, o problema é a string.
- **Distinga "pouco estudado" de "estudado em outro lugar".** Muitos temas migram para revistas de
  outra área — a lacuna é do campo mapeado, não do conhecimento.
- **Prefira a lacuna relacional.** "Ninguém estudou X" é frágil e quase sempre falso. "X é estudado
  no agrupamento A e Y no agrupamento B, e os dois não se citam" é verificável no próprio dado, e é
  o tipo de achado que só uma revisão cienciométrica produz.

## 5 Escrever a seção de resultados

Uma ordem que funciona, do panorama ao específico:

1. **Corpus e fluxo** — quantos registros, de quais bases, com data de corte, e o PRISMA.
2. **Desempenho** — produção no tempo, fontes, autores, países, impacto. Poucos números no texto;
   o resto em tabela.
3. **Estrutura intelectual** — co-citação: as tradições que o campo compartilha.
4. **Estrutura social** — colaboração: quem produz com quem, e o que a fragmentação sugere.
5. **Estrutura conceitual** — co-palavras e mapa temático, com os rótulos que você validou lendo.
6. **Evolução** — o que mudou entre os subperíodos.
7. **Proposições** — o que se sustentou e o que se refutou, incluindo o que contraria a expectativa
   inicial. Refutação relatada é sinal de desenho honesto, e revisor experiente lê assim.
8. **Limitações** — cobertura das bases, campos incompletos, homonímia de autores, decisões de
   limiar. Toda revisão tem; a que não declara nenhuma é a menos confiável.

Ao escrever, ancore cada afirmação num número que existe nas saídas, e nomeie a fonte dele
("segundo a rede de co-citação, com cobertura de 78% do corpus"). Adjetivo sem número —
"crescimento expressivo", "forte concentração" — é o que o parecerista corta primeiro.

## 6 Frases que costumam estar erradas

| Frase | Problema | Substituir por |
|---|---|---|
| "Os autores mais citados são os mais influentes do campo" | Citação mede circulação, não influência | "Os mais citados no corpus, na data de corte, são…" |
| "O agrupamento mostra uma corrente teórica unificada" | Co-citação não implica concordância | "Trabalhos lidos em conjunto pela comunidade, incluindo posições divergentes" |
| "O tema X é emergente" (só pelo mapa) | Quadrante não distingue emergente de declínio | Confirmar com a série por subperíodo |
| "Não há pesquisa sobre Y" | Pode ser limite da busca | "Não há, no corpus recuperado por esta estratégia, trabalhos que…" |
| "A produção cresceu 300%" | Base pequena infla percentual | Dar os números absolutos ao lado |
| "O país X lidera a pesquisa mundial" | Contagem integral favorece coautoria numerosa; bases favorecem o inglês | Relatar contagem fracionária e a limitação de cobertura |
