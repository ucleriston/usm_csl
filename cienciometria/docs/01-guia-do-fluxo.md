# Guia do fluxo — como conduzir uma revisão cienciométrica com este motor

Vale para qualquer tema. O que muda de uma revisão para outra são os documentos e a configuração
dentro de `revisoes/<slug>/`; o pipeline é o mesmo.

---

## 0 Antes de tudo: a revisão é do tema ou do campo?

Cienciometria descreve **o campo que estuda um tema** — quem publica, onde, com quem, sobre o quê,
citando quem. Ela não responde o que o campo *concluiu*. Se a sua pergunta é "o que se sabe sobre
X?", você quer uma revisão sistemática ou integrativa, e este motor só ajuda na etapa de
identificação. Se a pergunta é "como o conhecimento sobre X está organizado, e o que ficou de
fora?", é aqui.

## 1 Criar a revisão

```bash
python -m cienciometria nova capacidade-estatal-municipal \
    --titulo "Capacidade estatal municipal: mapeamento da produção" \
    --tema "Capacidades administrativas dos governos locais"
```

Cria `revisoes/<slug>/` a partir do esqueleto: documentos-modelo, configuração, tesauros vazios e
as pastas de dados e saídas.

## 2 Delimitar antes de buscar

Preencha, nesta ordem — cada um alimenta o seguinte:

1. `docs/01-projeto-de-pesquisa.md` — tema, problema, perguntas, proposições, objetivos.
2. `config/revisao.json` — o mesmo recorte em forma de máquina: janela, idiomas, tipos, limiares,
   subperíodos, códigos de exclusão e **as proposições com o critério que as refuta**.
3. `docs/02-protocolo-prisma.md` — elegibilidade, fontes, procedimento de triagem.
4. `docs/03-estrategias-de-busca.md` — blocos e strings por base.
5. `docs/04-livro-de-codigos.md` — o que será codificado à mão e com que vocabulário.

> A regra que sustenta tudo: **o critério de refutação é escrito antes de existir resultado.** É a
> diferença entre descrever um campo e confirmar a própria expectativa.

## 3 Calibrar a busca

Monte o conjunto-semente (`config/sementes.csv`) com trabalhos que você já sabe pertinentes — e
que entraram na lista *antes* de qualquer busca. Rode a string e veja quantos ela recupera. Recall
baixo significa string ruim, não literatura escassa.

## 4 Buscar e exportar

Salve as exportações em `revisoes/<slug>/dados/bruto/`, com o nome da base no arquivo
(`scopus_2026-04-10.csv`, `wos_2026-04-10_01.txt`, `scielo_2026-04-10.ris`). Registre cada execução
em `config/execucao.json`: string, filtros, data, hora, contagem e arquivo. Sem esse registro a
execução não existe para efeito de relato.

## 5 Construir o corpus

```bash
make importar REVISAO=<slug>     # lê, normaliza e junta as bases
make dedup    REVISAO=<slug>     # remove duplicatas; separa a faixa de dúvida para conferência
```

Confira à mão o arquivo `revisao-duplicatas.csv` antes de seguir: é ali que ficam os pares que o
programa não teve segurança de fundir.

## 6 Triar

```bash
make triagem REVISAO=<slug>      # planilha cega, uma coluna por revisor
make kappa   REVISAO=<slug> TRIAGEM=revisoes/<slug>/dados/processado/triagem-preenchida.csv
```

Kappa abaixo do mínimo declarado significa critério mal escrito. A resposta é reescrever o critério
e refazer a rodada — não negociar registro a registro.

## 7 Analisar

```bash
make analise REVISAO=<slug>
```

Roda importação, deduplicação, indicadores, redes, PRISMA e relatório. As saídas ficam em
`revisoes/<slug>/saidas/`.

## 8 Interpretar

O relatório entrega números e agrupamentos; ele não entrega leitura. Antes de escrever o artigo:

- leia os 10 itens mais centrais de cada agrupamento e substitua o rótulo automático por um rótulo
  seu;
- confira a cobertura declarada de cada indicador que dependa de campo incompleto;
- relate as proposições refutadas como refutadas.

## 9 Publicar

Versione código, protocolo, strings e a lista de identificadores do corpus. As exportações brutas
de bases proprietárias ficam fora do repositório — ver
[06-reprodutibilidade.md](06-reprodutibilidade.md).
