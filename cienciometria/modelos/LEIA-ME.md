# Modelos

| Arquivo | Uso |
|---|---|
| `triagem.csv` | Gerado por `make triagem`. Planilha cega: cada revisor preenche apenas a sua coluna (`decisao_r1` ou `decisao_r2`) sem ver a do outro |
| `ficha-de-extracao.md` | Codificação manual das variáveis de conteúdo |
| `registro-de-decisoes.csv` | Toda decisão discricionária tomada durante a revisão. `afeta_protocolo = sim` obriga a registrar emenda em `docs/02-protocolo-prisma.md`, §10 |

**Decisões válidas na triagem:** `incluido`, `excluido`, `duvida`.
**Exclusão exige código** `E1`–`E8` (protocolo, §3.2). Um único código por registro, o de maior
precedência na ordem listada.
