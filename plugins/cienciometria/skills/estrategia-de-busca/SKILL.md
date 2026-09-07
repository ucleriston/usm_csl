---
name: estrategia-de-busca
description: >-
  Constrói, calibra e documenta strings de busca bibliográfica para Scopus, Web of Science, SciELO,
  Dimensions, Lens, OpenAlex, Crossref, PubMed e afins — blocos conceituais, sinônimos em português, inglês e espanhol,
  truncamento, operadores de proximidade, filtros por ano, tipo e idioma, teste de recall com
  conjunto-semente e registro conforme PRISMA-S. Use SEMPRE que o usuário pedir string de busca,
  estratégia de busca, termos de busca, expressão de pesquisa, descritores, operadores booleanos,
  "como faço essa busca na Scopus", "minha busca traz coisa demais/de menos", "como exporto os
  resultados dessa base" ou quando estiver montando o protocolo de uma revisão sistemática,
  integrativa, de escopo ou bibliométrica. Use também quando a busca já existir e o usuário quiser
  auditá-la, ampliá-la ou reduzir ruído.
---

# Estratégia de busca

Uma string mal construída não é um detalhe técnico: ela decide qual literatura existe para a
revisão. Erro aqui não aparece no resultado — aparece como ausência, que ninguém percebe.

## 1 Decompor o tema em blocos

Dois ou três blocos combinados por `AND`; dentro de cada bloco, sinônimos por `OR`.

| Bloco | Papel |
|---|---|
| B1 | Conceito central — o que o trabalho precisa tratar para pertencer ao tema |
| B2 | Qualificador, fenômeno ou teoria que restringe o conceito |
| B3 | Unidade de análise, população ou contexto |

Três blocos dão precisão; dois dão recall. Monte as duas versões, rode as duas, compare o ganho de
registros elegíveis da mais ampla — e relate a decisão, inclusive quando for descartá-la.

Para levantar sinônimos, três fontes valem mais que a memória: as palavras-chave dos trabalhos que
o usuário já conhece, os termos do tesauro da base quando houver (índice de assuntos, MeSH em
saúde) e as variações que aparecem nos títulos dos 20 primeiros resultados de um teste rápido.

Sinônimo, aqui, não é só a mesma palavra escrita de outro jeito: é **a tradição vizinha que estuda o
mesmo fenômeno com outro nome**. Quem busca resiliência e deixa `vulnerabilit*` e `adaptation` de
fora perde uma literatura inteira que responde à mesma pergunta; quem busca capacidade estatal e
ignora `bureaucratic quality` perde outra. Antes de fechar o bloco, pergunte-se que outra escola
chamaria isso de outra coisa.

## 2 Erros que custam caro

1. **Campo errado.** `TITLE-ABS-KEY` na Scopus, `TS=` na WoS. Só no título perde metade da
   literatura; no texto completo traz ruído incontrolável.
2. **Truncamento cedo demais.** `municipal*` recupera *municipality*, *municipalities*;
   `munic*` recupera *Munich*.
3. **Uma só grafia.** `decentralization` sem `decentralisation` perde sistematicamente a produção
   britânica — perda enviesada, não aleatória.
4. **Expressão sem aspas.** `fiscal federalism` sem aspas vira `fiscal AND federalism`.
5. **Termo genérico sozinho.** Palavras como *capacity*, *reform*, *governance* ou *federalism* só
   entram acompanhadas de outro bloco.
6. **Idioma único.** Se o tema tem produção em português ou espanhol, os termos entram nos mesmos
   blocos — e uma base regional entra na identificação, não como complemento.
7. **Sigla nacional na busca principal.** Siglas locais quebram a comparabilidade internacional;
   use-as depois, para recortar o corpus já formado.

## 3 Calibrar com conjunto-semente

Antes de valer, monte de 20 a 25 trabalhos que você e o usuário já sabem pertinentes — escolhidos
**antes** da busca, nunca depois de vê-los no resultado — e verifique quantos a string recupera.
Dentro do próprio Scopus dá para medir sem exportar nada: `( sua string ) AND ( DOI("10.x/a") OR
DOI("10.x/b") ... )` devolve quantas sementes a string alcança.
Menos de ~90% significa string incompleta: leia os que escaparam e descubra que termo faltou. É o
teste mais barato e o mais convincente na hora de defender a revisão.

## 6 Sintaxe por base

