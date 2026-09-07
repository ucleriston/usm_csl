# Revisão de demonstração — dados sintéticos

Esta revisão existe para exercitar o pipeline de ponta a ponta sem depender de acesso a bases
proprietárias. **Os registros são fabricados** por `testes/gerar_exemplo.py` com semente fixa:
autores (`Alfa A.`, `Beta B.`, …), títulos, DOI `10.5555/exemplo.*` e contagens de citação não
correspondem a nada real. Nenhum número produzido aqui pode ser citado como resultado.

```bash
make exemplo     # gera os arquivos sintéticos e roda o fluxo completo
less revisoes/exemplo-sintetico/saidas/relatorio.md
```

Há sobreposição proposital entre os três arquivos gerados (Scopus × WoS × SciELO), para que a
deduplicação tenha o que remover, e os limiares em `config/revisao.json` são mais baixos que os
padrões, porque o corpus é pequeno.

Os documentos em `docs/` são os modelos por preencher — ficam aqui para você ver a estrutura de uma
revisão antes de criar a sua:

```bash
python -m cienciometria nova <slug> --titulo "..." --tema "..."
```
