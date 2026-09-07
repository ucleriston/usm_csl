"""Indicadores de desempenho do corpus (plano de análise, §1).

Cada função devolve estruturas simples (listas de dicionários) que o módulo
relatorio converte em CSV e em texto. Sem dependências externas.
"""

import math
import re
from collections import Counter, defaultdict


def producao_anual(corpus, ano_corte=None):
    contagem = Counter(int(r["ano"]) for r in corpus if r.get("ano"))
    if not contagem:
        return []
    inicio, fim = min(contagem), ano_corte or max(contagem)
    citacoes = defaultdict(int)
    for r in corpus:
        if r.get("ano"):
            citacoes[int(r["ano"])] += int(r.get("citacoes") or 0)
    linhas, acumulado = [], 0
    for ano in range(inicio, fim + 1):
        acumulado += contagem.get(ano, 0)
        linhas.append(
            {
                "ano": ano,
                "publicacoes": contagem.get(ano, 0),
                "acumulado": acumulado,
                "citacoes": citacoes.get(ano, 0),
                "citacoes_por_publicacao": round(
                    citacoes.get(ano, 0) / contagem[ano], 2) if contagem.get(ano) else 0.0,
            }
        )
    return linhas


def tcac(serie, janela=3):
    """Taxa de crescimento anual composta, com médias trienais nas pontas."""
    if len(serie) < 2 * janela:
        return None
    inicio = sum(l["publicacoes"] for l in serie[:janela]) / janela
    fim = sum(l["publicacoes"] for l in serie[-janela:]) / janela
    anos = serie[-1]["ano"] - serie[0]["ano"]
    if inicio <= 0 or anos <= 0:
        return None
    return round(((fim / inicio) ** (1.0 / anos) - 1) * 100, 2)


def contagem_por_campo(corpus, campo, fracionaria=False, minimo=1):
    """Contagem integral e fracionária de um campo de lista (autores, países, instituições)."""
    integral, fracao = Counter(), defaultdict(float)
    for r in corpus:
        itens = r.get(campo) or []
        if not itens:
            continue
        peso = 1.0 / len(itens)
        for item in itens:
            integral[item] += 1
            fracao[item] += peso
    linhas = [
        {
            "item": item,
            "publicacoes": n,
            "publicacoes_fracionarias": round(fracao[item], 2),
            "participacao_%": round(100 * n / len(corpus), 2) if corpus else 0.0,
        }
        for item, n in integral.most_common()
        if n >= minimo
    ]
    if fracionaria:
        linhas.sort(key=lambda l: l["publicacoes_fracionarias"], reverse=True)
    return linhas