**Scopus**
```
TITLE-ABS-KEY ( ( "termo a" OR "termo b" ) AND ( termo* OR "termo c" ) )
AND PUBYEAR > 1989
AND ( LIMIT-TO ( DOCTYPE , "ar" ) OR LIMIT-TO ( DOCTYPE , "re" ) )
AND ( LIMIT-TO ( LANGUAGE , "English" ) OR LIMIT-TO ( LANGUAGE , "Portuguese" ) )
```
Exportar: `Export → CSV`, **todos** os campos, obrigatoriamente com *References*; lotes de 2.000.

**Web of Science**
```
TS = ( ( "termo a" OR "termo b" ) AND ( termo* ) )
```
Filtros na interface (anos, *Document Types*, idiomas). Exportar: *Plain Text — Full Record and
Cited References*, lotes de 500. É o formato que preserva as referências citadas.

**SciELO, Redalyc e interfaces menores** não suportam strings longas com o mesmo comportamento:
quebre em buscas simples, registre cada uma, exporte em RIS ou BibTeX.

**Dimensions e Lens**: busca em título e resumo, filtro por ano e tipo, exportação CSV completa.

**PubMed**: `("termo a"[tiab] OR "termo b"[tiab]) AND ("termo c"[MeSH Terms])`; exportar em RIS.

**OpenAlex e Crossref** são abertas e podem ser consultadas pelo próprio motor
(`cienciometria coletar --revisao <slug> --fonte openalex --busca "..." --email ...`), que pagina,
salva a resposta crua e registra a execução. É o caminho de quem não tem acesso institucional a
Scopus e WoS. Duas ressalvas para o relato: a busca por API tem processamento textual próprio e não
devolve o mesmo conjunto da interface do Scopus; e os "conceitos" do OpenAlex são atribuídos por
máquina, não são palavras-chave de autor.

**Google Scholar** não é base para corpus: não exporta de forma reprodutível e não tem controle de
tipo documental. Serve para conferir recall, e isso é tudo.

**Portal de Periódicos da CAPES é meio de acesso, não base de busca.** Quem tem acesso por ele
busca *dentro* de Scopus, Web of Science, SciELO ou Scopus/Elsevier — a busca federada do portal
não tem sintaxe estável nem exportação reprodutível. Dizer "busquei no Portal CAPES" numa seção de
métodos é declarar o caminho, não a fonte.

**Bases nacionais e regionais decidem temas brasileiros.** SciELO, SPELL (administração), LILACS e
BVS (saúde), BDTD e o Catálogo de Teses da CAPES (teses e dissertações), e a literatura cinzenta
institucional (IPEA, Fiocruz, Embrapa, ministérios) concentram parte relevante da produção que as
bases anglófonas não indexam. Nenhuma delas é coletável pela API do motor: a exportação é manual, em
RIS ou BibTeX, e entra em `dados/bruto/` como qualquer outra. Deixá-las de fora não é decisão
neutra — é decidir que aquela literatura não existe.

## 5 Registrar

Cada execução gera uma linha: base, identificador da string, data, hora, filtros, número de
resultados e arquivo salvo. Sem esse registro a busca não é repetível — e uma revisão que não pode
ser repetida não é sistemática, seja qual for o rótulo na capa.

Numa revisão criada por este plugin, o registro vai em `revisoes/<slug>/config/execucao.json` e a
string documentada em `docs/03-estrategias-de-busca.md`. Os arquivos exportados vão para
`revisoes/<slug>/dados/bruto/` **com o nome da base no arquivo** (`scopus_2026-04-10.csv`,
`wos_2026-04-10_01.txt`, `scielo_2026-04-10.ris`) — é assim que o motor escolhe o parser.

## 9 Quando a busca vem torta

| Sintoma | Causa provável | Correção |
|---|---|---|
| Resultado enorme, maioria irrelevante | Bloco genérico sozinho ou truncamento largo | Acrescentar bloco de contexto; fechar o truncamento |
| Resultado pequeno demais | Sinonímia pobre, idioma único, campo restrito ao título | Ampliar sinônimos; incluir outras línguas; usar título-resumo-palavras-chave |
| Sementes conhecidas não aparecem | Termo que a literatura usa e você não previu | Ler as palavras-chave das sementes perdidas e incorporá-las |
| Muita coisa de outra área com os mesmos termos | Ambiguidade lexical | Bloco de contexto disciplinar, ou filtro por área da base |
| Base sem campo de referências na exportação | Formato de exportação errado | Reexportar no formato completo; sem isso não há co-citação |
