# Estratégias de busca

Relato conforme PRISMA-S. Toda string abaixo é para ser **copiada e colada** na interface da base.
Nenhuma delas foi executada ainda: as contagens são preenchidas na execução e registradas em
`config/execucao.json`.

---

## 1 Blocos conceituais

A busca combina três blocos por `AND`. Cada bloco reúne sinônimos em português, inglês e espanhol.

**Bloco 1 — Dimensão fiscal**
`fiscal, tributári*, tax*, taxation, revenue, receita, orçament*, budget*, presupuest*, finanç*
públic*, public finance, gasto público, transferênci*, transfer*, transferenci*, endividament*,
debt, deuda, arrecadação, hacienda`

**Bloco 2 — Arranjo intergovernamental**
`federalismo fiscal, fiscal federalism, federalismo fiscal (es), descentralização fiscal, fiscal
decentrali*ation, descentralización fiscal, relações intergovernamentais, intergovernmental fiscal
relations, relaciones intergubernamentales, repartição de receitas, revenue sharing, coparticipación,
equalização fiscal, fiscal equali*ation, transferências intergovernamentais, intergovernmental
transfers, autonomia financeira, fiscal autonomy, guerra fiscal, tax competition`

**Bloco 3 — Ente subnacional**
`subnacional, subnational, sub-national, estadual, state government, provincial, province, regional
government, municipal, municipality, município, municipio, local government, governo local, gobierno
local, comuna, county, city government, ente federativo, ente federado`

---

## 2 Scopus

### 2.1 String principal

```
TITLE-ABS-KEY (
   ( "fiscal federalism" OR "federalismo fiscal" OR "fiscal decentralization"
     OR "fiscal decentralisation" OR "descentralização fiscal" OR "descentralizacion fiscal"
     OR "intergovernmental fiscal relations" OR "relações intergovernamentais"
     OR "relaciones fiscales intergubernamentales" OR "intergovernmental transfers"
     OR "transferências intergovernamentais" OR "transferencias intergubernamentales"
     OR "revenue sharing" OR "repartição de receitas" OR "coparticipación"
     OR "fiscal equalization" OR "fiscal equalisation" OR "equalização fiscal"
     OR "tax assignment" OR "competência tributária" )
   AND
   ( subnational OR "sub-national" OR subnacional OR municipal* OR municipio* OR município*
     OR "local government*" OR "governo* local*" OR "gobierno* local*"
     OR "state government*" OR "governo* estadual*" OR provincial OR province*
     OR "regional government*" OR "ente* federativo*" OR "ente* federado*" )
)
AND PUBYEAR > 1989
AND ( LIMIT-TO ( DOCTYPE , "ar" ) OR LIMIT-TO ( DOCTYPE , "re" )
      OR LIMIT-TO ( DOCTYPE , "ch" ) OR LIMIT-TO ( DOCTYPE , "cp" ) )
AND ( LIMIT-TO ( LANGUAGE , "English" ) OR LIMIT-TO ( LANGUAGE , "Portuguese" )
      OR LIMIT-TO ( LANGUAGE , "Spanish" ) )
```

### 2.2 Variante de sensibilidade (S2)

Bloco 1 + Bloco 2 sem exigir o Bloco 3 — captura trabalhos que tratam do ente subnacional sem
nomeá-lo nos campos indexados:

```
TITLE-ABS-KEY ( ( fiscal OR tax* OR revenue OR budget* OR "public finance" )
  AND ( federalism OR federalismo OR "decentrali*ation" OR "descentraliza*"
        OR intergovernmental OR intergubernamental OR interfederativ* ) )
AND PUBYEAR > 1989
```

A variante S2 é executada e comparada com a principal; o ganho marginal de registros elegíveis é
relatado. Se a precisão de S2 na amostra de 100 registros ficar abaixo de 0,20, ela é descartada e
o descarte é justificado no relato.

### 2.3 Exportação

`Export → CSV` com **todos** os campos, obrigatoriamente incluindo: *Authors, Author(s) ID, Title,
Year, Source title, Volume, Issue, Pages, Cited by, DOI, Affiliations, Authors with affiliations,
Abstract, Author Keywords, Index Keywords, References, Document Type, Language of Original Document,
Publisher, ISSN*.
Salvar em `dados/bruto/scopus_AAAA-MM-DD.csv`. Exportações de 2.000 em 2.000 registros; manter os
arquivos parciais, sem concatenar manualmente — o pipeline concatena.

---

## 3 Web of Science (Core Collection)

