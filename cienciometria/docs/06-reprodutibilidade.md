# Reprodutibilidade

## 1 Princípio

Um resultado cienciométrico que não pode ser reexecutado é uma opinião com números. Por isso:

- toda transformação de dado é feita por código versionado, nunca por edição manual de planilha;
- toda decisão discricionária (tesauro, limiar, precedência entre bases) fica em arquivo de
  configuração, não dentro do código;
- toda execução de busca é registrada com string, filtros, data, hora e contagem;
- toda saída é regenerável a partir de `dados/bruto/` com um único comando.

## 2 Requisitos

Python 3.9 ou superior. **Nenhuma dependência externa é necessária** para o pipeline: parsers,
deduplicação, indicadores e redes usam apenas a biblioteca padrão.

Opcionais: `matplotlib` (gráficos PNG — o pipeline gera os dados dos gráficos de qualquer modo) e
`rapidfuzz` (deduplicação mais rápida em corpus > 20 mil registros; sem ele, usa-se `difflib`).

## 3 Estrutura de diretórios

```
cienciometria/
├── docs/                 guias do motor (fluxo, protocolo, buscas, códigos, análise, este)
├── config/               configuração comum a todas as revisões (léxico de países)
├── src/cienciometria/    o motor
├── modelos/
│   └── revisao-modelo/   esqueleto copiado ao criar uma revisão
├── revisoes/
│   └── <slug>/           uma revisão: um tema, um corpus, um conjunto de saídas
│       ├── docs/         projeto, protocolo, buscas e livro de códigos DAQUELE tema
│       ├── config/       revisao.json, execucao.json, tesauros, sementes
│       ├── dados/
│       │   ├── bruto/        exportações das bases (não versionadas — ver §5)
│       │   └── processado/   corpus, decisões, estatísticas
│       └── saidas/       tabelas, redes, relatório e log de execução
└── testes/               testes automatizados e gerador da amostra sintética
```

A separação é deliberada: **o motor não sabe de tema nenhum**. Recorte, tesauros, limiares,
subperíodos e proposições vivem em `revisoes/<slug>/config/revisao.json`. Trocar de tema é criar
outra revisão, não editar o código.

## 4 Comandos

```bash
python -m cienciometria nova <slug> --titulo "..." --tema "..."
python -m cienciometria listar

python -m cienciometria coletar     --revisao <slug> --fonte openalex --busca "..."
python -m cienciometria importar    --revisao <slug>
python -m cienciometria dedup       --revisao <slug>
python -m cienciometria triagem     --revisao <slug>
python -m cienciometria kappa       --revisao <slug> --triagem <arquivo.csv>
python -m cienciometria indicadores --revisao <slug>
python -m cienciometria redes       --revisao <slug>
python -m cienciometria prisma      --revisao <slug>
python -m cienciometria relatorio   --revisao <slug>
python -m cienciometria analise     --revisao <slug>   # tudo, na ordem

# equivalentes pelo Makefile
make analise REVISAO=<slug>
make exemplo                 # revisão de demonstração com dados sintéticos
make teste
```

Os limiares (`--min-termo`, `--min-autor`, `--min-cocitacao`, `--min-acoplamento`) e a semente
(`--seed`) sobrepõem, quando informados, o que está declarado na revisão; sem eles, vale a
configuração — para que a execução padrão seja sempre a mesma.

Cada comando anexa a `revisoes/<slug>/saidas/execucao.log` o comando, a data, o hash do commit e as
contagens de entrada e saída.

## 5 Dados versionados e não versionados

| Conteúdo | Versionado? | Razão |
|---|---|---|
| Motor, guias, esqueleto de revisão | Sim | É a ferramenta |
| `revisoes/<slug>/docs/` e `config/` | Sim | É a pesquisa: recorte, protocolo, strings, tesauros, proposições |
| `dados/exemplo/` da revisão de demonstração | Sim | Amostra **sintética**. Não são registros reais |
| `revisoes/<slug>/dados/bruto/*` de bases proprietárias | **Não** | Termos de uso proíbem redistribuir registros completos |
| `revisoes/<slug>/dados/bruto/*` de fontes abertas | Sim | SciELO, Lens, Crossref, OpenAlex |
| `dados/processado/corpus.csv` | Publicado como lista de DOI + variáveis derivadas | Compatibiliza reprodutibilidade e licença das bases |
| `saidas/` | Sim, na versão final | São os resultados |

Quem quiser reexecutar a partir das bases proprietárias precisa de acesso institucional próprio; as
strings e a data de corte estão nos documentos da revisão e em `config/execucao.json`, o que
torna a reexecução possível sem redistribuição de dados licenciados.

## 6 Versionamento e citação

- Cada marco (fechamento do corpus, submissão) recebe uma *tag* git.
- O pacote de reprodutibilidade é depositado em repositório com DOI (Zenodo/OSF) na submissão.
- O relatório registra: data de corte, versão do código, versão dos tesauros e semente.

## 7 Auditoria

`revisoes/<slug>/saidas/execucao.log` permite responder, para qualquer número do artigo: de qual arquivo bruto veio,
por qual código passou, com qual configuração e em que data. Se um número não puder ser rastreado
assim, ele não entra no artigo.
