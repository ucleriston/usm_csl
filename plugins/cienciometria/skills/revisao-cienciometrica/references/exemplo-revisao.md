# Exemplo de revisão configurada

Referência de preenchimento. Vem de uma revisão real sobre federalismo fiscal dos entes
subnacionais; o que interessa aqui é a **forma** de cada decisão, não o tema.

## Recorte (docs/01-projeto-de-pesquisa.md)

**Tema.** Arranjos fiscais entre níveis de governo em que o ente subnacional (estado, província,
município) é a unidade de análise.

**Delimitação em três eixos.**
- *Temático:* competência tributária subnacional, transferências, equalização, endividamento,
  capacidade fiscal, competição horizontal, regras fiscais. Fora: federalismo apenas político;
  finanças do governo central.
- *Temporal:* 1990–2026 — o ciclo global de descentralização dos anos 1990 e, no Brasil, o regime
  da Constituição de 1988.
- *Documental:* artigos, revisões, capítulos e anais indexados, em português, inglês e espanhol.

**Pergunta que só esta revisão faz (QP6).** Qual a posição da produção latino-americana na
estrutura do campo, e em que medida ela dialoga com o núcleo internacional?

## Configuração (config/revisao.json)

```json
{
  "janela": {"inicio": 1990, "fim": 2026},
  "idiomas": ["pt", "en", "es"],
  "bases": ["scopus", "wos", "scielo", "dimensions", "lens"],
  "limiares": {"min_termo": 5, "min_cocitacao": 5, "kappa_minimo": 0.75},
  "periodos": [[1990, 1999], [2000, 2009], [2010, 2019], [2020, 2100]]
}
```

## Códigos de exclusão

| Código | Critério |
|---|---|
| E1 | Federalismo apenas político, sem componente fiscal |
| E2 | Finanças do governo central, sem recorte subnacional |
| E3 | Descentralização sem componente fiscal |
| E4 | Editorial, resenha, errata, carta, entrevista |
| E5 | Metadado insuficiente |
| E6 | Duplicata |
| E7 | Menção marginal ou metafórica ao tema |
| E8 | Texto integral indisponível |

Note que E1 a E3 são específicos do objeto e E4 a E8 valem para qualquer revisão. É a proporção
usual: o que muda de tema para tema são os três primeiros.

## Casos de fronteira decididos de antemão

- Federações e Estados unitários descentralizados: **ambos entram**; a forma vira variável.
- Estudo de um único município: entra **se** discutir a posição do ente no arranjo
  intergovernamental; estudo de gestão orçamentária interna, não.
- Direito tributário: entra quando discute repartição de competência entre entes; sai quando trata
  da relação fisco-contribuinte.

## Proposições com critério de refutação

```json
[
  {"id": "P1",
   "enunciado": "A produtividade dos autores aproxima-se da Lei de Lotka",
   "indicador": "expoente α e teste KS",
   "criterio": {"tipo": "todos", "condicoes": [
      {"campo": "lotka.alpha", "operador": "entre", "valor": [1.7, 2.3]},
      {"campo": "lotka.adere", "operador": "==", "valor": true}]}},

  {"id": "P4",
   "enunciado": "As redes de colaboração são fragmentadas por região linguística",
   "indicador": "componente gigante da coautoria e coautoria internacional",
   "criterio": {"tipo": "algum", "condicoes": [
      {"campo": "coautoria.metricas.componente_gigante_%", "operador": "<=", "valor": 60},
      {"campo": "colaboracao.coautoria_internacional_%", "operador": "<=", "valor": 40}]}},

  {"id": "P3",
   "enunciado": "A base intelectual é dominada pela tradição anglófona",
   "indicador": "origem das 50 referências mais co-citadas",
   "criterio": {"tipo": "manual",
                "observacao": "codificar a origem das 50 mais co-citadas; refutada se menos de 60% forem anglófonas"}}
]
```

A terceira mostra o padrão importante: o que depende de leitura entra como `manual` e é relatado
como pendente. Fingir veredicto automático para o que exige codificação humana é o erro que corrói
a confiança em todo o resto do relatório.

## Blocos de busca

| Bloco | Termos |
|---|---|
| B1 | `"fiscal federalism" OR "federalismo fiscal" OR "fiscal decentralization" OR "descentralização fiscal" OR "intergovernmental fiscal relations" OR "revenue sharing" OR "fiscal equalization"` |
| B2 | `subnational OR municipal* OR "local government*" OR "state government*" OR provincial OR "ente* federativo*"` |

Repare que os termos em três idiomas estão **dentro** dos mesmos blocos, e que `federalism`
sozinho ficou de fora: recall alto, precisão baixíssima.

## Vocabulário de temas (para a codificação manual)

T01 competência tributária · T02 transferências · T03 equalização e desigualdade territorial ·
T04 endividamento · T05 esforço e capacidade fiscal · T06 competição horizontal · T07
descentralização de serviços · T08 regras fiscais · T09 economia política · T10 reformas e
transição · T11 efeitos econômicos · T12 dogmática e jurisdição constitucional

Doze categorias é uma boa faixa: menos que isso não discrimina, mais que isso ninguém aplica com
consistência. Tema novo só nasce se ao menos 5 registros não couberem nos existentes — e a criação
vira emenda ao protocolo.
