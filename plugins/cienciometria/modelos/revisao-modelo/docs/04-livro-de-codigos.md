# Livro de códigos — {{TITULO}}

As variáveis automáticas (identificação, autoria, publicação, impacto) são as mesmas em qualquer
revisão e estão descritas no [livro de códigos do motor](../../../docs/04-livro-de-codigos.md).
Este documento traz apenas o que é específico deste tema.

## 1 Variáveis de conteúdo (codificação manual)

| Variável | Tipo | Domínio | Regra |
|---|---|---|---|
| `abordagem` | categórica | teorica, empirica_quant, empirica_qual, mista, normativa_juridica, revisao | Do desenho do trabalho |
| `tema_declarado` | categórica múltipla | ver §2 | Até 3, em ordem de centralidade |
| `pais_do_caso` | lista | ISO-3, `XXX` teórico, `MUL` > 5 países | Do objeto empírico |
| «variável própria» | | | |

## 2 Vocabulário de temas

Deve espelhar `vocabulario_temas` em `config/revisao.json`.

| Código | Tema | Abrange |
|---|---|---|
| T01 | | |
| T02 | | |

> Tema novo só é criado se pelo menos 5 registros não couberem nos existentes, e a criação vira
> emenda ao protocolo.

## 3 Tesauros

| Arquivo | Função |
|---|---|
| `config/thesauro-termos.json` | Unifica palavras-chave entre idiomas e grafias |
| `config/thesauro-fontes.json` | Unifica nomes de periódicos |
| `config/thesauro-instituicoes.json` | Unifica afiliações |

O motor carrega primeiro os tesauros de `config/` da raiz (comuns a todas as revisões, como o
léxico de países) e depois os desta revisão, que prevalecem. Nenhuma normalização é feita
diretamente no dado.
