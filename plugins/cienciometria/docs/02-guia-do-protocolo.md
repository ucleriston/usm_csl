# Guia do protocolo — o que precisa estar decidido antes da primeira busca

O protocolo é o compromisso que torna a revisão auditável. Este guia diz o que ele precisa conter;
o esqueleto preenchível está em `modelos/revisao-modelo/docs/02-protocolo-prisma.md`.

## 1 Elegibilidade que decide sozinha

Um critério bom é aquele que dois revisores aplicam ao mesmo registro e chegam à mesma resposta sem
conversar. Teste cada um assim: *dá para decidir só com título, resumo e palavras-chave?* Se não
dá, ele pertence à triagem 2 (texto integral), e isso precisa estar escrito.

Escreva os critérios de exclusão como **códigos numerados** e mantenha-os iguais em
`config/revisao.json` — é por eles que o fluxo PRISMA conta as perdas. Um registro excluído recebe
um único código: o de maior precedência na ordem em que estão listados.

## 2 Casos de fronteira decididos de antemão

Todo tema tem sua zona cinzenta. Liste as situações que você já sabe que vão aparecer e decida
agora, por escrito. Decidir depois de ver o resultado é o caminho mais curto para o viés de
confirmação — e é indefensável na revisão por pares.

## 3 Fontes com papel declarado

Para cada base: principal ou complementar, e por quê. Duas advertências que valem para qualquer
tema:

- **Co-citação exige campo de referências.** Bases que não o entregam servem para desempenho, não
  para estrutura intelectual.
- **Cobertura é enviesada por língua.** Se o seu tema tem produção relevante fora do inglês, uma
  base regional precisa entrar já na identificação, não como complemento.

## 4 Triagem que mede a própria concordância

Dois revisores independentes e cegos entre si; calibração numa amostra antes de começar; kappa de
Cohen ao fim de cada rodada; divergência resolvida por consenso e, persistindo, por um terceiro.
Registre o kappa mesmo quando ele for ruim: kappa baixo relatado é limitação; kappa não medido é
falha.

## 5 Extração com codificação verificável

Separe o que o pipeline extrai (metadados) do que exige leitura (abordagem, tema, país do caso).
Para o que exige leitura, defina domínio fechado e recodifique 20% da amostra em duplicata.

## 6 Emendas em vez de reescrita silenciosa

Mudança de critério no meio do caminho é normal e legítima — desde que datada, justificada e
visível na seção de emendas. O que não se faz é ajustar o critério ao resultado sem dizer.
