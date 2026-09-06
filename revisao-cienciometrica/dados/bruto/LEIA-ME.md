# dados/bruto

Coloque aqui as exportações das bases, **com o nome da base no arquivo** — é assim que o pipeline
escolhe o parser:

| Base | Nome esperado | Formato |
|---|---|---|
| Scopus | `scopus_AAAA-MM-DD.csv` | CSV com todos os campos, incluindo *References* |
| Web of Science | `wos_AAAA-MM-DD_01.txt` | Plain Text — *Full Record and Cited References* |
| SciELO | `scielo_AAAA-MM-DD.ris` ou `.bib` | RIS ou BibTeX |
| Dimensions | `dimensions_AAAA-MM-DD.csv` | CSV completo |
| Lens | `lens_AAAA-MM-DD.csv` | CSV completo |

Arquivos parciais (lotes de 500 ou 2.000 registros) podem ficar lado a lado: o pipeline concatena.
Não edite as exportações à mão.

**Este diretório não é versionado** (exceto este arquivo): os termos de uso de Scopus, Web of Science
e Dimensions proíbem redistribuir registros completos. Ver `docs/06-reprodutibilidade.md`, §5.
