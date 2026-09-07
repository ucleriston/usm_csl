# Projeto de pesquisa

## {{TITULO}}

> Modelo. Substitua cada trecho entre «» e apague as notas em citação. Tudo o que estiver aqui
> precisa estar coerente com `config/revisao.json` — o motor lê o recorte de lá, não deste texto.

---

## 1 Tema e delimitação

**Tema:** {{TEMA}}

> Delimite em três eixos, porque são eles que a busca vai operacionalizar:
>
> - **Temático:** o que integra o objeto e o que fica de fora. Nomeie os subtemas.
> - **Temporal:** a janela e a razão dela (marco legal, virada teórica, evento). Deve bater com
>   `janela` em `config/revisao.json`.
> - **Documental:** tipos, idiomas e veículos. Deve bater com `tipos_documento` e `idiomas`.

## 2 Problema

> Uma pergunta, formulada de modo que a resposta dependa de dado observável no corpus.

**Perguntas derivadas** — cada uma com o indicador que a responde:

| # | Pergunta | Indicador |
|---|---|---|
| QP1 | Qual o volume, o ritmo e a distribuição temporal da produção? | Produção anual, TCAC, índice de Price |
| QP2 | Como se distribuem autores, fontes e países? | Lotka, Bradford, produção por país |
| QP3 | Qual a estrutura intelectual — que base teórica o campo compartilha? | Co-citação, acoplamento bibliográfico |
| QP4 | Qual a estrutura social — quem colabora com quem? | Redes de coautoria e de países |
| QP5 | Qual a estrutura conceitual — que temas há, quais são centrais? | Co-palavras, mapa temático |
| QP6 | «pergunta própria do seu recorte» | «indicador» |

> As cinco primeiras servem a qualquer revisão cienciométrica; QP6 em diante é onde entra o que só
> a sua pesquisa pergunta.

## 3 Proposições

> Afirmações verificáveis, cada uma com um indicador que pode refutá-la. Devem espelhar, uma a uma,
> as entradas de `proposicoes` em `config/revisao.json`: é lá que o critério de refutação fica
> registrado antes de haver resultado, e é de lá que o relatório tira o veredicto.

- **P1.** «proposição» — refutada se «critério».
- **P2.** …

## 4 Objetivos

**Geral:** «mapear … por métodos cienciométricos, no período …».

**Específicos:**
1. Construir corpus reprodutível a partir das bases selecionadas.
2. Descrever o desempenho do campo (produção, fontes, autores, países, impacto, obsolescência).
3. Reconstituir a estrutura intelectual.
4. Reconstituir a estrutura social.
5. Reconstituir a estrutura conceitual e sua evolução.
6. «objetivo próprio do recorte».
7. Explicitar lacunas e derivar delas uma agenda de pesquisa.

## 5 Justificativa

> Três frentes: **científica** (que lacuna de revisão existe), **metodológica** (por que
> cienciometria e não revisão narrativa) e **aplicada** (quem usa o resultado e para quê).

## 6 Referencial

**Do objeto:** «as correntes teóricas do seu tema — que a análise de co-citação vai verificar, e
não pressupor».

**Do método:** Lotka (1926), Bradford (1934), Price (1965), Small (1973), Kessler (1963), Callon,
Courtial e Laville (1991); orientação de procedimento em Zupic e Čater (2015) e Donthu *et al.*
(2021); relato conforme PRISMA 2020 (Page *et al.*, 2021) e PRISMA-S (Rethlefsen *et al.*, 2021);
cobertura das bases em Mongeon e Paul-Hus (2016) e Visser, van Eck e Waltman (2021).

## 7 Metodologia

Ver, nesta mesma pasta: [protocolo](02-protocolo-prisma.md), [estratégias de busca](03-estrategias-de-busca.md)
e [livro de códigos](04-livro-de-codigos.md); e, no motor, o
[plano de análise](../../../docs/05-plano-de-analise.md) e a
[nota de reprodutibilidade](../../../docs/06-reprodutibilidade.md).

**Limite declarado:** a revisão descreve a literatura indexada. Não mede qualidade dos trabalhos,
não estabelece causalidade e não substitui a leitura analítica das obras do núcleo.

## 8 Resultados esperados e produtos

1. Corpus deduplicado e anotado. 2. Relatório cienciométrico. 3. Redes em formato aberto.
4. Artigo. 5. Agenda de pesquisa. 6. Pacote de reprodutibilidade.

## 9 Cronograma

| Etapa | M1 | M2 | M3 | M4 | M5 | M6 | M7 | M8 | M9 | M10 | M11 | M12 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| Protocolo e calibração das strings | ● | ● | | | | | | | | | | |
| Buscas e exportação | | ● | ● | | | | | | | | | |
| Deduplicação e triagem dupla | | | ● | ● | | | | | | | | |
| Extração e normalização | | | | ● | ● | | | | | | | |
| Análise de desempenho | | | | | ● | ● | | | | | | |
| Redes e mapa temático | | | | | | ● | ● | ● | | | | |
| Leitura analítica do núcleo | | | | | | | | ● | ● | | | |
| Redação e submissão | | | | | | | | | ● | ● | ● | ● |

## 10 Riscos

| Risco | Efeito | Mitigação |
|---|---|---|
| Cobertura desigual das bases | Sub-representação de parte da literatura | Base de língua local desde a identificação; análise de sensibilidade por base |
| Ambiguidade terminológica | Perda de recall | Blocos sinonímicos amplos; teste de recall com conjunto-semente |
| Homonímia de autores | Distorção nas redes | ORCID quando houver; revisão manual do topo da lista |
| Referências ausentes em parte das bases | Co-citação enfraquecida | Cobertura declarada em todo indicador dela dependente |
| Deriva temporal entre execuções | Não reprodutibilidade | Data de corte declarada; exportações preservadas |

## 11 Ética e dados

Metadados bibliográficos, sem seres humanos envolvidos. Bases proprietárias restringem
redistribuição: publica-se código, protocolo, strings e identificadores; não as exportações brutas.

## Referências

> Monte a lista final a partir do próprio corpus. Confira cada entrada no registro da base antes de
> submeter.
