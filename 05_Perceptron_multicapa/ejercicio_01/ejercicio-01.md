# Ejercicio 1 — Más capas en el perceptrón multicapa (Iris)

**Configuración común a las cuatro corridas:** activación sigmoide en todas las capas,
error MSE, SGD con η = 0.03, 500 épocas, 150 ejemplos de Iris (4 atributos, 3 clases one-hot).

## 1. Resultados de las cuatro corridas

| Corrida | Topología | Parámetros | Error/loss inicial | Error/loss final (época 500) | Tiempo celda de entrenamiento |
|---|---|---|---|---|---|
| NumPy original | 4×3×3 | 27 | 0.8155 | 0.0584 | 8.1 s |
| NumPy profunda | 4×3×3×3×3 | 51 | 0.7326 | 0.3471 (plana en 0.670 hasta ≈ época 360) | 19.1 s |
| Keras original | 4×3×3 | 27 | 0.233 | ≈ 0.128 (todavía bajando) | no medido |
| Keras profunda | 4×3×3×3×3 | 51 | 0.3248 | 0.2222 (plana desde ≈ época 225) | no medido |

Error cada 50 épocas (tomado de las salidas de las notebooks):

| Época | NumPy 4×3×3 | NumPy 4×3×3×3×3 | Keras 4×3×3×3×3 |
|---|---|---|---|
| 0 / 1 | 0.8155 | 0.7326 | 0.3248 |
| 50 | 0.3525 | 0.6704 | 0.2504 |
| 100 | 0.2033 | 0.6703 | 0.2292 |
| 150 | 0.1351 | 0.6701 | 0.2242 |
| 200 | 0.1036 | 0.6699 | 0.2228 |
| 250 | 0.0864 | 0.6692 | 0.2224 |
| 300 | 0.0760 | 0.6672 | 0.2223 |
| 350 | 0.0691 | 0.6533 | 0.2223 |
| 400 | 0.0643 | 0.4068 | 0.2222 |
| 450 | 0.0609 | 0.3503 | 0.2222 |
| 500 | 0.0584 | 0.3471 | 0.2222 |

Predicción de ejemplo con la entrada [3, 3, 1, 1] en la red profunda de Keras:
[0.5627, 0.3358, 0.2984]. Gana la clase 0 (setosa), pero con poca separación entre las
tres salidas, coherente con una red que apenas se movió de [1/3, 1/3, 1/3].

Si la red responde ≈ [1/3, 1/3, 1/3] para cualquier entrada (es decir, no aprendió nada y solo reproduce la frecuencia de cada clase), el MSE contra un one-hot
vale ((2/3)^2 + 2x(1/3)^2) / 3 = 2/9 = 0.2222 Las 500 épocas solo ajustó el bias de la salida y las capas ocultas no aprendieron.
En NumPy la misma meseta aparece en 0.670 (= 3 x 0.223).

## 2. ¿Bajó más el error al añadir dos capas, o se estancó / empeoró?

**Empeoró en las dos implementaciones, pero diferente.**

- **Keras:** la red original bajó de 0.233 a ≈ 0.128 y a la época 500 la curva *todavía iba
  bajando*. La red profunda bajó de 0.3248 a 0.2225 en las primeras ≈ 225 épocas y de ahí a la
  época 500 solo se movió en la cuarta cifra decimal. No es que aprenda más lento: se estancó en
  la solución trivial de "predecir 1/3 para todo".
- **NumPy:** la red original bajó de 0.8155 a 0.0584, con una pequeña meseta alrededor de 0.35
  cerca de la época 50 y luego una bajada limpia; a la época 300 ya estaba por debajo de 0.08. La
  red profunda cayó de 0.7326 a 0.670 en las primeras épocas y se quedó **plana ahí unas 350
  épocas** (0.6704 en la época 50, 0.6672 en la 300). Alrededor de la época 360 despegó, cayó a
  0.4068 en la época 400 y terminó en 0.3471: **seis veces peor** que la original con el mismo
  presupuesto de épocas.
- **Depende de la inicialización.** En corridas repetidas de la notebook 04 la meseta aparece
  siempre en el mismo valor (≈ 0.667–0.670), pero la época en que la red despega cambia con los
  pesos iniciales: en unas corridas fue cerca de la época 220, en esta de Colab cerca de la 360, y
  en otras no despegó en las 500 épocas. En ninguna la red profunda superó a la original.

Conclusión: con estos hiperparámetros, más capas **no** bajaron el error; en Keras se estancó y en
NumPy necesitó más de 350 épocas solo para salir de la meseta.

## 3. ¿Se parecen las curvas de NumPy y de Keras con la misma topología?

**No.** Con 4x3x3, NumPy llega a un error equivalente de aprox 0.019 y Keras a 0.128, la curva de
NumPy es una "L" que ya se aplanó a la época 300, mientras que la de Keras es una bajada suave que
no termina de converger. Con 4x3x3x3x3 ambas caen en la misma meseta, pero NumPy alcanza a salir
de ella y Keras no. 

## 4. ¿Tiene sentido que una red más profunda no aprenda mejor en Iris?

Sí, por dos razones que se ven directamente en las gráficas.

**a) Gradiente que se desvanece.** En backprop, δ de una capa oculta es
h(1−h) ⊙ (Wᵀ δ de la capa siguiente). El factor h(1−h) de la sigmoide vale como máximo 0.25 (y
mucho menos si la neurona satura), y los pesos iniciales tienen magnitud ≈ 0.5. Cada capa
adicional multiplica el gradiente por algo del orden de 0.25 × 0.5; con tres capas ocultas, el
gradiente que llega a `layer1` es cientos de veces más chico que el de la salida. Con η = 0.03 las
primeras capas casi no se mueven. Además, con MSE + sigmoide en la salida, el δ de salida es
o(1−o)(y−o): cuando una salida satura cerca de 0 o 1 aunque esté equivocada, su gradiente también
se apaga. 
**b) Iris no necesita profundidad.** Setosa es linealmente separable de las otras dos y versicolor
y virginica casi lo son; un 4x3x3 ya baja el error a 0.058 y clasifica bien casi todos los
ejemplos. Las dos capas extra no agregan capacidad útil.

