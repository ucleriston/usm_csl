# Guia de buscas — construindo a string para qualquer tema

Relato conforme PRISMA-S. O modelo preenchível fica em cada revisão
(`revisoes/<slug>/docs/03-estrategias-de-busca.md`).

## 1 A string em blocos

Decomponha o tema em dois ou três blocos conceituais e combine-os por `AND`; dentro de cada bloco,
sinônimos por `OR`.

| Bloco | O que é | Exemplo (tema: capacidade estatal municipal) |
|---|---|---|
| B1 | Conceito central | `"state capacity" OR "capacidade estatal" OR "administrative capacity"` |
| B2 | Qualificador ou fenômeno | `bureaucra* OR "public administration" OR "gestão pública"` |
| B3 | Unidade de análise ou contexto | `municipal* OR "local government*" OR município*` |

Três blocos dão precisão; dois dão recall. Rode as duas versões e relate o ganho marginal da mais
ampla — inclusive quando a decisão for descartá-la.

## 2 Regras que evitam os erros mais comuns

1. **Campo certo.** `TITLE-ABS-KEY` no Scopus, `TS=` na WoS. Buscar só no título perde metade da
   literatura; buscar no texto completo traz ruído incontrolável.
2. **Truncamento consciente.** `municipal*` pega *municipality*, *municipalities*, *municipal*.
   Truncar cedo demais (`munic*`) traz *Munich*.
3. **Grafias britânica e americana sempre juntas.** `decentrali?ation`, ou as duas formas por `OR`.
   Esquecer uma delas é perda sistemática, não aleatória.
4. **Três idiomas, se o tema os tiver.** Termos em português e espanhol dentro dos mesmos blocos.
5. **Aspas em expressões.** Sem aspas, `fiscal federalism` vira `fiscal AND federalism`.
6. **Termo genérico sozinho, nunca.** Palavras como *federalism*, *capacity* ou *reform* só entram
   acompanhadas de outro bloco.
7. **Siglas nacionais fora da busca principal.** Elas quebram a comparabilidade internacional; use-as
   depois, para recortar o corpus já formado.

## 3 Teste de recall antes de valer

Monte um conjunto-semente de 20 a 25 trabalhos que você já sabe pertinentes — escolhidos **antes**
da busca — e verifique quantos a string recupera. Menos de ~90% significa string incompleta.
Registre o resultado em `config/execucao.json`; ele é a evidência de que a busca foi calibrada, e
não improvisada.

## 4 Exportação por base

| Base | Como exportar | Formato lido pelo motor |
|---|---|---|
| Scopus | *Export → CSV*, todos os campos, **com References** | `scopus_*.csv` |
| Web of Science | *Export → Plain Text*, *Full Record and Cited References*, lotes de 500 | `wos_*.txt` |
| SciELO | RIS ou BibTeX | `scielo_*.ris`, `*.bib` |
| Dimensions | CSV completo | `dimensions_*.csv` |
| Lens | CSV ou BibTeX | `lens_*.csv` |
| Outras | RIS ou BibTeX pelo gerenciador de referências | `*.ris`, `*.bib` |

O parser é escolhido pelo **nome do arquivo** (a base) e pela extensão. Arquivos parciais podem
ficar lado a lado: o motor concatena. Nunca edite uma exportação à mão.

**Campo de referências:** sem ele não há co-citação nem acoplamento bibliográfico. Se a sua base
principal não o exporta, diga isso no protocolo e trate a estrutura intelectual como análise de
cobertura parcial.

## 5 Registro da execução

Cada busca executada gera uma entrada em `config/execucao.json`: base, identificador da string,
data, hora, filtros, número de resultados e arquivo gerado. É esse registro — e não a memória —
que permite a outra pessoa repetir a busca e comparar.
