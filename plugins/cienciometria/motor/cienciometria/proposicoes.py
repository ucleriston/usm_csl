"""Avaliação declarativa das proposições da revisão.

As proposições vivem em config/revisao.json de cada revisão, com o critério de
refutação escrito ANTES de haver resultado. Este módulo só aplica o critério ao
que o pipeline calculou — ele não decide nada por conta própria.

Formato de uma proposição:

    {
      "id": "P1",
      "enunciado": "A produtividade dos autores segue a Lei de Lotka",
      "indicador": "expoente α e teste KS",
      "criterio": {"tipo": "todos", "condicoes": [
          {"campo": "lotka.alpha", "operador": "entre", "valor": [1.7, 2.3]},
          {"campo": "lotka.adere", "operador": "==", "valor": true}]}
    }

Tipos de critério: "condicao" (uma só), "todos" (conjunção), "algum" (disjunção)
e "manual" (depende de codificação humana — relatado como pendente, nunca como
sustentado).
"""

OPERADORES = {
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "entre": lambda a, b: b[0] <= a <= b[1],
    "fora": lambda a, b: not (b[0] <= a <= b[1]),
    "contem": lambda a, b: b in a if a is not None else False,
}


def valor_em(dados, caminho):
    """Lê um valor por caminho pontuado, com índice numérico para listas.

    Ex.: "bradford.zonas.0.artigos_%", "copalavras.metricas.componente_gigante_%".
    """
    atual = dados
    for parte in str(caminho).split("."):
        if atual is None:
            return None
        if isinstance(atual, list):
            try:
                atual = atual[int(parte)]
                continue
            except (ValueError, IndexError):
                return None
        if isinstance(atual, dict):
            if parte in atual:
                atual = atual[parte]
                continue
            return None
        return None
    return atual


def _avaliar_condicao(condicao, resultados):
    campo = condicao.get("campo")
    operador = condicao.get("operador", ">=")
    esperado = condicao.get("valor")
    obtido = valor_em(resultados, campo)
    if obtido is None:
        return None, "%s = indisponível" % campo
    funcao = OPERADORES.get(operador)
    if funcao is None:
        return None, "operador desconhecido: %s" % operador
    try:
        return bool(funcao(obtido, esperado)), "%s = %s" % (campo, obtido)
    except (TypeError, ValueError, IndexError):
        return None, "%s = %s (incomparável com %s)" % (campo, obtido, esperado)


def avaliar_uma(proposicao, resultados):
    criterio = proposicao.get("criterio") or {"tipo": "manual"}
    tipo = criterio.get("tipo", "condicao")

    if tipo == "manual":
        return {
            "proposicao": "%s — %s" % (proposicao.get("id", "?"), proposicao.get("enunciado", "")),
            "indicador": proposicao.get("indicador", ""),
            "valor": criterio.get("observacao", "depende de codificação manual"),
            "situacao": "exige etapa manual",
        }

    condicoes = criterio.get("condicoes") or ([criterio] if criterio.get("campo") else [])
    veredictos, descricoes = [], []
    for condicao in condicoes:
        veredicto, descricao = _avaliar_condicao(condicao, resultados)
        veredictos.append(veredicto)
        descricoes.append(descricao)

    if not veredictos or any(v is None for v in veredictos):
        situacao = "não avaliável"
    elif tipo == "algum":
        situacao = "sustentada" if any(veredictos) else "refutada"
    else:  # "todos" e "condicao"
        situacao = "sustentada" if all(veredictos) else "refutada"

    return {
        "proposicao": "%s — %s" % (proposicao.get("id", "?"), proposicao.get("enunciado", "")),
        "indicador": proposicao.get("indicador", ""),
        "valor": "; ".join(descricoes) or "sem condições declaradas",
        "situacao": situacao,
    }


def avaliar(proposicoes, resultados):
    """Avalia todas as proposições declaradas na revisão."""
    if not proposicoes:
        return [{
            "proposicao": "nenhuma proposição declarada",
            "indicador": "—",
            "valor": "config/revisao.json não traz o campo 'proposicoes'",
            "situacao": "não avaliável",
        }]
    return [avaliar_uma(p, resultados) for p in proposicoes]
