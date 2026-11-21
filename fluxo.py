from grafo import GrafoLista, GrafoMatriz, caminho_busca_em_profundidade

EPS = 1e-9  # tolerancia para considerar uma capacidade (float) como zero


def ford_fulkerson(grafo, origem, destino, caminhos=None):
    """Fluxo maximo de 'origem' (fonte) ate 'destino' (sorvedouro).

    Segue o pseudocodigo dos slides:
      - cria um grafo auxiliar como copia do original
      - S = 0
      - enquanto existir caminho P de capacidade positiva da fonte ate o sorvedouro:
          A = menor arco de P;  S += A
          para cada arco (u,v) de P:
              subtrai A de (u,v)
              se existe (v,u) soma A em (v,u), senao cria (v,u) com valor A

    Se 'caminhos' for uma lista, cada caminho aumentante encontrado e adicionado
    a ela como (lista_de_vertices, valor).
    Retorna (S, grafo_residual).
    """
    if origem == destino:
        raise ValueError("A origem e o destino precisam ser vertices diferentes")

    # Copia de verdade (listas/matriz novas): o grafo original nao e alterado.
    residual = grafo.copiar()
    S = 0

    while True:
        # Caminho aumentante pela busca em profundidade da M1 (ignora arcos com peso 0)
        P = caminho_busca_em_profundidade(residual, origem, destino)
        if P is None:
            break

        arcos = list(zip(P, P[1:]))
        A = min(residual.peso(u, v) for u, v in arcos)
        S += A

        for u, v in arcos:
            restante = residual.peso(u, v) - A
            if restante <= EPS:
                residual.remover_aresta(u, v)  # arco de capacidade 0 e apagado
            else:
                residual.definir_peso(u, v, restante)
            residual.somar_peso(v, u, A)  # soma em (v,u) se existir, senao cria (v,u) = A

        if caminhos is not None:
            caminhos.append((P, A))

    return S, residual


def fluxo_nas_arestas(grafo, residual):
    """Fluxo que passa em cada aresta do grafo original: capacidade - residual (se > 0)."""
    fluxo = {}
    for u, v, c in grafo.copiar().arestas():
        r = residual.peso(u, v) or 0
        if c - r > EPS:
            fluxo[(u, v)] = c - r
    return fluxo


# ---------------------------------------------------------------------------
# Busca local
# ---------------------------------------------------------------------------

def montar_grafo(modelo, arestas):
    """Cria um grafo novo (mesma representacao de 'modelo') com as arestas dadas."""
    g = type(modelo)(modelo.num_vertices, True, True, modelo.base)
    for u, v, c in arestas:
        g.somar_peso(u, v, c)  # se o arco ja existir as capacidades sao somadas
    return g


def inverter(solucao, i):
    """Solucao vizinha: a mesma lista de arestas com a aresta i em direcao contraria."""
    u, v, c = solucao[i]
    vizinha = list(solucao)
    vizinha[i] = (v, u, c)
    return vizinha


def avaliar(modelo, solucao, origem, destino):
    return ford_fulkerson(montar_grafo(modelo, solucao), origem, destino)[0]


def busca_local(grafo, origem, destino, max_passos=None, mostrar=False):
    """Subida de encosta (hill climbing) pelo melhor vizinho.

    - Solucao inicial: as arestas do grafo passado, como estao.
    - Vizinhanca: todas as solucoes obtidas invertendo a direcao de UMA aresta.
    - Valor de uma solucao: fluxo maximo calculado com o Ford-Fulkerson.
    A cada passo vai para o melhor vizinho, se ele aumentar o fluxo; quando nenhum
    vizinho melhora (otimo local) a busca termina.

    Retorna um dicionario com fluxo inicial, fluxo final, solucao final,
    passos, avaliacoes e as arestas invertidas.
    """
    solucao = grafo.arestas()
    fluxo_inicial = avaliar(grafo, solucao, origem, destino)
    fluxo_atual = fluxo_inicial
    passos = 0
    avaliacoes = 1
    invertidas = []

    while max_passos is None or passos < max_passos:
        melhor_i, melhor_valor = None, fluxo_atual
        for i in range(len(solucao)):
            valor = avaliar(grafo, inverter(solucao, i), origem, destino)
            avaliacoes += 1
            if valor > melhor_valor + EPS:
                melhor_i, melhor_valor = i, valor

        if melhor_i is None:  # nenhum vizinho melhora: otimo local
            break

        u, v, c = solucao[melhor_i]
        solucao = inverter(solucao, melhor_i)
        fluxo_atual = melhor_valor
        passos += 1
        invertidas.append((u, v, c))
        if mostrar:
            print(f"  passo {passos}: inverte {u}->{v} (cap={c}) para {v}->{u}  =>  fluxo {fluxo_atual}")

    return {
        "fluxo_inicial": fluxo_inicial,
        "fluxo_final": fluxo_atual,
        "solucao": solucao,
        "passos": passos,
        "avaliacoes": avaliacoes,
        "invertidas": invertidas,
    }


# ---------------------------------------------------------------------------

def executar(grafo, origem, destino, mostrar_caminhos=True):
    print(grafo)
    print(f"Fonte: {origem}   Sorvedouro: {destino}")
    print()

    print("=== Ford-Fulkerson (grafo original) ===")
    caminhos = []
    fluxo, residual = ford_fulkerson(grafo, origem, destino, caminhos)
    if mostrar_caminhos:
        for n, (P, A) in enumerate(caminhos, 1):
            print(f"  caminho {n}: {' -> '.join(map(str, P))}   (A = {A})")
    else:
        print(f"  {len(caminhos)} caminhos aumentantes encontrados")
    print(f"Fluxo maximo: {fluxo}")
    if mostrar_caminhos:
        print("Fluxo em cada aresta:")
        for (u, v), f in sorted(fluxo_nas_arestas(grafo, residual).items()):
            print(f"  {u}->{v}: {f}/{grafo.peso(u, v)}")
    print()

    print("=== Busca local (inverter a direcao de uma aresta) ===")
    r = busca_local(grafo, origem, destino, mostrar=True)
    if not r["invertidas"]:
        print("  nenhuma inversao melhora o fluxo")
    print(f"Fluxo maximo da solucao original: {r['fluxo_inicial']}")
    print(f"Fluxo maximo da solucao final:    {r['fluxo_final']}")
    print(f"Numero de passos utilizados:      {r['passos']}")
    print(f"Solucoes avaliadas (Ford-Fulkerson executado): {r['avaliacoes']}")
    print()


if __name__ == "__main__":
    import sys

    uso = "uso: python fluxo.py arquivo [origem destino] [--matriz] [--resumido]"
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or flags - {"--matriz", "--resumido"} or len(args) not in (1, 3):
        sys.exit(uso)

    classe = GrafoMatriz if "--matriz" in flags else GrafoLista
    g = classe.ler_arquivo(args[0])
    if len(args) == 3:
        origem, destino = int(args[1]), int(args[2])
    else:  # padrao: primeiro vertice e a fonte, ultimo e o sorvedouro
        origem, destino = g.vertices[0], g.vertices[-1]
    if origem not in g.vertices or destino not in g.vertices:
        sys.exit(f"origem/destino devem estar entre {g.vertices[0]} e {g.vertices[-1]}")

    executar(g, origem, destino, mostrar_caminhos="--resumido" not in flags)
