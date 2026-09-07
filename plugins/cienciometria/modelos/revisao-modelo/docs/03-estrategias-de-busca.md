# Estratégias de busca — {{TITULO}}

Relato conforme PRISMA-S. Preencha as contagens em `config/execucao.json` ao executar.
O guia de construção das strings está em [docs/03-guia-de-buscas.md](../../../docs/03-guia-de-buscas.md).

## 1 Blocos conceituais

| Bloco | Papel | Termos (pt / en / es) |
|---|---|---|
| B1 | «conceito central» | |
| B2 | «qualificador teórico ou fenômeno» | |
| B3 | «unidade de análise, recorte ou contexto» | |

## 2 Scopus

```
TITLE-ABS-KEY ( ( «B1» ) AND ( «B2» ) AND ( «B3» ) )
AND PUBYEAR > «ano inicial - 1»
AND ( LIMIT-TO ( DOCTYPE , "ar" ) OR LIMIT-TO ( DOCTYPE , "re" ) )
AND ( LIMIT-TO ( LANGUAGE , "English" ) OR LIMIT-TO ( LANGUAGE , "Portuguese" ) )
```

Exportação: CSV com todos os campos, **incluindo References**, em `dados/bruto/scopus_AAAA-MM-DD.csv`.

## 3 Web of Science

```
TS = ( ( «B1» ) AND ( «B2» ) AND ( «B3» ) )
```
Filtros: anos, tipos e idiomas conforme `config/revisao.json`.
Exportação: *Plain Text — Full Record and Cited References*, em `dados/bruto/wos_AAAA-MM-DD_01.txt`.

## 4 Base de língua local (SciELO, Redalyc, outra)

> Interfaces menores costumam não suportar strings longas: quebre em buscas simples e registre cada
> uma separadamente.

```
(ab:("«termo»") OR ti:("«termo»") OR kw:("«termo»"))
```

## 5 Demais bases

«Dimensions, Lens, ou o que o tema exigir.»

## 6 Variante de sensibilidade

> Uma versão mais ampla da string, para medir o que a principal deixa de fora. Execute, compare o
> ganho de registros elegíveis e relate a decisão — inclusive a de descartar a variante.

## 7 Teste de recall

Conjunto-semente em `config/sementes.csv`. Mínimo exigido declarado em `config/execucao.json`.
Abaixo do mínimo, a string é revista antes de qualquer outra coisa.

## 8 Decisões terminológicas

| Termo | Decisão | Razão |
|---|---|---|
| | | |