def lei_de_lotka(corpus):
    """Ajusta y = C / x^alpha por mínimos quadrados em escala log-log.

    Devolve o expoente, o C, a tabela observada/esperada e a estatística de
    Kolmogorov-Smirnov (D) sobre as distribuições acumuladas.
    """
    trabalhos_por_autor = Counter()
    for r in corpus:
        for autor in r.get("autores") or []:
            trabalhos_por_autor[autor] += 1
    if not trabalhos_por_autor:
        return {"alpha": None, "c": None, "tabela": [], "ks": None, "n_autores": 0}

    distribuicao = Counter(trabalhos_por_autor.values())
    xs = sorted(distribuicao)
    n_autores = len(trabalhos_por_autor)

    # regressão linear de log(y) sobre log(x)
    lx = [math.log(x) for x in xs]
    ly = [math.log(distribuicao[x]) for x in xs]
    n = len(xs)
    media_x, media_y = sum(lx) / n, sum(ly) / n
    sxx = sum((v - media_x) ** 2 for v in lx)
    sxy = sum((lx[i] - media_x) * (ly[i] - media_y) for i in range(n))
    inclinacao = sxy / sxx if sxx else 0.0
    alpha = -inclinacao
    intercepto = media_y - inclinacao * media_x
    c_bruto = math.exp(intercepto)

    # normaliza C para que as proporções esperadas somem 1 no domínio observado
    soma = sum(1.0 / (x ** alpha) for x in range(1, max(xs) + 1)) if alpha else 0.0
    c = 1.0 / soma if soma else 0.0

    tabela, acum_obs, acum_esp, ks = [], 0.0, 0.0, 0.0
    for x in xs:
        obs = distribuicao[x] / n_autores
        esp = c / (x ** alpha) if alpha else 0.0
        acum_obs += obs
        acum_esp += esp
        ks = max(ks, abs(acum_obs - acum_esp))
        tabela.append(
            {
                "trabalhos_por_autor": x,
                "autores_observado": distribuicao[x],
                "proporcao_observada": round(obs, 4),
                "proporcao_esperada": round(esp, 4),
                "autores_esperado": round(esp * n_autores, 1),
            }
        )
    critico = 1.36 / math.sqrt(n_autores)  # KS a 5%
    return {
        "alpha": round(alpha, 4),
        "c": round(c, 4),
        "c_bruto": round(c_bruto, 4),
        "n_autores": n_autores,
        "tabela": tabela,
        "ks": round(ks, 4),
        "ks_critico_5%": round(critico, 4),
        # expoente não positivo descreve uma distribuição crescente: não é a Lei de Lotka,
        # por melhor que o teste KS pareça
        "adere": bool(ks <= critico and alpha > 0),
    }


def lei_de_bradford(corpus, zonas=3):
    """Distribui as fontes em zonas com número aproximadamente igual de artigos."""
    contagem = Counter(r["fonte"] for r in corpus if r.get("fonte"))
    if not contagem:
        return {"tabela": [], "zonas": [], "multiplicador": None}
    total = sum(contagem.values())
    alvo = total / zonas
    tabela, acumulado, zona, fontes_na_zona = [], 0, 1, Counter()
    for posicao, (fonte, n) in enumerate(contagem.most_common(), start=1):
        acumulado += n
        tabela.append(
            {
                "posicao": posicao,
                "fonte": fonte,
                "artigos": n,
                "acumulado": acumulado,
                "zona": zona,
            }
        )
        fontes_na_zona[zona] += 1
        if acumulado >= alvo * zona and zona < zonas:
            zona += 1
    resumo = []
    for z in range(1, zonas + 1):
        artigos = sum(l["artigos"] for l in tabela if l["zona"] == z)
        resumo.append(
            {
                "zona": z,
                "fontes": fontes_na_zona[z],
                "artigos": artigos,
                "artigos_%": round(100 * artigos / total, 2),
            }
        )
    multiplicador = None
    if resumo[0]["fontes"]:
        razoes = [resumo[i + 1]["fontes"] / resumo[i]["fontes"] for i in range(len(resumo) - 1)
                  if resumo[i]["fontes"]]
        if razoes:
            multiplicador = round(sum(razoes) / len(razoes), 2)
    return {"tabela": tabela, "zonas": resumo, "multiplicador": multiplicador}


_ANO_REF = re.compile(r"(1[89]\d{2}|20\d{2})")


