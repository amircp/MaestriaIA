# Ejercicio 1 — Comparar Greedy y A* en el mapa de Rumania

**Instancia elegida:** `Timisoara → Bucharest` (distinta de la pareja por defecto `Arad → Bucharest`)

## 1. Instancia elegida y justificación

Se eligió **Timisoara > Bucharest**. Ambas ciudades existen en el mapa y están conectadas.

## 2. Heurística `h(n)` hacia Bucharest

Salida de `02_heuristics.py` para el destino elegido :

```
$ python 02_heuristics.py --from-city Timisoara --to Bucharest
Heuristic: straight-line distance to Bucharest (AIMA table)

  h(n)  city
      0  Bucharest  <- goal
     77  Giurgiu
     80  Urziceni
    100  Pitesti
    151  Hirsova
    160  Craiova
    161  Eforie
    176  Fagaras
    193  Rimnicu Vilcea
    199  Vaslui
    226  Iasi
    234  Neamt
    241  Mehadia
    242  Drobeta
    244  Lugoj
    253  Sibiu
    329  Timisoara  <- start
    366  Arad
    374  Zerind
    380  Oradea
```

| Vecino de Timisoara | Tramo (km) | `h(n)` | `g(n)` | `f(n) = g + h` | Costo real por carretera a Bucharest |
|---|---|---|---|---|---|
| **Lugoj** | 111 | **244** (menor) | 111 | **355** (menor) | 504 km (70+75+120+138+101) |
| **Arad** | 118 | 366 | 118 | 484 | 418 km (140+80+97+101) |

## Grafo


```
        Arad ---------- 140 ---------- Sibiu -------- 99 -------- (Fagaras)
       h=366                           h=253                        h=176
         |                               |                             \
        118                              80                            211
         |                               |                               \
     Timisoara                    Rimnicu Vilcea ----- 97 ----- Pitesti --- 101 --- Bucharest
       h=329                           h=193  \                  h=100                h=0
      ORIGEN                                   \                   |               DESTINO
         |                                     146                138
        111                                      \                 |
         |                                        \                |
       Lugoj --- 70 --- Mehadia --- 75 --- Drobeta --- 120 --- Craiova
       h=244             h=241              h=242               h=160

  Greedy : Timisoara → Lugoj → Mehadia → Drobeta → Craiova → Pitesti → Bucharest   (fila inferior)
  A*     : Timisoara → Arad  → Sibiu   → Rimnicu Vilcea → Pitesti → Bucharest       (fila superior)
```


---

## Tabla comparativa

| Algoritmo | Heurística | Status | Path | Depth (roads) | Cost (km) | Expanded | Generated | Max frontier |
|---|---|---|---|---|---|---|---|---|
| **Greedy best-first** | SLD a Bucharest (tabla AIMA) | success | Timisoara → Lugoj → Mehadia → Drobeta → Craiova → Pitesti → Bucharest | 6 | 615 | **6** | 15 | 3 |
| **A\*** | SLD a Bucharest (tabla AIMA) | success | Timisoara → Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest | **5** | **536** | 10 | 27 | 5 |
| UCS (verificación cruzada, proyecto de búsqueda no informada) | ninguna | success | Timisoara → Arad → Sibiu → Rimnicu Vilcea → Pitesti → Bucharest | 5 | 536 | 12 | 31 | 4 |

### `g / h / f` a lo largo de cada camino

**Greedy** (615 km):

| city | g | h | f |
|---|---|---|---|
| Timisoara | 0 | 329 | 329 |
| Lugoj | 111 | 244 | 355 |
| Mehadia | 181 | 241 | 422 |
| Drobeta | 256 | 242 | 498 |
| Craiova | 376 | 160 | 536 |
| Pitesti | 514 | 100 | 614 |
| Bucharest | 615 | 0 | 615 |

**A\*** (536 km):

| city | g | h | f |
|---|---|---|---|
| Timisoara | 0 | 329 | 329 |
| Arad | 118 | 366 | 484 |
| Sibiu | 258 | 253 | 511 |
| Rimnicu Vilcea | 338 | 193 | 531 |
| Pitesti | 435 | 100 | 535 |
| Bucharest | 536 | 0 | 536 |

---

# Reporte

### ¿A\* encontró el camino de menos km? ¿Greedy coincidió o se desvió?

**A\* sí encontró el óptimo y Greedy se desvió.** A\* devolvió `Timisoara > Arad  > Sibiu > Rimnicu
Vilcea > Pitesti > Bucharest` con **536 km y 5 carreteras**. es el mínimo en km y lo confirma
una ejecucion independiente de UCS sobre la misma pareja:
mismo camino, mismos 536 km. Greedy devolvió un camino distinto, `Timisoara > Lugoj > Mehadia > Drobeta > Craiova > Pitesti > Bucharest`, 
con **615 km y 6 carreteras**: 79 km más y una carretera más.

### ¿Por qué Greedy puede devolver un camino más caro aunque `h` sea admisible?

Porque **admisible es una propiedad de `h` respecto al costo real restante, no una garantía sobre el
algoritmo que la use**. Admisible significa `h(n) ≤ h*(n)`: nunca sobreestima lo que falta. Esa
propiedad es la que hace a A\* óptimo, y lo hace *solo* porque A\* combina `h` con `g`: entonces
`f(n) = g(n) + h(n)` es una **cota inferior** del costo de cualquier solución que pase por `n`, y A\*
no saca la meta de la frontera mientras quede una cota inferior más pequeña pendiente.

Greedy tira esa cota a la basura al ignorar `g`. Compara valores de `h` que subestiman en distinta
medida y se fía del que subestima más. En esta instancia:

| Ciudad | `h(n)` | Costo real restante `h*(n)` | Error de la subestimación |
|---|---|---|---|
| Lugoj | 244 | 504 | **260 km** |
| Craiova | 160 | 239 | 79 km |
| Arad | 366 | 418 | 52 km |


### En el camino de A\*, ¿`f` tiende a no disminuir? Relación con la consistencia

**Sí: `f` es creciente a lo largo de todo el camino de A\*:** 329 >> 484 >> 511 >> 531 >> 535 >> 536.

---