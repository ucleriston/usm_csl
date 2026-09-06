# Plano de análise

Cada indicador tem: definição, fórmula, insumo, saída gerada pelo pipeline e a pergunta que responde.
Nenhum resultado entra no relatório sem constar desta tabela — e nenhum indicador desta tabela é
omitido do relatório por ser inconveniente à proposição.

---

## 1 Desempenho (QP1, QP2)

| Indicador | Definição / fórmula | Saída |
|---|---|---|
| Produção anual | Contagem de registros por ano | `producao_anual.csv` |
| TCAC | `((P_final / P_inicial)^(1/n) - 1) × 100`, com janelas trienais nas pontas para reduzir ruído | `relatorio.md` |
| Fontes mais produtivas | Contagem por `fonte` | `fontes.csv` |
| Lei de Bradford | Ordenação decrescente de fontes; três zonas com nº de artigos aproximadamente igual; razão entre zonas ≈ 1:n:n² | `bradford.csv` |
| Autores mais produtivos | Contagem fracionária **e** integral (ambas relatadas) | `autores.csv` |
| Lei de Lotka | `y_x = C / x^α`; α estimado por mínimos quadrados sobre `log(x)`,`log(y)`; aderência por Kolmogorov–Smirnov | `lotka.csv` |
| Índice de colaboração | Média de autores por trabalho com mais de um autor | `relatorio.md` |
| Coautoria internacional | % de registros com `colab_internacional = 1` | `relatorio.md` |
| Produção por país | Contagem por país de afiliação (integral e fracionária) | `paises.csv` |
| Índice de Price | % de referências citadas com até 5 anos na data da publicação citante | `price.csv` |
| Impacto | Total de citações, média por trabalho, média por ano, h-index do corpus, top 25 mais citados | `citacoes.csv` |
| Meia-vida citada | Mediana da idade das referências citadas | `relatorio.md` |

**Fracionária vs. integral.** A contagem integral atribui 1 a cada autor/país do trabalho; a
fracionária, `1/n`. Ambas são relatadas porque diferem sistematicamente em campos com coautoria
desigual — apresentar só uma delas é escolher o resultado.

---

## 2 Estrutura intelectual (QP3)

| Análise | Unidade | Regra |
|---|---|---|
| Co-citação de referências | Referência citada | Duas referências são ligadas quando citadas juntas. Limiar: referência com ≥ 5 citações no corpus |
| Co-citação de autores | Primeiro autor da referência | Limiar: ≥ 10 co-citações |
| Acoplamento bibliográfico | Documento do corpus | Peso = nº de referências compartilhadas; limiar ≥ 3 |
| Normalização | — | Índice de associação (força de associação): `w_ij / (s_i × s_j)`, o mesmo do VOSviewer |
| Agrupamento | — | Propagação de rótulos por peso, com semente fixa (`--seed`), replicada 20 vezes; adota-se a partição modal |
| Validação | — | Cada agrupamento é rotulado após leitura dos 10 itens de maior força de ligação; rótulo automático nunca vai para o texto final sem leitura |

Restrição declarada: a co-citação usa apenas o subcorpus com campo de referências. A cobertura desse
subcorpus (n e % do corpus) é relatada junto de todo resultado que dele dependa.

---

## 3 Estrutura social (QP4)

| Rede | Nós | Aresta | Métricas |
|---|---|---|---|
| Coautoria | Autores | Coassinatura | Grau, intermediação, componentes, densidade, tamanho do componente gigante |
| Colaboração institucional | Instituições normalizadas | Coassinatura | Idem |
| Colaboração entre países | Países | Coassinatura | Idem + matriz de colaboração e taxa MCP/SCP |

`SCP` = trabalhos com autores de um só país; `MCP` = com múltiplos países. A razão MCP/(SCP+MCP)
por país é o indicador central de P4.

---

## 4 Estrutura conceitual (QP5)

