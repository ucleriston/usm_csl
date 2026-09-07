# Federalismo fiscal dos entes subnacionais

Revisão cienciométrica da produção científica sobre arranjos fiscais entre níveis de governo em que
o ente subnacional é a unidade de análise, 1990–2026.

| Documento | Conteúdo |
|---|---|
| [Projeto de pesquisa](docs/01-projeto-de-pesquisa.md) | Tema, problema, seis perguntas, proposições, objetivos, justificativa, referencial, cronograma, riscos, referências |
| [Protocolo](docs/02-protocolo-prisma.md) | Elegibilidade, códigos E1–E8, triagem dupla cega, kappa, extração, fluxo, verificação final |
| [Estratégias de busca](docs/03-estrategias-de-busca.md) | Strings para Scopus, WoS, SciELO, Dimensions e Lens; teste de recall; decisões terminológicas |
| [Livro de códigos](docs/04-livro-de-codigos.md) | Variáveis, vocabulário de temas T01–T12, tesauros, precedência entre bases |
| `config/revisao.json` | O mesmo recorte em forma de máquina, com as proposições e seus critérios de refutação |

```bash
make analise REVISAO=federalismo-fiscal-subnacional
```

**Situação:** protocolo e strings prontos; buscas ainda não executadas. Falta preencher
`config/sementes.csv` (conjunto-semente do teste de recall, escolhido antes da busca) e
`config/execucao.json` (data de corte e contagens por base).

Esta revisão sustenta o estado da arte do projeto de doutorado em `../../../output.md`, sobre
capacidade estatal municipal e receita de referência na transição ao IBS — temas T05 e T10 do livro
de códigos.
