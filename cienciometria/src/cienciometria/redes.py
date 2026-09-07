"""Redes e mapeamento de ciência (plano de análise, §§2-4).

Construção de redes de coocorrência, normalização por força de associação
(mesma do VOSviewer), agrupamento por propagação de rótulos com semente fixa,
mapa temático de Callon e exportação em Pajek, GML e lista de arestas.
"""

import random
import re
from collections import Counter, defaultdict

from .normalizacao import chave_texto


# --------------------------------------------------------------------- construção

def rede_coocorrencia(listas, minimo=2, limite_nos=300):
    """Rede não dirigida a partir de listas de itens coocorrentes por documento.

    Devolve (nos, arestas), com `nos` = {item: frequência} e
    `arestas` = {(a, b): peso}, a < b.
    """
    frequencia = Counter()
    for itens in listas:
        for item in set(itens):
            frequencia[item] += 1
    selecionados = {
        item for item, n in frequencia.most_common(limite_nos) if n >= minimo
    }
    arestas = Counter()
    for itens in listas:
        presentes = sorted(set(i for i in itens if i in selecionados))
        for i in range(len(presentes)):
            for j in range(i + 1, len(presentes)):
                arestas[(presentes[i], presentes[j])] += 1
    nos = {item: frequencia[item] for item in selecionados}
    return nos, dict(arestas)


def normalizar_associacao(nos, arestas):
    """Força de associação: w_ij / (s_i * s_j), normalizada pela média."""
    if not arestas:
        return {}
    bruto = {
        (a, b): peso / (nos[a] * nos[b]) for (a, b), peso in arestas.items() if nos.get(a) and nos.get(b)
    }
    media = sum(bruto.values()) / len(bruto)
    return {par: valor / media for par, valor in bruto.items()} if media else bruto


def rede_coautoria(corpus, campo="autores", minimo=2, limite_nos=300):
    return rede_coocorrencia([r.get(campo) or [] for r in corpus], minimo, limite_nos)


def rede_copalavras(corpus, campo="palavras_chave", minimo=5, limite_nos=200):
    return rede_coocorrencia([r.get(campo) or [] for r in corpus], minimo, limite_nos)


def _chave_referencia(ref):
    """Chave curta e estável de uma referência citada: autor + ano (+ doi, se houver)."""
    ref = re.sub(r"\s+", " ", ref.strip())
    doi = re.search(r"10\.\d{4,9}/\S+", ref)
    if doi:
        return doi.group(0).lower().rstrip(".,;")
    ano = re.search(r"(1[89]\d{2}|20\d{2})", ref)
    autor = re.split(r"[,.]", ref)[0].strip()
    autor = chave_texto(autor)[:40]
    if not autor:
        return ""
    return "%s (%s)" % (autor.upper(), ano.group(0) if ano else "s.d.")


def rede_cocitacao(corpus, minimo=5, limite_nos=200):
    """Co-citação de referências, restrita ao subcorpus com campo de referências."""
    subcorpus = [r for r in corpus if r.get("referencias")]
    listas = [[_chave_referencia(x) for x in r["referencias"]] for r in subcorpus]
    listas = [[c for c in l if c] for l in listas]
    nos, arestas = rede_coocorrencia(listas, minimo, limite_nos)
    cobertura = round(100 * len(subcorpus) / len(corpus), 2) if corpus else 0.0
    return nos, arestas, {"documentos_com_referencias": len(subcorpus), "cobertura_%": cobertura}


def acoplamento_bibliografico(corpus, minimo=3, limite_nos=300):
    """Documentos ligados pelo número de referências compartilhadas."""
    subcorpus = [r for r in corpus if r.get("referencias")]
    chaves = {
        r["id"]: set(c for c in (_chave_referencia(x) for x in r["referencias"]) if c)
        for r in subcorpus
    }
    ordenados = sorted(subcorpus, key=lambda r: -len(chaves[r["id"]]))[:limite_nos]
    ids = [r["id"] for r in ordenados]
    rotulos = {
        r["id"]: "%s (%s)" % (
            (r.get("autores") or ["s.a."])[0].split(",")[0], r.get("ano") or "s.d.")
        for r in ordenados
    }
    arestas = {}
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            comum = len(chaves[ids[i]] & chaves[ids[j]])
            if comum >= minimo:
                arestas[(rotulos[ids[i]] + "|" + ids[i], rotulos[ids[j]] + "|" + ids[j])] = comum
    nos = {rotulos[i] + "|" + i: len(chaves[i]) for i in ids}
    return nos, arestas


