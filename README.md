# usm_csl

Repositório de pesquisa acadêmica.

| Pasta | Conteúdo |
|---|---|
| `cienciometria/` | Motor de revisões cienciométricas: pipeline reprodutível (indicadores, redes, PRISMA, relatório) e as revisões conduzidas com ele |
| `plugins/cienciometria/` | O mesmo motor empacotado como plugin do Claude, com as skills que conduzem a revisão — cópia sincronizada por `make plugin` |
| `output.md` | Projeto de doutorado: capacidade estatal municipal e receita de referência na transição ao IBS |
| `convert.py` | Conversão de PDF para Markdown com MarkItDown |

## Plugin

```
/plugin marketplace add ucleriston/usm_csl
/plugin install cienciometria@usm-csl
```

Ativa quatro skills — condução da revisão, estratégia de busca, triagem e PRISMA, interpretação dos
resultados — e três comandos: `/nova-revisao`, `/analisar-corpus` e `/interpretar-mapa`.
Detalhes em [`plugins/cienciometria/README.md`](plugins/cienciometria/README.md).

## Motor

```bash
cd cienciometria
make exemplo     # roda o fluxo completo sobre a revisão de demonstração
make teste
make listar
```

Requisito: Python 3.9+, sem dependências externas. Documentação em
[`cienciometria/README.md`](cienciometria/README.md).
