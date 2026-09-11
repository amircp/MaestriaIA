# Ejercicio 1 
**Instancia elegida:** `Oradea > Bucharest` 


Se eligió **Oradea > Bucharest**. Ambas ciudades existen en el mapa y están conectadas:

En esta instancia **BFS y UCS discrepan**: existe un camino
con *menos carreteras pero más kilómetros* y otro con *más carreteras pero menos kilómetros*.

```
$ python 01_romania_map.py --from-city Oradea
  Oradea: Sibiu 151 km, Zerind 71 km

$ python 01_romania_map.py --from-city Bucharest
  Bucharest: Fagaras 211 km, Giurgiu 90 km, Pitesti 101 km, Urziceni 85 km
```

# Subgrafo relevante

```
                              (Zerind)
                                 |
                                 71
                                 |
                              Oradea
                                 |
                                151
                                 |
     Arad  ------ 140 ------- Sibiu ------- 99 ------ Fagaras
      |                          |                        \
     118                        80                        211
      |                          |                          \
  Timisoara              Rimnicu Vilcea ---- 97 ---- Pitesti --- 101 --- Bucharest
      |                          |                       |
     111                        146                     138
      |                          |                       |
    Lugoj                        +------ Craiova --------+
      |                                     |
     70                                    120
      |                                     |
   Mehadia --------- 75 --------------- Drobeta
```

## Tabla comparativa

| Algoritmo | Status | Path | Depth (roads) | Cost (km) | Expanded | Generated | Max frontier |
|---|---|---|---|---|---|---|---|
| **BFS** | success | Oradea > Sibiu > Fagaras > Bucharest | **3** | 461 | 5 | 13 | 4 |
| **UCS** | success | Oradea > Sibiu > Rimnicu Vilcea > Pitesti > Bucharest | 4 | **429** | 10 | 27 | 4 |
| **DFS** | success | Oradea > Sibiu > Arad > Timisoara > Lugoj > Mehadia > Drobeta > Craiova > Pitesti > Bucharest | 9 | 1024 | 9 | 24 | 4 |
| **DLS** `--limit 2` | **cutoff** | — | — | — | 3 | 9 | 6 |
| **DLS** `--limit 3` | success | Oradea > Sibiu > Fagaras > Bucharest | **3** | 461 | 4 | 8 | 6 |
| **DLS** `--limit 4` | success | Oradea > Sibiu > Fagaras > Bucharest | **3** | 461 | 6 | 12 | 6 |
| **IDS** | success (`last_limit=3`) | Oradea > Sibiu > Fagaras > Bucharest | **3** | 461 | 8 | 21 | 6 |

---

# Reporte

### ¿BFS encontró el camino con menos carreteras? ¿UCS el de menos km?

Sí en ambos casos, y son caminos distintos. BFS devolvió `Oradea > Sibiu > Fagaras >
Bucharest` con 3 carreteras, y ese es el mínimo posible: DLS con
`--limit 2` reportó `cutoff`, que significa que no existe un camino de 2 o menos * entre Oradea y Bucharest. UCS devolvió
`Oradea > Sibiu > Rimnicu Vilcea > Pitesti > Bucharest` con **429 km**, que es el mínimo
en kilómetros, a costa de usar 4 carreteras en lugar de 3.

BFS usa una cola **FIFO** que expande por niveles de profundidad y se detiene en cuanto alcanza la meta en el nivel 3,
sin haber mirado el nivel 4. Nunca se entera de que dar un rodeo de un salto extra
por Rimnicu Vilcea y Pitesti sale 32 km más barato. UCS, en cambio, ordena por
**costo acumulado g(n)** con una cola de prioridad, así que expande primero los nodos baratos
sin importar a qué profundidad estén; cuando finalmente saca Bucharest de la frontera, tiene
la garantía de que ningún camino pendiente puede costar menos. **BFS optimiza aristas, UCS
optimiza kilómetros, y en este mapa esas dos cosas no coinciden.**

UCS expandió **10 nodos y generó 27**, el doble que BFS (5 y 13). Es el algoritmo que más trabajo realizo, y lo hizo
para ahorrar 32 km.

### ¿Por qué DFS puede devolver un camino más largo aunque el grafo sea el mismo?

Porque DFS usa una frontera **LIFO** (pila) y no compara alternativas

### ¿Con qué `--limit` pasó DLS de cutoff a solución?

DLS reportó `cutoff` con **límites 0, 1 y 2**, y encontró solución a partir de **`--limit 3`**.


### IDS frente a BFS

IDS coincide con BFS **en todo lo que garantiza la teoría**: mismo camino
(`Oradea > Sibiu > Fagaras > Bucharest`), misma profundidad (**3 carreteras**) y mismo costo
(461 km).
---