# --------------------------------------------------------------------- agrupamento

def propagacao_de_rotulos(nos, arestas, semente=42, iteracoes=30, repeticoes=20):
    """Agrupamento por propagação de rótulos ponderada, com partição modal.

    Procedimento estocástico: repete `repeticoes` vezes com sementes derivadas de
    `semente` e adota a partição mais frequente (pelo número de agrupamentos e
    pela assinatura da partição), como declarado no plano de análise.
    """
    if not nos:
        return {}
    vizinhos = defaultdict(dict)
    for (a, b), peso in arestas.items():
        vizinhos[a][b] = peso
        vizinhos[b][a] = peso

    candidatas = []
    for repeticao in range(repeticoes):
        rng = random.Random(semente + repeticao)
        rotulo = {no: i for i, no in enumerate(sorted(nos))}
        ordem = sorted(nos)
        for _ in range(iteracoes):
            rng.shuffle(ordem)
            mudou = False
            for no in ordem:
                if not vizinhos[no]:
                    continue
                pesos = defaultdict(float)
                for viz, peso in vizinhos[no].items():
                    pesos[rotulo[viz]] += peso
                melhor = max(pesos.items(), key=lambda kv: (kv[1], -kv[0]))[0]
                if melhor != rotulo[no]:
                    rotulo[no] = melhor
                    mudou = True
            if not mudou:
                break
        assinatura = tuple(sorted((no, rotulo[no]) for no in ordem))
        candidatas.append(assinatura)

    modal = Counter(candidatas).most_common(1)[0][0]
    bruto = dict(modal)
    # renumera os agrupamentos por tamanho decrescente
    tamanhos = Counter(bruto.values())
    ordem_final = {r: i + 1 for i, (r, _) in enumerate(tamanhos.most_common())}
    return {no: ordem_final[r] for no, r in bruto.items()}


