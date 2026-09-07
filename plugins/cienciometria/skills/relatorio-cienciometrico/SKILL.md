---
name: relatorio-cienciometrico
description: >-
  Monta o relatório final da pesquisa cienciométrica — artigo, capítulo ou relatório técnico — a
  partir dos números da análise e das lacunas do fichamento, seguindo a estrutura consolidada
  (resumo estruturado, introdução em funil, material e métodos com fluxo PRISMA, resultados por tipo
  de análise, discussão, conclusão) e adaptando-se ao modelo do periódico ou do programa. Use SEMPRE
  que o usuário disser escrever o artigo, redigir o relatório, montar o texto final, "como escrevo
  os resultados da bibliometria", "preciso formatar no modelo da revista", "monta o rascunho do
  artigo", "transforma a análise em texto", "gera o relatório em Word" ou estiver na etapa de
  redação de uma revisão cienciométrica. Também para revisar um texto já escrito contra os dados que
  o sustentam.
---

# Relatório final

O texto final não é escrito do zero nem gerado por inteiro: ele é **montado dos dados e escrito por
quem assina**. O motor entrega o esqueleto com todos os números no lugar; a interpretação, a
justificativa e a discussão são do autor.

## 1 Gerar o rascunho

```bash
"$CIENCIO" artigo --revisao <slug>
```

Produz `saidas/artigo.md` com a estrutura completa e duas marcações que não podem sobrar na versão
final:

- **`[ESCREVER: ...]`** — depende de interpretação, leitura ou decisão do autor.
- **`[SEM DADO: ...]`** — o pipeline não produziu aquele valor. Cada um aponta uma etapa que não foi
  executada; a correção é reexecutar a etapa, **nunca** preencher o número de memória.

O comando informa quantas marcações de cada tipo existem. É a medida honesta de quanto falta.

## 2 A estrutura, e o que alimenta cada parte

| Seção | Vem de | Cuidado |
|---|---|---|
| Resumo e abstract | Escritos **por último**, depois do texto pronto | Estrutura: objetivo, métodos, resultados, conclusão |
| 1 Introdução | Funil: tema → o que se sabe → o que falta → objetivo | O parágrafo "o que falta" vem da matriz de lacunas do fichamento, não de impressão |
| 2 Material e Métodos | `execucao.json`, protocolo, `saidas/prisma.md` | Strings completas no apêndice; declare semente, limiares e versão do software |
| 3.1 Temporal e autoria | Produção anual, TCAC, Lotka, colaboração | Descreva o que aconteceu; a explicação vai na discussão |
| 3.2 Periódicos | Bradford, zonas | Zona 1 é onde publicar e onde procurar, não "os melhores" |
| 3.3 Estrutura e parcerias | Co-palavras, mapa temático, redes de coautoria | Rótulo de agrupamento só entra depois de ler os itens centrais |
| 3.4 Citação | Mais citados, co-citação, Price, h-index | Relate citações por ano: ranking puro premia a idade |
| 3.5 Países | SCP/MCP | Contagem integral favorece coautoria numerosa — relate a fracionária também |
| 4 Discussão | Responde às perguntas da introdução, na mesma ordem | Aqui entram as proposições refutadas, e as limitações |
| 5 Conclusão | Retoma o objetivo e aponta a pesquisa seguinte | É a ponte para o projeto do usuário |

A regra de ouro da divisão: **resultados dizem o que foi encontrado; discussão diz o que significa.**
Misturar os dois é o defeito mais comum em artigo cienciométrico, e o mais fácil de corrigir.

## 3 Adaptar ao modelo do usuário

Periódicos e programas têm exigências próprias: número de palavras, resumo estruturado ou corrido,
resultados e discussão juntos ou separados, ordem das seções, limite de figuras. Peça o modelo ou as
normas antes de formatar, e adapte — a estrutura acima é o padrão do campo, não uma camisa de força.

Quando o usuário fornecer um modelo (`.docx` do periódico, manual do programa, orientação do
orientador), trate-o como autoridade sobre **forma**, nunca sobre **conteúdo**: se o modelo pede uma
seção que os dados não sustentam, a resposta é dizer isso, não preencher.

Para entregar em Word seguindo o modelo, use a skill `docx` a partir do `artigo.md` já escrito.
Mantenha o Markdown como fonte: é ele que o motor regenera quando a análise muda.

## 4 Figuras

O motor gera os **dados** das figuras, não as imagens: `producao_anual.csv`, `bradford.csv`,
`lotka.csv`, `mapa_tematico.csv`, e as redes em `.net` e `.gml` para VOSviewer ou Gephi. As legendas
seguem o padrão do campo:

> **Figura X** — Rede de coocorrência das N palavras-chave mais frequentes. Cada nó representa uma
> palavra-chave; a espessura das ligações representa a força de associação. Limiar mínimo: N
> ocorrências. Elaborada com [software].

Toda figura precisa dizer, na legenda: o que é cada nó, o que é cada ligação, o limiar aplicado e a
ferramenta. Sem isso ninguém reproduz.

## 5 Antes de submeter

- Nenhum `[ESCREVER:` ou `[SEM DADO` sobrou no texto.
- Todo número do texto existe em `saidas/`, e a data de corte está declarada.
- Rótulos de agrupamento validados por leitura, não os automáticos.
- Nada chamado de emergente sem a série por subperíodo.
- Proposições refutadas relatadas como refutadas.
- Limitações declaradas: cobertura das bases, campos incompletos, homonímia, limiares.
- Referências conferidas no registro da base — inclusive as de método.
- Material de reprodutibilidade indicado: strings, data de corte, semente, versão do código.

## 6 Quando a análise mudar

Ela vai mudar: um filtro corrigido, uma base acrescentada, o tesauro revisado. Reexecute a análise e
gere o rascunho de novo em outro arquivo, compare, e traga para o texto o que mudou — em vez de
editar números à mão no texto antigo, que é como as inconsistências entram e ficam.
