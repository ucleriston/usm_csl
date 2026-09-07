---
description: Lê as saídas de uma análise bibliométrica e escreve a seção de resultados
argument-hint: [slug da revisão ou caminho das saídas]
---

Interprete os resultados de **$ARGUMENTS** seguindo a skill `interpretar-resultados`.

1. Leia `saidas/relatorio.md` e `saidas/resultados.json`.
2. Rotule os agrupamentos de verdade: para cada um, pegue os 10 itens de maior frequência em
   `saidas/<rede>_nos.csv`, encontre esses trabalhos no corpus e leia título e resumo. O rótulo
   automático do motor é pista, não resposta.
3. Antes de chamar qualquer tema de emergente, confira a série por subperíodo em
   `saidas/evolucao_tematica.csv` — emergente e em declínio ocupam o mesmo quadrante do mapa.
4. Escreva a seção de resultados na ordem: corpus e fluxo, desempenho, estrutura intelectual,
   social e conceitual, evolução, proposições e limitações.

Cada afirmação precisa estar ancorada num número que existe nas saídas, com a fonte nomeada.
Lacuna só é declarada depois de descartar que seja limite da busca. E o que foi refutado entra no
texto como refutado.