def mapa_tematico(nos, arestas, agrupamentos):
    """Centralidade e densidade de Callon por agrupamento, com os quadrantes."""
    internas = defaultdict(float)
    externas = defaultdict(float)
    tamanho = Counter(agrupamentos.values())
    for (a, b), peso in arestas.items():
        ca, cb = agrupamentos.get(a), agrupamentos.get(b)
        if ca is None or cb is None:
            continue
        if ca == cb:
            internas[ca] += peso
        else:
            externas[ca] += peso
            externas[cb] += peso
    linhas = []
    for c in sorted(tamanho):
        w = tamanho[c]
        centralidade = 10 * externas[c]
        densidade = 100 * (internas[c] / w) if w else 0.0
        termos = sorted(
            [n for n in agrupamentos if agrupamentos[n] == c],
            key=lambda n: -nos.get(n, 0),
        )
        linhas.append(
            {
                "agrupamento": c,
                "itens": w,
                "centralidade": round(centralidade, 2),
                "densidade": round(densidade, 2),
                "termos_representativos": "; ".join(termos[:8]),
                "rotulo_provisorio": termos[0] if termos else "",
            }
        )
    if len(linhas) == 1:
        linhas[0]["quadrante"] = "indefinido (agrupamento unico)"
    elif linhas:
        centros = sorted(l["centralidade"] for l in linhas)
        dens = sorted(l["densidade"] for l in linhas)
        med_c = centros[len(centros) // 2]
        med_d = dens[len(dens) // 2]
        for l in linhas:
            alta_c = l["centralidade"] >= med_c
            alta_d = l["densidade"] >= med_d
            l["quadrante"] = (
                "motor" if alta_c and alta_d
                else "basico_transversal" if alta_c and not alta_d
                else "nicho" if alta_d
                else "emergente_ou_declinio"
            )
    return linhas


def evolucao_tematica(corpus, cortes=((1990, 1999), (2000, 2009), (2010, 2019), (2020, 2100)),
                      campo="palavras_chave", topo=15):
    """Termos mais frequentes por subperíodo e índice de inclusão entre períodos."""
    periodos = []
    for inicio, fim in cortes:
        subcorpus = [r for r in corpus if inicio <= int(r.get("ano") or 0) <= fim]
        contagem = Counter(t for r in subcorpus for t in set(r.get(campo) or []))
        periodos.append(
            {
                "periodo": "%d-%s" % (inicio, "corte" if fim > 2090 else fim),
                "documentos": len(subcorpus),
                "termos": contagem.most_common(topo),
                "conjunto": set(t for t, _ in contagem.most_common(topo)),
            }
        )
    fluxos = []
    for i in range(len(periodos) - 1):
        a, b = periodos[i], periodos[i + 1]
        if not a["conjunto"] or not b["conjunto"]:
            continue
        comum = a["conjunto"] & b["conjunto"]
        fluxos.append(
            {
                "de": a["periodo"],
                "para": b["periodo"],
                "termos_mantidos": len(comum),
                "indice_inclusao": round(len(comum) / min(len(a["conjunto"]), len(b["conjunto"])), 3),
                "novos": "; ".join(sorted(b["conjunto"] - a["conjunto"])[:10]),
                "abandonados": "; ".join(sorted(a["conjunto"] - b["conjunto"])[:10]),
            }
        )
    for p in periodos:
        p.pop("conjunto")
    return periodos, fluxos


# --------------------------------------------------------------------- exportação

def exportar_pajek(caminho, nos, arestas):
    """Formato .net, lido por VOSviewer e Gephi."""
    indice = {no: i + 1 for i, no in enumerate(sorted(nos))}
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write("*Vertices %d\n" % len(indice))
        for no, i in sorted(indice.items(), key=lambda kv: kv[1]):
            fh.write('%d "%s"\n' % (i, no.replace('"', "'")))
        fh.write("*Edges\n")
        for (a, b), peso in sorted(arestas.items()):
            fh.write("%d %d %s\n" % (indice[a], indice[b], peso))


def exportar_gml(caminho, nos, arestas, agrupamentos=None):
    indice = {no: i for i, no in enumerate(sorted(nos))}
    with open(caminho, "w", encoding="utf-8") as fh:
        fh.write("graph [\n  directed 0\n")
        for no, i in sorted(indice.items(), key=lambda kv: kv[1]):
            fh.write('  node [\n    id %d\n    label "%s"\n    frequencia %d\n' %
                     (i, no.replace('"', "'"), nos[no]))
            if agrupamentos:
                fh.write("    agrupamento %d\n" % agrupamentos.get(no, 0))
            fh.write("  ]\n")
        for (a, b), peso in sorted(arestas.items()):
            fh.write("  edge [\n    source %d\n    target %d\n    weight %s\n  ]\n" %
                     (indice[a], indice[b], peso))
        fh.write("]\n")


def metricas_da_rede(nos, arestas):
    """Grau, densidade, componentes e componente gigante — sem dependências externas."""
    grau = defaultdict(float)
    vizinhos = defaultdict(set)
    for (a, b), peso in arestas.items():
        grau[a] += peso
        grau[b] += peso
        vizinhos[a].add(b)
        vizinhos[b].add(a)
    n = len(nos)
    possiveis = n * (n - 1) / 2 if n > 1 else 0
    vistos, componentes = set(), []
    for no in sorted(nos):
        if no in vistos:
            continue
        pilha, comp = [no], []
        vistos.add(no)
        while pilha:
            atual = pilha.pop()
            comp.append(atual)
            for viz in vizinhos[atual]:
                if viz not in vistos:
                    vistos.add(viz)
                    pilha.append(viz)
        componentes.append(comp)
    gigante = max((len(c) for c in componentes), default=0)
    return {
        "nos": n,
        "arestas": len(arestas),
        "densidade": round(len(arestas) / possiveis, 4) if possiveis else 0.0,
        "componentes": len(componentes),
        "componente_gigante": gigante,
        "componente_gigante_%": round(100 * gigante / n, 2) if n else 0.0,
        "grau_medio_ponderado": round(sum(grau.values()) / n, 2) if n else 0.0,
        "top_grau": sorted(grau.items(), key=lambda kv: -kv[1])[:20],
    }
