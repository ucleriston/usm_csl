# Guia de buscas — construindo a string para qualquer tema

Relato conforme PRISMA-S. O modelo preenchível fica em cada revisão
(`revisoes/<slug>/docs/03-estrategias-de-busca.md`).

## 1 A string em blocos

Decomponha o tema em dois ou três blocos conceituais e combine-os por `AND`; dentro de cada bloco,
sinônimos por `OR`.

| Bloco | O que é | Exemplo (tema: capacidade estatal municipal) |
|---|---|---|
| B1 | Conceito central | `"state capacity" OR "capacidade estatal" OR "administrative capacity"` |
| B2 | Qualificador ou fenômeno | `bureaucra* OR "public administration" OR "gestão pública"` |
| B3 | Unidade de análise ou contexto | `municipal* OR "local government*" OR município*` |

Três blocos dão precisão; dois dão recall. Rode as duas versões e relate o ganho marginal da mais
ampla — inclusive quando a decisão for descartá-la.

## 2 Regras que evitam os erros mais comuns

1. **Campo certo.** `TITLE-ABS-KEY` no Scopus, `TS=` na WoS. Buscar só no título perde metade da
   literatura; buscar no texto completo traz ruído incontrolável.
2. **Truncamento consciente.** `municipal*` pega *municipality*, *municipalities*, *municipal*.
   Truncar cedo demais (`munic*`) traz *Munich*.
3. **Grafias britânica e americana sempre juntas.** `decentrali?ation`, ou as duas formas por `OR`.
   Esquecer uma delas é perda sistemática, não aleatória.
4. **Três idiomas, se o tema os tiver.** Termos em português e espanhol dentro dos mesmos blocos.
5. **Aspas em expressões.** Sem aspas, `fiscal federalism` vira `fiscal AND federalism`.
6. **Termo genérico sozinho, nunca.** Palavras como *federalism*, *capacity* ou *reform* só entram
   acompanhadas de outro bloco.
7. **Siglas nacionais fora da busca principal.** Elas quebram a comparabilidade internacional; use-as
   depois, para recortar o corpus já formado.

## 3 Teste de recall antes de valer

Monte um conjunto-semente de 20 a 25 trabalhos que você já sabe pertinentes — escolhidos **antes**
da busca — e verifique quantos a string recupera. Menos de ~90% significa string incompleta.
Registre o resultado em `config/execucao.json`; ele é a evidência de que a busca foi calibrada, e
não improvisada.

## 4 Exportação por base

| Base | Como exportar | Formato lido pelo motor |
|---|---|---|
| Scopus | *Export → CSV*, todos os campos, **com References** | `scopus_*.csv` |
| Web of Science | *Export → Plain Text*, *Full Record and Cited References*, lotes de 500 | `wos_*.txt` |
| SciELO | RIS ou BibTeX | `scielo_*.ris`, `*.bib` |
| Dimensions | CSV completo | `dimensions_*.csv` |
| Lens | CSV ou BibTeX | `lens_*.csv` |
| Outras | RIS ou BibTeX pelo gerenciador de referências | `*.ris`, `*.bib` |

O parser é escolhido pelo **nome do arquivo** (a base) e pela extensão. Arquivos parciais podem
ficar lado a lado: o motor concatena. Nunca edite uma exportação à mão.

**Campo de referências:** sem ele não há co-citação nem acoplamento bibliográfico. Se a sua base
principal não o exporta, diga isso no protocolo e trate a estrutura intelectual como análise de
cobertura parcial.

## 5 Quando não há Scopus nem Web of Science

Duas APIs abertas cobrem boa parte do que as bases proprietárias cobrem, sem chave de acesso, e o
motor as consulta direto:

```bash
cienciometria coletar --revisao <slug> --fonte openalex \
    --busca "fiscal federalism" --email voce@exemplo.org --limite 3000
cienciometria importar --revisao <slug>
```

O comando pagina por cursor, salva a **resposta crua** em `dados/bruto/openalex_<data>/` e registra
a execução em `config/execucao.json` — consulta, filtros, data, hora e contagem. O mapeamento para o
corpus acontece na importação: ajustar o mapeamento depois não exige consultar a API de novo.

| Fonte | Vantagem | Limite a declarar |
|---|---|---|
| **OpenAlex** | Cobertura ampla; traz referências citadas (`referenced_works`), afiliação com país e acesso aberto | Palavras-chave são conceitos inferidos por máquina, não termos de autor |
| **Crossref** | Cobre tudo o que tem DOI | Referências só quando a editora as deposita; afiliação quase sempre ausente, o que enfraquece as redes de colaboração |

Três cuidados que precisam ir para o texto da revisão, não ficar implícitos:

1. **Conceito do OpenAlex não é palavra-chave de autor.** Serve para a rede de co-palavras, mas
   muda o que a rede significa — diga isso ao relatar.
2. **A busca por API não é a mesma da interface.** `title_and_abstract.search` tem processamento
   textual próprio; não espere o mesmo conjunto que a string do Scopus devolve. Usando as duas,
   relate cada uma separadamente.
3. **Teto de registros.** `--limite` corta a coleta; atingir o teto significa corpus truncado — o
   comando avisa, e a decisão (refinar a busca ou elevar o teto) precisa ficar registrada.

Se a coleta falhar:

| Mensagem | Significado | O que fazer |
|---|---|---|
| HTTP 403 ao consultar | A rede, ou uma política de egresso, bloqueia o host | Usar outra rede; não há como contornar de dentro. A alternativa é exportar pela interface da base |
| Nenhum resultado | Termos restritivos demais, ou filtro de ano/tipo excluindo tudo | Testar a mesma consulta na interface web da fonte antes de concluir que não há literatura |
| Registros sem afiliação ou sem referências | A fonte não traz esses campos ali | Declarar a cobertura; considerar complementar com outra base |

## 6 Registro da execução

Cada busca executada gera uma entrada em `config/execucao.json`: base, identificador da string,
data, hora, filtros, número de resultados e arquivo gerado. É esse registro — e não a memória —
que permite a outra pessoa repetir a busca e comparar.
