class Grafo:
    def __init__(self, num_vertices, direcionado=False, ponderado=False, base=0):
        self.num_vertices = num_vertices
        self.direcionado = direcionado
        self.ponderado = ponderado
        self.base = base
        self.vertices = list(range(base, base + num_vertices))

    def adicionar_aresta(self, origem, destino, peso=1):
        self._inserir(origem, destino, peso)
        if not self.direcionado:
            self._inserir(destino, origem, peso)

    def _inserir(self, origem, destino, peso):
        raise NotImplementedError

    def vizinhos(self, v):
        raise NotImplementedError

    def peso(self, origem, destino):
        """Peso (capacidade) da aresta origem->destino, ou None se nao existir."""
        raise NotImplementedError

    def definir_peso(self, origem, destino, peso):
        """Altera o peso da aresta origem->destino (cria a aresta se nao existir)."""
        raise NotImplementedError

    def remover_aresta(self, origem, destino):
        raise NotImplementedError

    def somar_peso(self, origem, destino, valor):
        """Se a aresta origem->destino existe soma 'valor' ao peso, senao cria com esse valor."""
        atual = self.peso(origem, destino)
        if atual is None:
            self._inserir(origem, destino, valor)
        else:
            self.definir_peso(origem, destino, atual + valor)

    def arestas(self):
        """Lista de arestas (origem, destino, peso), como estao armazenadas."""
        return [(u, v, p) for u in self.vertices for v, p in self.vizinhos(u)]

    def copiar(self):
        """Copia independente do grafo: nenhuma lista/matriz e compartilhada com o original,
        entao alterar a copia nao altera o original. Arestas paralelas sao somadas."""
        novo = type(self)(self.num_vertices, self.direcionado, self.ponderado, self.base)
        for u, v, p in self.arestas():
            novo.somar_peso(u, v, p)
        return novo

    @classmethod
    def ler_arquivo(cls, caminho):
        with open(caminho, "r", encoding="utf-8") as f:
            linhas = [l.split() for l in f if l.strip()]
        if not linhas or len(linhas[0]) < 4:
            raise ValueError("Cabecalho invalido, esperado 'V A D P'")

        num_vertices, num_arestas, direcionado, ponderado = (int(x) for x in linhas[0][:4])
        corpo = linhas[1:]
        if len(corpo) < num_arestas:
            raise ValueError(f"Esperadas {num_arestas} arestas, encontradas {len(corpo)}")
        corpo = corpo[:num_arestas]

        ids = [int(p[i]) for p in corpo for i in (0, 1)]
        base = 1 if ids and min(ids) >= 1 and max(ids) >= num_vertices else 0

        g = cls(num_vertices, direcionado == 1, ponderado == 1, base)
        for partes in corpo:
            if ponderado and len(partes) < 3:
                raise ValueError(f"Aresta sem peso: {' '.join(partes)}")
            peso = float(partes[2]) if ponderado else 1
            if isinstance(peso, float) and peso.is_integer():
                peso = int(peso)
            g.adicionar_aresta(int(partes[0]), int(partes[1]), peso)
        return g

    def cabecalho(self):
        tipo = "direcionado" if self.direcionado else "nao direcionado"
        tipo += ", ponderado" if self.ponderado else ", nao ponderado"
        return f"{type(self).__name__} ({tipo}) com {self.num_vertices} vertices"

    def __str__(self):
        linhas = [self.cabecalho()]
        for v in self.vertices:
            if self.ponderado:
                viz = ", ".join(f"{d}(p={p})" for d, p in self.vizinhos(v))
            else:
                viz = ", ".join(str(d) for d, _ in self.vizinhos(v))
            linhas.append(f"  {v} -> [{viz}]")
        return "\n".join(linhas)


class GrafoLista(Grafo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.adj = {v: [] for v in self.vertices}

    def _inserir(self, origem, destino, peso):
        self.adj[origem].append((destino, peso))

    def vizinhos(self, v):
        return sorted(self.adj[v])

    def peso(self, origem, destino):
        for d, p in self.adj[origem]:
            if d == destino:
                return p
        return None

    def definir_peso(self, origem, destino, peso):
        lista = self.adj[origem]
        for i, (d, _) in enumerate(lista):
            if d == destino:
                lista[i] = (destino, peso)
                return
        lista.append((destino, peso))

    def remover_aresta(self, origem, destino):
        self.adj[origem] = [(d, p) for d, p in self.adj[origem] if d != destino]


class GrafoMatriz(Grafo):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        n = self.num_vertices
        self.mat = [[None] * n for _ in range(n)]

    def _inserir(self, origem, destino, peso):
        self.mat[origem - self.base][destino - self.base] = peso

    def vizinhos(self, v):
        linha = self.mat[v - self.base]
        return [(j + self.base, p) for j, p in enumerate(linha) if p is not None]

    def peso(self, origem, destino):
        return self.mat[origem - self.base][destino - self.base]

    def definir_peso(self, origem, destino, peso):
        self.mat[origem - self.base][destino - self.base] = peso

    def remover_aresta(self, origem, destino):
        self.mat[origem - self.base][destino - self.base] = None

def caminho_busca_em_profundidade(grafo, inicio, fim):
    """Mesma busca em profundidade da M1, mas guardando o pai de cada vertice para
    reconstruir o caminho inicio->fim. Arestas com peso <= 0 sao ignoradas.
    Retorna a lista de vertices do caminho, ou None se 'fim' nao for alcancavel."""
    pai = {}
    pilha = [(inicio, None)]
    while pilha:
        atual, anterior = pilha.pop()
        if atual in pai:
            continue
        pai[atual] = anterior
        if atual == fim:
            caminho = [fim]
            while pai[caminho[-1]] is not None:
                caminho.append(pai[caminho[-1]])
            return caminho[::-1]
        for vizinho, peso in reversed(grafo.vizinhos(atual)):
            if peso > 0 and vizinho not in pai:
                pilha.append((vizinho, atual))
    return None