| Etapa | Procedimento |
|---|---|
| Fonte dos termos | Palavras-chave de autor (principal); *keywords plus* e termos de resumo em análise de robustez |
| Normalização | `config/thesauro-termos.json`; singular/plural, grafias, idiomas |
| Rede de co-palavras | Coocorrência no mesmo registro; limiar ≥ 5 ocorrências |
| Agrupamento | Propagação de rótulos, como em §2 |
| Mapa temático | Para cada agrupamento *c*: **centralidade** `= 10 × Σ e_kh` (ligações externas) e **densidade** `= 100 × (Σ e_ij / w)` (ligações internas), conforme Callon; quatro quadrantes: motores, básicos/transversais, de nicho, emergentes/em declínio |
| Evolução temática | Subperíodos 1990–1999, 2000–2009, 2010–2019, 2020–corte; fluxo de termos entre períodos por índice de inclusão |
| Palavras em ascensão | Variação da frequência relativa entre o penúltimo e o último subperíodo |

---

## 5 Recorte brasileiro e latino-americano (QP6)

| Indicador | Cálculo |
|---|---|
| Participação | % do corpus com `pais_do_caso` ou país de afiliação na América Latina; série anual |
| Integração intelectual | % das referências citadas pelos trabalhos latino-americanos que também constam da base de co-citação do núcleo internacional |
| Citação cruzada | Matriz de citação entre grupos (LATAM ↔ resto), quando as referências permitirem identificar o citado |
| Sobreposição temática | Índice de Jaccard entre os conjuntos de termos dos dois grupos |
| Fontes de publicação | Distribuição por fonte e por idioma, comparada com o restante do corpus |

---

## 6 Correspondência entre proposições e indicadores

| Proposição | Indicador decisivo | Critério de refutação |
|---|---|---|
| P1 (Lotka) | α estimado, KS | α fora de [1,7; 2,3] ou KS rejeitando a 5% |
| P2 (Bradford) | Zonas e razão | Razão entre zonas fora do padrão 1:n:n² com desvio > 30% |
| P3 (base anglófona) | Origem das 50 referências mais co-citadas | Menos de 60% de origem anglófona |
| P4 (fragmentação) | Componentes da rede de coautoria; MCP por país | Componente gigante > 60% dos nós **e** MCP latino-americana > 40% |
| P5 (núcleo/emergentes) | Quadrantes do mapa temático | T10/T05 não aparecendo no quadrante emergente |
| P6 (isolamento brasileiro) | Matriz de citação cruzada | > 40% das citações a trabalhos brasileiros virem de fora do Brasil |

Proposição refutada é relatada como refutada. O objetivo do desenho é descrever o campo, não
confirmar a expectativa de partida.

---

## 7 Robustez

1. **Sensibilidade por base:** todos os indicadores centrais recalculados excluindo cada base por vez.
2. **Sensibilidade por limiar:** redes recalculadas com limiares ±1 em relação ao adotado.
3. **Sensibilidade por agrupamento:** partição comparada com a de outro método (modularidade gulosa);
   concordância medida por informação mútua ajustada.
4. **Janela temporal:** indicadores recalculados excluindo o último ano (incompleto na indexação).
5. **Semente:** todo procedimento estocástico com semente fixa e registrada.

---

## 8 Apresentação

| Figura | Conteúdo |
|---|---|
| F1 | Fluxo PRISMA |
| F2 | Produção anual e citações acumuladas |
| F3 | Dispersão de Bradford e ajuste de Lotka |
| F4 | Rede de co-citação de referências |
| F5 | Rede de colaboração entre países |
| F6 | Mapa temático (centralidade × densidade) |
| F7 | Evolução temática por subperíodos |
| F8 | Recorte latino-americano: participação e integração |

Tabelas: top 20 fontes, top 20 autores, top 25 trabalhos citados, agrupamentos com rótulo, tamanho e
itens representativos.
