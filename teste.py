import random
from collections import deque
from itertools import product

from grafo import GrafoLista, GrafoMatriz, caminho_busca_em_profundidade
from fluxo import ford_fulkerson, busca_local, montar_grafo, inverter, avaliar

CLASSES = (GrafoLista, GrafoMatriz)


def edmonds_karp(n, arestas, s, t):
    """Fluxo maximo independente (BFS + matriz de capacidades) para conferencia."""
    cap = [[0] * n for _ in range(n)]
    for u, v, c in arestas:
        cap[u][v] += c
    total = 0
    while True:
        pai = [-1] * n
        pai[s] = s
        fila = deque([s])
        while fila and pai[t] == -1:
            u = fila.popleft()
            for v in range(n):
                if pai[v] == -1 and cap[u][v] > 0:
                    pai[v] = u
                    fila.append(v)
        if pai[t] == -1:
            return total
        a, v = float("inf"), t
        while v != s:
            a, v = min(a, cap[pai[v]][v]), pai[v]
        v = t
        while v != s:
            cap[pai[v]][v] -= a
            cap[v][pai[v]] += a
            v = pai[v]
        total += a


def grafo_aleatorio(rnd, n, m):
    pares = set()
    while len(pares) < m:
        u, v = rnd.sample(range(n), 2)
        pares.add((u, v))
    return [(u, v, rnd.randint(1, 15)) for u, v in sorted(pares)]


# --- instancias conhecidas -------------------------------------------------
for classe in CLASSES:
    g = classe.ler_arquivo("grafos_fluxo/classico_6.txt")
    assert ford_fulkerson(g, 0, 5)[0] == 23, classe
    assert ford_fulkerson(g, 5, 0)[0] == 0, classe

    g = classe.ler_arquivo("grafos_fluxo/inverter_4.txt")
    r = busca_local(g, 0, 3)
    assert (r["fluxo_inicial"], r["fluxo_final"], r["passos"]) == (2, 7, 1), classe

    g = classe.ler_arquivo("grafos_fluxo/inverter_8.txt")  # vertices de 1 a 8
    assert g.vertices[0] == 1
    r = busca_local(g, 1, 8)
    assert (r["fluxo_inicial"], r["fluxo_final"], r["passos"]) == (8, 13, 2), classe

# --- DFS de caminho ignora arestas com peso 0 --------------------------------
for classe in CLASSES:
    g = classe(3, True, True)
    g.adicionar_aresta(0, 1, 0)
    g.adicionar_aresta(1, 2, 5)
    assert caminho_busca_em_profundidade(g, 0, 2) is None, classe
    g.definir_peso(0, 1, 3)
    assert caminho_busca_em_profundidade(g, 0, 2) == [0, 1, 2], classe

# --- a copia nao compartilha referencias com o original ----------------------
for classe in CLASSES:
    g = classe.ler_arquivo("grafos_fluxo/classico_6.txt")
    antes = g.arestas()
    ford_fulkerson(g, 0, 5)
    assert g.arestas() == antes, classe
    c = g.copiar()
    c.definir_peso(0, 1, 999)
    c.remover_aresta(3, 5)
    assert g.peso(0, 1) == 16 and g.peso(3, 5) == 20, classe

# --- Ford-Fulkerson == Edmonds-Karp em grafos aleatorios ----------------------
rnd = random.Random(2026)
for _ in range(300):
    n = rnd.randint(2, 12)
    m = rnd.randint(0, n * (n - 1))
    arestas = grafo_aleatorio(rnd, n, m)
    s, t = rnd.sample(range(n), 2)
    esperado = edmonds_karp(n, arestas, s, t)
    for classe in CLASSES:
        g = montar_grafo(classe(n), arestas)
        fluxo, residual = ford_fulkerson(g, s, t)
        assert fluxo == esperado, (classe, arestas, s, t, fluxo, esperado)
        assert caminho_busca_em_profundidade(residual, s, t) is None
        assert all(p > 0 for _, _, p in residual.arestas())  # arcos de custo 0 apagados

# --- busca local: nunca piora, para em otimo local, nao passa do otimo global ---
for _ in range(60):
    n = rnd.randint(3, 6)
    m = rnd.randint(1, min(8, n * (n - 1)))
    arestas = grafo_aleatorio(rnd, n, m)
    s, t = rnd.sample(range(n), 2)
    for classe in CLASSES:
        g = montar_grafo(classe(n), arestas)
        r = busca_local(g, s, t)
        assert r["fluxo_inicial"] == edmonds_karp(n, arestas, s, t)
        assert r["fluxo_final"] >= r["fluxo_inicial"]
        assert r["fluxo_final"] == edmonds_karp(n, r["solucao"], s, t)
        assert r["passos"] == len(r["invertidas"])
        sol = r["solucao"]
        assert all(avaliar(g, inverter(sol, i), s, t) <= r["fluxo_final"] for i in range(len(sol)))
        otimo = max(
            edmonds_karp(n, [(v, u, c) if inv else (u, v, c) for (u, v, c), inv in zip(arestas, bits)], s, t)
            for bits in product((False, True), repeat=len(arestas))
        )
        assert r["fluxo_final"] <= otimo

print("Todos os testes passaram.")
