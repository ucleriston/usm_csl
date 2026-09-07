# Plano de análise do motor

Os indicadores abaixo são calculados em **qualquer** revisão, seja qual for o tema: eles descrevem
a forma do campo, não o seu conteúdo. Cada um traz definição, fórmula, insumo, saída gerada e a
pergunta que responde.

Nenhum resultado entra no relatório sem constar desta tabela — e nenhum indicador desta tabela é
omitido do relatório por ser inconveniente a uma proposição. O que cada revisão acrescenta são os
recortes próprios do seu objeto (§5) e as proposições que serão confrontadas com esses números
(§6).

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
| Fonte dos termos | Campo declarado em `campo_termos` (padrão: palavras-chave de autor); *keywords plus* e termos de resumo em análise de robustez |
| Normalização | Tesauro de termos da revisão; singular/plural, grafias, idiomas |
| Rede de co-palavras | Coocorrência no mesmo registro; limiar ≥ 5 ocorrências |
| Agrupamento | Propagação de rótulos, como em §2 |
| Mapa temático | Para cada agrupamento *c*: **centralidade** `= 10 × Σ e_kh` (ligações externas) e **densidade** `= 100 × (Σ e_ij / w)` (ligações internas), conforme Callon; quatro quadrantes: motores, básicos/transversais, de nicho, emergentes/em declínio |
| Evolução temática | Subperíodos declarados em `periodos`; fluxo de termos entre períodos por índice de inclusão |
| Palavras em ascensão | Variação da frequência relativa entre o penúltimo e o último subperíodo |

---

## 5 Recortes próprios da revisão (QP6 em diante)

As quatro seções anteriores cobrem o que toda revisão cienciométrica descreve. A pergunta que
distingue a **sua** revisão costuma exigir um recorte adicional sobre o corpus já formado. Padrões
que se repetem, com o indicador correspondente:

| Tipo de recorte | Pergunta típica | Como se calcula |
|---|---|---|
| Geográfico ou linguístico | A produção da região X dialoga com o núcleo internacional? | Participação na série anual; % de referências compartilhadas com a base de co-citação do núcleo; matriz de citação entre grupos; Jaccard entre os conjuntos de termos |
| Disciplinar | O tema é tratado por uma comunidade ou por várias que não se leem? | Distribuição por área da fonte; sobreposição de referências entre áreas; componentes da rede de coautoria por área |
| Metodológico | O campo é teórico, empírico ou normativo? | Distribuição de `abordagem` e `metodo_principal` (codificação manual) por período |
| Institucional | A produção vem da universidade, do governo ou de organismos internacionais? | Tipo de afiliação por período; participação no total de citações |
| Temporal | O que mudou depois do marco Y? | Todos os indicadores centrais recalculados por subperíodo (`periodos` em `config/revisao.json`) |

Escolha o que a sua QP6 exige, declare o cálculo aqui e registre a proposição correspondente em
`config/revisao.json`. Recorte que dependa de codificação manual entra como proposição do tipo
`manual`: o relatório o marca como pendente em vez de fingir um veredicto automático.

## 6 Proposições: critério declarado antes do resultado

As proposições ficam em `config/revisao.json`, cada uma com o indicador que a decide e o critério
que a refuta. O relatório aplica o critério ao valor calculado e devolve **sustentada**,
**refutada**, **exige etapa manual** ou **não avaliável** — nunca um juízo improvisado.

```json
{
  "id": "P1",
  "enunciado": "A produtividade dos autores segue a Lei de Lotka",
  "indicador": "expoente α e teste KS",
  "criterio": {"tipo": "todos", "condicoes": [
      {"campo": "lotka.alpha", "operador": "entre", "valor": [1.7, 2.3]},
      {"campo": "lotka.adere", "operador": "==", "valor": true}]}
}
```

| Elemento | Valores |
|---|---|
| `tipo` | `condicao` (uma), `todos` (conjunção), `algum` (disjunção), `manual` (depende de leitura) |
| `campo` | Caminho pontuado dentro de `saidas/resultados.json`, com índice para listas — ex.: `bradford.zonas.0.artigos_%`, `coautoria.metricas.componente_gigante_%`, `copalavras.quadrantes.emergente_ou_declinio` |
| `operador` | `>`, `>=`, `<`, `<=`, `==`, `!=`, `entre`, `fora`, `contem` |

Campos frequentes: `lotka.alpha`, `lotka.adere`, `bradford.multiplicador`,
`price.indice_price_corpus`, `impacto.h_index`, `colaboracao.coautoria_internacional_%`,
`cocitacao.cobertura_%`, `copalavras.agrupamentos`.

Proposição sem critério verificável é opinião. Proposição refutada é relatada como refutada: o
objetivo do desenho é descrever o campo, não confirmar a expectativa de partida.

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
| F8 | Recorte próprio da revisão (§5) |

Tabelas: top 20 fontes, top 20 autores, top 25 trabalhos citados, agrupamentos com rótulo, tamanho e
itens representativos.