def indice_de_price(corpus, janela=5):
    """% de referências com até `janela` anos na data da publicação citante."""
    linhas, recentes_total, refs_total = [], 0, 0
    idades = []
    for r in corpus:
        ano_pub = int(r.get("ano") or 0)
        refs = r.get("referencias") or []
        if not ano_pub or not refs:
            continue
        recentes, contadas = 0, 0
        for ref in refs:
            anos = [int(a) for a in _ANO_REF.findall(ref)]
            anos = [a for a in anos if a <= ano_pub]
            if not anos:
                continue
            ano_ref = max(anos)
            idade = ano_pub - ano_ref
            idades.append(idade)
            contadas += 1
            if idade <= janela:
                recentes += 1
        if contadas:
            linhas.append(
                {
                    "id": r["id"],
                    "ano": ano_pub,
                    "referencias_datadas": contadas,
                    "recentes": recentes,
                    "indice_price": round(100 * recentes / contadas, 2),
                }
            )
            recentes_total += recentes
            refs_total += contadas
    idades.sort()
    meia_vida = idades[len(idades) // 2] if idades else None
    return {
        "detalhe": linhas,
        "indice_price_corpus": round(100 * recentes_total / refs_total, 2) if refs_total else None,
        "referencias_datadas": refs_total,
        "meia_vida_citada": meia_vida,
        "cobertura_%": round(100 * len(linhas) / len(corpus), 2) if corpus else 0.0,
    }


def h_index(citacoes):
    h = 0
    for i, c in enumerate(sorted(citacoes, reverse=True), start=1):
        if c >= i:
            h = i
        else:
            break
    return h


def impacto(corpus, ano_corte):
    cits = [int(r.get("citacoes") or 0) for r in corpus]
    total = sum(cits)
    for r in corpus:
        ano = int(r.get("ano") or 0)
        idade = max(1, (ano_corte - ano) + 1) if ano else 1
        r["citacoes_por_ano"] = round(int(r.get("citacoes") or 0) / idade, 2)
    mais_citados = sorted(corpus, key=lambda r: int(r.get("citacoes") or 0), reverse=True)[:25]
    return {
        "citacoes_totais": total,
        "media_por_trabalho": round(total / len(corpus), 2) if corpus else 0.0,
        "sem_citacao_%": round(100 * sum(1 for c in cits if c == 0) / len(cits), 2) if cits else 0.0,
        "h_index": h_index(cits),
        "mais_citados": [
            {
                "id": r["id"],
                "autores": "; ".join((r.get("autores") or [])[:3]),
                "ano": r.get("ano"),
                "titulo": r.get("titulo"),
                "fonte": r.get("fonte"),
                "citacoes": r.get("citacoes"),
                "citacoes_por_ano": r.get("citacoes_por_ano"),
                "doi": r.get("doi"),
            }
            for r in mais_citados
        ],
    }


def colaboracao(corpus):
    com_coautoria = [r for r in corpus if (r.get("n_autores") or 0) > 1]
    autores_total = sum(int(r.get("n_autores") or 0) for r in corpus)
    internacionais = [r for r in corpus if int(r.get("colab_internacional") or 0) == 1]
    scp = mcp = 0
    por_pais = defaultdict(lambda: {"scp": 0, "mcp": 0})
    for r in corpus:
        paises = r.get("paises") or []
        if not paises:
            continue
        if len(paises) > 1:
            mcp += 1
            for p in paises:
                por_pais[p]["mcp"] += 1
        else:
            scp += 1
            por_pais[paises[0]]["scp"] += 1
    tabela_paises = [
        {
            "pais": p,
            "scp": v["scp"],
            "mcp": v["mcp"],
            "total": v["scp"] + v["mcp"],
            "mcp_%": round(100 * v["mcp"] / (v["scp"] + v["mcp"]), 2) if (v["scp"] + v["mcp"]) else 0.0,
        }
        for p, v in sorted(por_pais.items(), key=lambda kv: -(kv[1]["scp"] + kv[1]["mcp"]))
    ]
    return {
        "autores_por_trabalho": round(autores_total / len(corpus), 2) if corpus else 0.0,
        "indice_colaboracao": round(
            sum(int(r["n_autores"]) for r in com_coautoria) / len(com_coautoria), 2
        ) if com_coautoria else 0.0,
        "trabalhos_com_um_autor_%": round(
            100 * (len(corpus) - len(com_coautoria)) / len(corpus), 2) if corpus else 0.0,
        "coautoria_internacional_%": round(
            100 * len(internacionais) / len(corpus), 2) if corpus else 0.0,
        "scp": scp,
        "mcp": mcp,
        "por_pais": tabela_paises,
    }
