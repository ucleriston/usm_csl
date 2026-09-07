# Instalar o plugin Cienciometria

Requisito: Python 3.9 ou superior. Nenhuma biblioteca externa.

## Opção 1 — instalação local (funciona agora)

Descompacte o pacote numa pasta que você vá manter, por exemplo `~/plugins-claude/`. Depois, dentro
do Claude Code:

```
/plugin marketplace add ~/plugins-claude/cienciometria-marketplace
/plugin install cienciometria@usm-csl
```

O caminho é o da pasta que contém `.claude-plugin/marketplace.json` — a raiz do que você
descompactou. Confira com `/plugin` que ele aparece instalado, e com `/help` que os comandos
apareceram.

## Opção 2 — direto do GitHub

Requer o conteúdo no **branch padrão** do repositório. Hoje o plugin está no branch
`claude/federalismo-fiscal-cienciometria-80gdzo`; depois de mesclá-lo (ou de trocar o branch padrão
nas configurações do repositório):

```
/plugin marketplace add ucleriston/usm_csl
/plugin install cienciometria@usm-csl
```

É a melhor opção no dia a dia, porque atualiza com `/plugin marketplace update usm-csl`.

## Primeiro contato

Fale naturalmente:

> quero mapear a literatura sobre [seu tema], por onde começo?

Ou use o comando de entrada, que funciona mesmo sem nenhuma revisão criada:

```
/estado-da-pesquisa
```

A skill de entrada é `pesquisa-cienciometrica`. Ela conduz oito etapas — escopo, protocolo, busca,
corpus, triagem, análise, fichamento e artigo — e **mantém o estado no disco**: você fecha o
computador, volta em três semanas, roda `/estado-da-pesquisa` e ela diz exatamente onde parou.

## Testar o pipeline inteiro sem gastar busca nenhuma

O plugin traz um gerador de amostra **sintética** (registros fabricados, não são reais — nenhum
número dali pode ser citado). Numa pasta de trabalho qualquer:

```bash
PLUGIN=~/.claude/plugins/cienciometria          # ajuste para onde ficou instalado

"$PLUGIN/bin/cienciometria" nova teste --titulo "Teste" --tema "Qualquer coisa"
python3 "$PLUGIN/exemplo/gerar-dados-sinteticos.py" ./revisoes/teste/dados/bruto
"$PLUGIN/bin/cienciometria" analise --revisao teste
"$PLUGIN/bin/cienciometria" fichar  --revisao teste --sugerir
"$PLUGIN/bin/cienciometria" artigo  --revisao teste
"$PLUGIN/bin/cienciometria" estado  --revisao teste
```

Ao final, olhe `revisoes/teste/saidas/`: relatório, artigo, tabelas e as redes em `.net` e `.gml`
(abrem no VOSviewer e no Gephi).

## Onde o plugin escreve

As revisões são criadas **na sua pasta de trabalho**, em `./revisoes/<slug>/` — nunca dentro da
instalação. Para trabalhar noutra pasta, defina `CIENCIOMETRIA_DIR=/caminho/do/projeto`.

## Se algo não funcionar

| Sintoma | Causa provável | Saída |
|---|---|---|
| `/plugin marketplace add` não encontra nada | Caminho apontando para a pasta errada | Aponte para a pasta que contém `.claude-plugin/marketplace.json` |
| `bin/cienciometria: permission denied` | Bit de execução perdido na descompactação | `chmod +x "$PLUGIN/bin/cienciometria"` |
| `python3: command not found` | Python ausente ou com outro nome | Instale o Python 3.9+, ou defina `CIENCIOMETRIA_PYTHON=python` |
| As skills não disparam sozinhas | Plugin instalado mas não habilitado | `/plugin` e habilite; ou chame pelo comando `/estado-da-pesquisa` |
