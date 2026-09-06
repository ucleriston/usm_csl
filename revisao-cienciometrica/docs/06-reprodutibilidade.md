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
revisao-cienciometrica/
├── docs/               projeto, protocolo, strings, livro de códigos, plano de análise
├── config/             tesauros, léxicos, sementes, registro de execução das buscas
├── dados/
│   ├── bruto/          exportações das bases (NÃO versionadas — ver §5)
│   ├── exemplo/        amostra sintética para testar o pipeline
│   └── processado/     corpus deduplicado, decisões de triagem
├── src/cienciometria/  pipeline
├── saidas/             tabelas, redes e relatório gerados
├── modelos/            planilha de triagem, ficha de extração, formulário de decisão
└── testes/             testes automatizados
```

## 4 Comandos

```bash
cd revisao-cienciometrica

python -m cienciometria importar   --entrada dados/bruto   --saida dados/processado/corpus.csv
python -m cienciometria dedup      --corpus dados/processado/corpus.csv
python -m cienciometria triagem    --corpus dados/processado/corpus.csv --saida modelos/triagem.csv
python -m cienciometria kappa      --triagem dados/processado/triagem-preenchida.csv
python -m cienciometria indicadores --corpus dados/processado/corpus.csv --saida saidas/
python -m cienciometria redes      --corpus dados/processado/corpus.csv --saida saidas/
python -m cienciometria relatorio  --saida saidas/
python -m cienciometria prisma     --saida saidas/

# tudo de uma vez:
make analise

# testar o pipeline com a amostra sintética:
make exemplo
```

Todos os comandos aceitam `--seed` (padrão 42) e escrevem, em `saidas/execucao.log`, o comando, a
data, a versão do código (hash do commit) e as contagens de entrada e saída.

## 5 Dados versionados e não versionados

| Conteúdo | Versionado? | Razão |
|---|---|---|
| Código, documentação, configuração, tesauros | Sim | É a pesquisa |
| `dados/exemplo/` | Sim | Amostra **sintética**, criada para teste do pipeline. Não são registros reais |
| `dados/bruto/*` de Scopus, WoS, Dimensions | **Não** | Termos de uso proíbem redistribuição de registros completos |
| `dados/bruto/*` de SciELO, Lens, Crossref, OpenAlex | Sim | Fontes abertas |
| `dados/processado/corpus.csv` | Publicado como lista de DOI + variáveis derivadas | Compatibiliza reprodutibilidade e licença das bases |
| `saidas/` | Sim, na versão final | São os resultados |

Quem quiser reexecutar a partir das bases proprietárias precisa de acesso institucional próprio; as
strings e a data de corte estão em `docs/03-estrategias-de-busca.md` e `config/execucao.json`, o que
torna a reexecução possível sem redistribuição de dados licenciados.

## 6 Versionamento e citação

- Cada marco (fechamento do corpus, submissão) recebe uma *tag* git.
- O pacote de reprodutibilidade é depositado em repositório com DOI (Zenodo/OSF) na submissão.
- O relatório registra: data de corte, versão do código, versão dos tesauros e semente.

## 7 Auditoria

`saidas/execucao.log` permite responder, para qualquer número do artigo: de qual arquivo bruto veio,
por qual código passou, com qual configuração e em que data. Se um número não puder ser rastreado
assim, ele não entra no artigo.
