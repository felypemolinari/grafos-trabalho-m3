# Trabalho M3.1 - Fluxo Maximo

Implementacao do algoritmo de fluxo maximo de **Ford-Fulkerson** e de uma **busca local**
que tenta aumentar o fluxo maximo invertendo a direcao das arestas.
A base (classes `GrafoLista` / `GrafoMatriz` e leitura de arquivo) vem do trabalho da M2.

## Arquivos

- `grafo.py` – base da M2 (lista e matriz de adjacencia, BFS, DFS, Dijkstra) com os acrescimos:
  - `peso`, `definir_peso`, `remover_aresta`, `somar_peso`, `arestas`;
  - `copiar()` – copia **independente** do grafo (lista/matriz novas, sem compartilhar referencias);
  - `caminho_busca_em_profundidade(grafo, s, t)` – a DFS da M1 guardando o pai de cada vertice
    para devolver o caminho; **ignora arestas com peso 0**.
- `fluxo.py` – Ford-Fulkerson, busca local e programa principal.
- `teste.py` – testes automaticos.
- `grafos_fluxo/` – instancias de teste.

## Ford-Fulkerson (pseudocodigo dos slides)

```
residual = copia do grafo original
S = 0
enquanto existir caminho P (DFS) de capacidade positiva da fonte ao sorvedouro:
    A = menor arco de P ;  S += A
    para cada arco (u,v) de P:
        subtrai A de (u,v)            -> se ficar 0 o arco e apagado
        se existe (v,u): soma A em (v,u)
        senao: cria (v,u) com valor A
```

## Busca local

- **Solucao inicial:** a estrutura do grafo lido.
- **Solucao vizinha:** a mesma estrutura com a direcao de **uma** aresta invertida
  (se ja existir o arco contrario, as capacidades sao somadas).
- **Avaliacao:** fluxo maximo calculado pelo Ford-Fulkerson.
- **Estrategia:** subida de encosta pelo melhor vizinho: a cada passo avalia todos os vizinhos e vai
  para o de maior fluxo; para quando nenhum vizinho melhora (otimo local).
- Ao final imprime o fluxo maximo da solucao original, o da solucao final e o numero de passos
  (e tambem quantas solucoes foram avaliadas).

## Formato do arquivo

Mesmo da M2: cabecalho `V A D P` (vertices, arestas, direcionado, ponderado) e uma aresta por
linha `origem destino capacidade`. Os vertices podem comecar em 0 ou 1.

## Como executar

```
python fluxo.py arquivo [origem destino] [--matriz] [--resumido]
```

- Sem `origem destino`: a fonte e o primeiro vertice e o sorvedouro e o ultimo.
- `--matriz`: usa matriz de adjacencia (padrao: lista).
- `--resumido`: nao imprime os caminhos aumentantes nem o fluxo em cada aresta.

Exemplos:

```
python fluxo.py grafos_fluxo/classico_6.txt          # fluxo 23 -> 24 em 1 passo
python fluxo.py grafos_fluxo/inverter_8.txt 1 8      # fluxo 8 -> 13 em 2 passos
python fluxo.py grafos_fluxo/aleatorio_100.txt --resumido
python teste.py
```

`teste.py` compara o Ford-Fulkerson com uma implementacao independente (Edmonds-Karp) em
centenas de grafos aleatorios, nas duas representacoes, confere que o grafo original nao e
alterado e que a busca local termina num otimo local sem passar do otimo global (forca bruta).