```
TS = (
  ( "fiscal federalism" OR "fiscal decentralization" OR "fiscal decentralisation"
    OR "intergovernmental fiscal relations" OR "intergovernmental transfers"
    OR "revenue sharing" OR "fiscal equalization" OR "fiscal equalisation"
    OR "tax assignment" OR "federalismo fiscal" OR "descentralización fiscal"
    OR "descentralização fiscal" OR "transferências intergovernamentais" )
  AND
  ( subnational OR "sub-national" OR municipal* OR "local government*"
    OR "state government*" OR provincial OR "regional government*"
    OR subnacional OR município* OR municipio* )
)
```

Filtros: `Publication Years 1990–<corte>`; `Document Types: Article, Review, Book Chapter,
Proceedings Paper`; `Languages: English, Portuguese, Spanish`.
Índices: SCI-EXPANDED, SSCI, A&HCI, ESCI, CPCI-SSH, BKCI-SSH (registrar quais foram assinados).

**Exportação:** `Export → Plain Text (Full Record and Cited References)`, lotes de 500 registros,
arquivos `dados/bruto/wos_AAAA-MM-DD_01.txt`, `_02.txt`, …

---

## 4 SciELO

A interface do SciELO não suporta strings longas com o mesmo comportamento das bases anglófonas.
Executar buscas separadas e registrar cada uma:

```
(ab:("federalismo fiscal") OR ti:("federalismo fiscal") OR kw:("federalismo fiscal"))
(ab:("descentralização fiscal") OR ab:("descentralización fiscal"))
(ab:("transferências intergovernamentais") OR ab:("transferencias intergubernamentales"))
(ab:("repartição de receitas") OR ab:("coparticipación federal"))
(ab:("autonomia financeira" AND município*))
(ab:("finanças municipais") OR ab:("finanzas municipales") OR ab:("finanças estaduais"))
(ab:("guerra fiscal") OR ab:("competição tributária"))
```

Coleções: Brasil, Argentina, Chile, Colômbia, México, Espanha, Portugal (SciELO Citation Index
quando disponível via WoS — nesse caso, registrar como execução da WoS).
Exportar em `.bib` ou `.ris`: `dados/bruto/scielo_AAAA-MM-DD_<termo>.ris`.

---

## 5 Dimensions

```
"fiscal federalism" OR "fiscal decentralization" OR "intergovernmental fiscal relations"
OR "federalismo fiscal" OR "descentralização fiscal" OR "descentralización fiscal"
```
Filtros: anos 1990–corte; tipo `Article, Chapter, Proceeding`; campos de pesquisa `Title and
abstract`. Exportar CSV completo para `dados/bruto/dimensions_AAAA-MM-DD.csv`.

---

## 6 Lens.org

```
(title:("fiscal federalism") OR abstract:("fiscal federalism")
 OR title:("federalismo fiscal") OR abstract:("federalismo fiscal")
 OR title:("fiscal decentralization") OR abstract:("fiscal decentralization"))
AND year_published:[1990 TO <corte>]
```
Exportar CSV/BibTeX para `dados/bruto/lens_AAAA-MM-DD.csv`.

---

## 7 Conjunto-semente (teste de recall)

Antes da execução definitiva, verificar se a string principal recupera os trabalhos de
`config/sementes.csv` — 25 obras notoriamente pertinentes, escolhidas para cobrir as três tradições
(anglófona, ibérica, latino-americana) e as duas gerações da teoria. Recall mínimo: **22/25**.

Registrar em `config/execucao.json`:

```json
{
  "data_de_corte": "AAAA-MM-DD",
  "execucoes": [
    {"base": "scopus", "string_id": "S1", "data": "AAAA-MM-DD", "hora": "HH:MM",
     "resultados": 0, "arquivo": "dados/bruto/scopus_AAAA-MM-DD.csv",
     "filtros": "PUBYEAR>1989; ar,re,ch,cp; en,pt,es"}
  ],
  "recall_sementes": {"recuperadas": 0, "total": 25}
}
```

---

## 8 Registro de decisões terminológicas

| Termo | Decisão | Razão |
|---|---|---|
| `federalism` isolado | Não usar sozinho | Recall alto, precisão muito baixa (federalismo político) |
| `decentrali?ation` | Grafias BR e US sempre juntas | Perda sistemática se apenas uma |
| `local finance` | Incluído apenas em variante de sensibilidade | Alta ambiguidade com finanças privadas locais |
| `intergovernmental` | Usado no bloco 2 | Recupera a literatura de relações intergovernamentais que não usa "federalism" |
| `interfederativ*` | Incluído | Termo corrente na literatura jurídica brasileira recente |
| `IBS`, `ICMS`, `ISS`, `FPM` | Não incluídos na busca principal | Siglas nacionais reduzem comparabilidade internacional; usadas apenas na etapa de recorte brasileiro sobre o corpus já formado |
