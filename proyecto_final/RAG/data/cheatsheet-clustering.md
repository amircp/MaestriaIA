# 📘 COMPENDIO AND CHEATSHEET: CLUSTERING EN PYTHON

---

## 1️⃣ ESTANDARIZACIÓN

### ¿Cuándo estandarizar?

| Situación | ¿Estandarizar? |
|-----------|---------------|
| Variables con diferentes unidades (edad, salario, altura) | ✅ SÍ |
| Variables con misma unidad (temp1, temp2, temp3) | ❌ NO |
| Escalas muy diferentes (1-10 vs 1000-10000) | ✅ SÍ |
| Datos binarios con Jaccard/Simple Matching | ❌ NO |
| Distancia de Mahalanobis | ❌ NO necesario |

### Código:

```python
from sklearn.preprocessing import StandardScaler

# Revisar escalas
print(df.describe())

# Estandarizar (media=0, std=1)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Usar datos estandarizados
Z = linkage(X_scaled, method='ward')
```

---

## 2️⃣ DECIDIR NÚMERO DE CLUSTERS (k)

### Métodos disponibles:

### **A. Inspección visual del dendrograma**
- Busca **saltos grandes** en altura
- Corta donde hay mayor diferencia vertical

### **B. Método del Codo (Elbow Method)**

```python
from scipy.cluster.hierarchy import linkage, fcluster
import matplotlib.pyplot as plt

Z = linkage(X, method='ward')
varianzas = []

for k in range(1, 8):
    clusters = fcluster(Z, t=k, criterion='maxclust')
    varianza_total = 0
    for cluster_id in range(1, k+1):
        puntos = X[clusters == cluster_id]
        if len(puntos) > 0:
            centroide = puntos.mean(axis=0)
            varianza_total += ((puntos - centroide)**2).sum()
    varianzas.append(varianza_total)

plt.plot(range(1, 8), varianzas, 'bo-')
plt.xlabel('k')
plt.ylabel('Varianza intra-cluster')
plt.title('Método del Codo')
plt.show()
```

**Interpretación:** Elige k donde la curva hace "codo" (cambio de pendiente).

---

### **C. Coeficiente de Silueta** ⭐ (más usado)

```python
from sklearn.metrics import silhouette_score
from scipy.cluster.hierarchy import fcluster

Z = linkage(X, method='ward')

for k in range(2, 6):
    clusters = fcluster(Z, t=k, criterion='maxclust')
    score = silhouette_score(X, clusters)
    print(f'k={k}: Silueta = {score:.3f}')
```

**Interpretación:**
- **1.0**: clusters perfectos
- **0.5-0.7**: buena separación
- **< 0.3**: clusters débiles
- **Negativo**: mala asignación

**Elige el k con mayor silueta.**

---

### **D. Otros índices**

```python
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score

for k in range(2, 6):
    clusters = fcluster(Z, t=k, criterion='maxclust')
    ch = calinski_harabasz_score(X, clusters)
    db = davies_bouldin_score(X, clusters)
    print(f'k={k}: Calinski-Harabasz={ch:.2f}, Davies-Bouldin={db:.3f}')
```

- **Calinski-Harabasz**: Más alto = mejor
- **Davies-Bouldin**: Más bajo = mejor

---

## 3️⃣ CORTAR DENDROGRAMA

### **Método 1: Por distancia**

```python
from scipy.cluster.hierarchy import fcluster

# Cortar en una distancia específica
clusters = fcluster(Z, t=7, criterion='distance')

# Visualizar corte
plt.axhline(y=7, color='red', linestyle='--', label='Corte')
```

**Cuándo usar:** Conoces la distancia de corte deseada.

---

### **Método 2: Por número de clusters** ⭐ (más común)

```python
# Especificar cuántos clusters quieres
k = 3
clusters = fcluster(Z, t=k, criterion='maxclust')

# Calcular distancia de corte automáticamente
if k > 1:
    distancia_corte = (Z[-(k-1), 2] + Z[-k, 2]) / 2
else:
    distancia_corte = Z[-1, 2]

# Visualizar
plt.axhline(y=distancia_corte, color='red', linestyle='--')
```

**Cuándo usar:** Sabes cuántos clusters necesitas (más intuitivo).

---

### **Método 3: Colorear automáticamente**

```python
# Dendrograma con colores por cluster
dendrogram(Z, 
          color_threshold=distancia_corte,  # Colorea automáticamente
          above_threshold_color='gray')
```

**Resultado:** Cada cluster tiene un color diferente en el dendrograma.

---

## 4️⃣ CAMBIAR NÚMERO DE CLUSTERS Y VER DENDROGRAMA

```python
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib.pyplot as plt

# 1. Hacer clustering UNA VEZ
Z = linkage(X, method='ward')

# 2. CAMBIAR ESTE NÚMERO
k = 3  # ← Número de clusters deseado

# 3. Calcular distancia de corte
if k > 1:
    distancia_corte = (Z[-(k-1), 2] + Z[-k, 2]) / 2
else:
    distancia_corte = Z[-1, 2]

# 4. Dibujar dendrograma coloreado
plt.figure(figsize=(10, 6))
dendrogram(Z, 
          labels=labels,
          color_threshold=distancia_corte,
          above_threshold_color='gray')
plt.axhline(y=distancia_corte, color='red', linestyle='--', label=f'k={k}')
plt.title(f'Dendrograma con {k} Clusters')
plt.ylabel('Distancia')
plt.legend()
plt.show()

# 5. Asignar clusters
clusters = fcluster(Z, t=k, criterion='maxclust')
```

---

## 5️⃣ RESUMEN DE FUNCIONES CLAVE

### **CLUSTERING JERÁRQUICO**

```python
from scipy.cluster.hierarchy import linkage, dendrogram, fcluster
from scipy.spatial.distance import pdist

# ---------- DATOS NUMÉRICOS ----------
# Calcular distancias
distancias = pdist(X, metric='euclidean')  # 'manhattan', 'minkowski', etc.

# O directamente:
Z = linkage(X, method='ward', metric='euclidean')
# Métodos: 'single', 'complete', 'average', 'ward', 'centroid'

# ---------- DATOS BINARIOS ----------
# Calcular similitud Jaccard y convertir a distancia
distancias = pdist(X_binario, metric='jaccard')
Z = linkage(distancias, method='average')

# ---------- DENDROGRAMA ----------
dendrogram(Z, labels=['A', 'B', 'C'])
plt.show()

# ---------- ASIGNAR CLUSTERS ----------
# Por distancia
clusters = fcluster(Z, t=7, criterion='distance')

# Por número de clusters
clusters = fcluster(Z, t=3, criterion='maxclust')
```

---

### **K-MEANS**

```python
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

# ---------- ESTANDARIZAR (recomendado) ----------
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ---------- CLUSTERING ----------
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters = kmeans.fit_predict(X_scaled)

# ---------- RESULTADOS ----------
centroides = kmeans.cluster_centers_  # Centroides
inercia = kmeans.inertia_  # Suma de distancias al cuadrado

# ---------- MÉTODO DEL CODO ----------
inertias = []
for k in range(1, 8):
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X_scaled)
    inertias.append(km.inertia_)

plt.plot(range(1, 8), inertias, 'bo-')
plt.xlabel('k')
plt.ylabel('Inercia')
plt.title('Método del Codo - K-means')
plt.show()
```

---

### **MÉTRICAS DE DISTANCIA DISPONIBLES**

```python
from scipy.spatial.distance import pdist

# ---------- DATOS NUMÉRICOS ----------
pdist(X, metric='euclidean')    # Euclidiana (más común)
pdist(X, metric='manhattan')    # Manhattan / City Block
pdist(X, metric='minkowski', p=3)  # Minkowski (generalización)
pdist(X, metric='chebyshev')    # Chebyshev
pdist(X, metric='cosine')       # Coseno
pdist(X, metric='correlation')  # Correlación

# ---------- DATOS BINARIOS ----------
pdist(X, metric='jaccard')      # Jaccard (ignora 0-0)
pdist(X, metric='dice')         # Dice
pdist(X, metric='hamming')      # Hamming
pdist(X, metric='matching')     # Simple Matching (considera 0-0)
```

---

## 6️⃣ TIPS IMPORTANTES

### ✅ **Clustering Jerárquico**

1. **Estandariza si las variables tienen diferentes escalas**
2. **Ward es el método de enlace más usado** (minimiza varianza)
3. **Single linkage** tiende a crear "cadenas" (clusters alargados)
4. **Complete linkage** tiende a crear clusters compactos
5. **Para datos binarios:** usa Jaccard (ignora 0-0) o Simple Matching (considera 0-0)

### ✅ **K-means**

1. **SIEMPRE estandariza** antes de K-means
2. **Usa `random_state`** para reproducibilidad
3. **Usa `n_init=10`** (ejecuta 10 veces con diferentes inicializaciones)
4. K-means es **sensible a outliers**
5. Funciona mejor con **clusters esféricos**

### ✅ **General**

1. **No existe "el k correcto"** → prueba varios y evalúa
2. **Silueta > 0.5** es buena señal
3. **Interpreta los resultados** → ¿tienen sentido práctico?
4. **Visualiza siempre** tus datos antes de clustering
5. **Compara métodos** (jerárquico vs k-means) para validar

---

## 7️⃣ TEMPLATE MÍNIMO PARA TAREAS

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# ========== 1. CARGAR DATOS ==========
df = pd.read_csv('datos.csv')
X = df[['Var1', 'Var2']].values
labels = df['ID'].values

# ========== 2. ESTANDARIZAR (si es necesario) ==========
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ========== 3. CLUSTERING JERÁRQUICO ==========
Z = linkage(X_scaled, method='ward')

# Encontrar mejor k con silueta
for k in range(2, 6):
    clusters = fcluster(Z, t=k, criterion='maxclust')
    score = silhouette_score(X_scaled, clusters)
    print(f'k={k}: Silueta={score:.3f}')

# Elegir k y visualizar
k = 3
distancia_corte = (Z[-(k-1), 2] + Z[-k, 2]) / 2

plt.figure(figsize=(10, 6))
dendrogram(Z, labels=labels, color_threshold=distancia_corte)
plt.axhline(y=distancia_corte, color='red', linestyle='--')
plt.title(f'Dendrograma - {k} Clusters')
plt.show()

# ========== 4. K-MEANS ==========
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters_km = kmeans.fit_predict(X_scaled)

# Visualizar
plt.scatter(X[:, 0], X[:, 1], c=clusters_km)
plt.scatter(kmeans.cluster_centers_[:, 0], 
           kmeans.cluster_centers_[:, 1], 
           c='red', marker='X', s=200)
plt.title('K-Means')
plt.show()
```

---

## 8️⃣ DECISIONES CLAVE - CHEATSHEET

| Pregunta | Respuesta |
|----------|-----------|
| **¿Estandarizar?** | SÍ si escalas diferentes, NO si misma escala |
| **¿Qué método de enlace?** | Ward (más usado), o Complete para clusters compactos |
| **¿Jaccard o Simple Matching?** | Jaccard si 0-0 no importan, Simple Matching si sí |
| **¿Cómo elegir k?** | Silueta + inspección visual + interpretabilidad |
| **¿Jerárquico o K-means?** | Jerárquico para explorar, K-means si sabes k |
| **¿Qué distancia usar?** | Euclidiana (más común), Jaccard para binarios |

---

## 9️⃣ FLUJO COMPLETO DEL PROCESO

```
1. DATOS ORIGINALES
        ↓
2. ¿Numéricas o binarias?
        ↓
   ┌─────────┴─────────┐
   ↓                   ↓
Numéricas          Binarias
   ↓                   ↓
¿Escalas           Similitud
diferentes?        (Jaccard/Simple Matching)
   ↓                   ↓
SÍ → Estandarizar  Convertir a distancia
   ↓                   ↓
   └─────────┬─────────┘
             ↓
3. CAPACIDAD DE CALCULAR DISTANCIAS
        ↓
4. ELIGE MÉTODO DE CLUSTERING
        ↓
   ┌─────────┴─────────────┐
   ↓                       ↓
Jerárquico           No jerárquico
   ↓                       ↓
┌──┴──┐               ┌────┴────┐
↓     ↓               ↓         ↓
Aglom Divis       K-means    DBSCAN
   ↓                   ↓
Método de enlace   Elegir k
(single, complete, Método del codo
average, ward)     o Silueta
   ↓                   ↓
Dendrograma        Visualizar
   ↓                   ↓
Elegir k           Evaluar
   ↓                   ↓
Asignar clusters   Resultados
```

---

## 🔟 MEDIDAS DE SIMILITUD PARA DATOS BINARIOS

### **Coeficiente de Jaccard** (el más usado)

**Fórmula:** `s = a / (a + b + c)`

- **a**: coincidencias 1-1
- **b**: discrepancias (0-1)
- **c**: discrepancias (1-0)
- **Ignora d** (coincidencias 0-0)

**Cuándo usar:** Especies en sitios, productos comprados, palabras en documentos (cuando NO tener algo en común NO significa similitud)

```python
distancias = pdist(X_binario, metric='jaccard')
```

---

### **Simple Matching**

**Fórmula:** `s = (a + d) / p`

- **Considera d** (coincidencias 0-0)

**Cuándo usar:** Síntomas médicos, características de casa, test binarios (cuando ausencias compartidas SÍ son informativas)

```python
def simple_matching_distance(u, v):
    coincidencias = np.sum(u == v)
    similitud = coincidencias / len(u)
    return 1 - similitud

distancias = pdist(X_binario, metric=simple_matching_distance)
```

---

### **Tabla de contingencia**

Cuando comparas dos objetos i y k:

```
           Objeto k
        1     0    Total
i   1   a     b    a+b
    0   c     d    c+d
Total  a+c   b+d    p
```

**Conversión de similitud a distancia:**

```python
d = sqrt(2 * (1 - s))
```

---

## 1️⃣1️⃣ EJEMPLO COMPLETO PASO A PASO

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

# ========== DATOS ==========
datos = {
    'ID': ['A', 'B', 'C', 'D', 'E'],
    'Edad': [25, 27, 45, 50, 52],
    'Salario': [30000, 32000, 60000, 65000, 70000]
}
df = pd.DataFrame(datos)
print(df.describe())  # Verificar escalas

# ========== PREPARAR ==========
X = df[['Edad', 'Salario']].values
labels = df['ID'].values

# Estandarizar (escalas muy diferentes)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# ========== CLUSTERING ==========
Z = linkage(X_scaled, method='ward')

# ========== ELEGIR k CON SILUETA ==========
print("\nCoeficientes de Silueta:")
for k in range(2, 5):
    clusters = fcluster(Z, t=k, criterion='maxclust')
    score = silhouette_score(X_scaled, clusters)
    print(f'k={k}: {score:.3f}')

# ========== VISUALIZAR CON k=2 ==========
k = 2
distancia_corte = (Z[-(k-1), 2] + Z[-k, 2]) / 2

plt.figure(figsize=(10, 6))
dendrogram(Z, 
          labels=labels,
          color_threshold=distancia_corte,
          above_threshold_color='gray')
plt.axhline(y=distancia_corte, color='red', linestyle='--', linewidth=2)
plt.title(f'Dendrograma - {k} Clusters (Ward)')
plt.ylabel('Distancia')
plt.show()

# ========== ASIGNAR Y MOSTRAR ==========
clusters = fcluster(Z, t=k, criterion='maxclust')
df['Cluster'] = clusters
print("\nAsignación de clusters:")
print(df)
```

---

## 1️⃣2️⃣ VALIDACIÓN DE CLUSTERS ⭐

### **¿Por qué validar?**

La validación asegura que tus clusters sean:
- ✅ **Representativos**: reflejan estructura real en los datos
- ✅ **Generalizables**: no son resultado de ruido o azar
- ✅ **Estables**: se mantienen con pequeños cambios en datos/parámetros
- ✅ **Robustos**: no dependen excesivamente de una variable específica

---

### **Método 1: Diferentes Medidas de Distancia**

Prueba múltiples métricas y compara resultados.

```python
from scipy.cluster.hierarchy import linkage, fcluster
from sklearn.metrics import adjusted_rand_score
from scipy.spatial.distance import pdist

# Clustering con diferentes distancias
metricas = ['euclidean', 'manhattan', 'cosine']
resultados = {}

for metrica in metricas:
    distancias = pdist(X_scaled, metric=metrica)
    Z = linkage(distancias, method='ward')
    clusters = fcluster(Z, t=3, criterion='maxclust')
    resultados[metrica] = clusters

# Comparar con Adjusted Rand Index (ARI)
print("Comparación de métricas de distancia:")
for i, metrica1 in enumerate(metricas):
    for metrica2 in metricas[i+1:]:
        ari = adjusted_rand_score(resultados[metrica1], resultados[metrica2])
        print(f'{metrica1} vs {metrica2}: ARI = {ari:.3f}')
```

**Interpretación:**
- **ARI > 0.7**: clusters estables entre métricas ✅
- **ARI < 0.5**: resultados inconsistentes, revisar datos ⚠️

---

### **Método 2: Diferentes Métodos de Clustering**

Compara jerárquico (varios enlaces) vs K-means.

```python
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score

# 1. Clustering jerárquico con diferentes métodos
metodos = ['ward', 'complete', 'average', 'single']
resultados_jerarquico = {}

for metodo in metodos:
    Z = linkage(X_scaled, method=metodo)
    clusters = fcluster(Z, t=3, criterion='maxclust')
    resultados_jerarquico[metodo] = clusters
    sil = silhouette_score(X_scaled, clusters)
    print(f'{metodo}: Silueta = {sil:.3f}')

# 2. K-means
kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
clusters_kmeans = kmeans.fit_predict(X_scaled)
sil_kmeans = silhouette_score(X_scaled, clusters_kmeans)
print(f'K-means: Silueta = {sil_kmeans:.3f}')

# 3. Comparar todos vs todos
print("\nComparación entre métodos:")
for metodo in metodos:
    ari = adjusted_rand_score(resultados_jerarquico[metodo], clusters_kmeans)
    print(f'{metodo} vs K-means: ARI = {ari:.3f}')
```

**Interpretación:**
- Si todos los métodos dan **resultados similares** → alta confianza ✅
- Si resultados **muy diferentes** → estructura débil o datos complejos ⚠️

---

### **Método 3: Split-Half (Dividir Datos)**

Divide datos aleatoriamente y verifica consistencia.

```python
from sklearn.model_selection import train_test_split
from sklearn.metrics import adjusted_rand_score, silhouette_score

# Dividir datos en dos mitades aleatorias
X_1, X_2 = train_test_split(X_scaled, test_size=0.5, random_state=42)

# Clustering en cada mitad
Z_1 = linkage(X_1, method='ward')
Z_2 = linkage(X_2, method='ward')

clusters_1 = fcluster(Z_1, t=3, criterion='maxclust')
clusters_2 = fcluster(Z_2, t=3, criterion='maxclust')

# Comparar siluetas
sil_1 = silhouette_score(X_1, clusters_1)
sil_2 = silhouette_score(X_2, clusters_2)

print(f'Mitad 1: Silueta = {sil_1:.3f}')
print(f'Mitad 2: Silueta = {sil_2:.3f}')
print(f'Diferencia: {abs(sil_1 - sil_2):.3f}')
```

**Interpretación:**
- **Diferencia < 0.2**: clusters estables ✅
- **Diferencia > 0.3**: clusters inestables, dependen de muestra específica ⚠️

---

### **Método 4: Eliminar Variables Aleatoriamente**

Verifica que clusters no dependan de una sola variable.

```python
import numpy as np
from sklearn.metrics import adjusted_rand_score

# Clustering con TODAS las variables
Z_completo = linkage(X_scaled, method='ward')
clusters_completo = fcluster(Z_completo, t=3, criterion='maxclust')

# Clustering eliminando una variable aleatoria
n_vars = X_scaled.shape[1]
for i in range(n_vars):
    # Eliminar variable i
    X_sin_i = np.delete(X_scaled, i, axis=1)
    
    Z_parcial = linkage(X_sin_i, method='ward')
    clusters_parcial = fcluster(Z_parcial, t=3, criterion='maxclust')
    
    # Comparar
    ari = adjusted_rand_score(clusters_completo, clusters_parcial)
    print(f'Sin variable {i}: ARI = {ari:.3f}')
```

**Interpretación:**
- **ARI > 0.7** al eliminar cualquier variable → clusters robustos ✅
- **ARI < 0.5** al eliminar una variable → clusters dependen de esa variable ⚠️

---

### **Método 5: Múltiples Ejecuciones (K-means)**

K-means puede dar resultados diferentes por inicialización aleatoria.

```python
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
import numpy as np

# Ejecutar K-means 10 veces con diferentes random_state
resultados = []
for i in range(10):
    kmeans = KMeans(n_clusters=3, random_state=i, n_init=10)
    clusters = kmeans.fit_predict(X_scaled)
    resultados.append(clusters)

# Comparar todas las ejecuciones
aris = []
for i in range(len(resultados)):
    for j in range(i+1, len(resultados)):
        ari = adjusted_rand_score(resultados[i], resultados[j])
        aris.append(ari)

ari_promedio = np.mean(aris)
ari_min = np.min(aris)

print(f'ARI promedio entre ejecuciones: {ari_promedio:.3f}')
print(f'ARI mínimo: {ari_min:.3f}')
```

**Interpretación:**
- **ARI promedio > 0.9**: K-means muy estable ✅
- **ARI promedio < 0.7**: resultados inconsistentes, probar más n_init ⚠️

**Nota:** Por eso se recomienda `n_init=10` en K-means (ejecuta 10 veces automáticamente).

---

### **📋 CHECKLIST DE VALIDACIÓN**

Antes de reportar resultados, verifica:

- [ ] ✅ **Similar con diferentes distancias** (ARI > 0.7)
- [ ] ✅ **Similar con diferentes métodos** (jerárquico vs K-means)
- [ ] ✅ **Similar al dividir datos** (diferencia silueta < 0.2)
- [ ] ✅ **Robusto al eliminar variables** (ARI > 0.7)
- [ ] ✅ **Estable en múltiples ejecuciones** (K-means ARI > 0.9)
- [ ] ✅ **Silueta > 0.5** (buena separación)
- [ ] ✅ **Interpretable y con sentido práctico**

---

### **🎯 CÓDIGO COMPLETO DE VALIDACIÓN**

```python
import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import linkage, fcluster
from scipy.spatial.distance import pdist
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.model_selection import train_test_split

# ========== PREPARAR DATOS ==========
df = pd.read_csv('datos.csv')
X = df[['Var1', 'Var2', 'Var3']].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

k = 3  # Número de clusters

# ========== 1. VALIDACIÓN: DIFERENTES DISTANCIAS ==========
print("=== VALIDACIÓN 1: Diferentes Distancias ===")
metricas = ['euclidean', 'manhattan', 'cosine']
resultados_dist = {}

for metrica in metricas:
    distancias = pdist(X_scaled, metric=metrica)
    Z = linkage(distancias, method='ward')
    clusters = fcluster(Z, t=k, criterion='maxclust')
    resultados_dist[metrica] = clusters
    sil = silhouette_score(X_scaled, clusters)
    print(f'{metrica}: Silueta = {sil:.3f}')

# Comparar métricas
ari_dist = adjusted_rand_score(resultados_dist['euclidean'], 
                                 resultados_dist['manhattan'])
print(f'ARI (euclidean vs manhattan): {ari_dist:.3f}')

# ========== 2. VALIDACIÓN: DIFERENTES MÉTODOS ==========
print("\n=== VALIDACIÓN 2: Diferentes Métodos ===")
Z_ward = linkage(X_scaled, method='ward')
clusters_ward = fcluster(Z_ward, t=k, criterion='maxclust')

kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
clusters_kmeans = kmeans.fit_predict(X_scaled)

ari_metodos = adjusted_rand_score(clusters_ward, clusters_kmeans)
print(f'ARI (Ward vs K-means): {ari_metodos:.3f}')

# ========== 3. VALIDACIÓN: SPLIT-HALF ==========
print("\n=== VALIDACIÓN 3: Split-Half ===")
X_1, X_2 = train_test_split(X_scaled, test_size=0.5, random_state=42)

Z_1 = linkage(X_1, method='ward')
clusters_1 = fcluster(Z_1, t=k, criterion='maxclust')
sil_1 = silhouette_score(X_1, clusters_1)

Z_2 = linkage(X_2, method='ward')
clusters_2 = fcluster(Z_2, t=k, criterion='maxclust')
sil_2 = silhouette_score(X_2, clusters_2)

print(f'Silueta Mitad 1: {sil_1:.3f}')
print(f'Silueta Mitad 2: {sil_2:.3f}')
print(f'Diferencia: {abs(sil_1 - sil_2):.3f}')

# ========== 4. VALIDACIÓN: ELIMINAR VARIABLES ==========
print("\n=== VALIDACIÓN 4: Robustez Variables ===")
Z_completo = linkage(X_scaled, method='ward')
clusters_completo = fcluster(Z_completo, t=k, criterion='maxclust')

for i in range(X_scaled.shape[1]):
    X_sin_i = np.delete(X_scaled, i, axis=1)
    Z_parcial = linkage(X_sin_i, method='ward')
    clusters_parcial = fcluster(Z_parcial, t=k, criterion='maxclust')
    ari = adjusted_rand_score(clusters_completo, clusters_parcial)
    print(f'Sin variable {i}: ARI = {ari:.3f}')

# ========== 5. VALIDACIÓN: MÚLTIPLES EJECUCIONES K-MEANS ==========
print("\n=== VALIDACIÓN 5: Estabilidad K-means ===")
resultados_km = []
for i in range(10):
    km = KMeans(n_clusters=k, random_state=i, n_init=10)
    clusters = km.fit_predict(X_scaled)
    resultados_km.append(clusters)

aris_km = []
for i in range(len(resultados_km)):
    for j in range(i+1, len(resultados_km)):
        ari = adjusted_rand_score(resultados_km[i], resultados_km[j])
        aris_km.append(ari)

print(f'ARI promedio: {np.mean(aris_km):.3f}')
print(f'ARI mínimo: {np.min(aris_km):.3f}')

# ========== RESUMEN DE VALIDACIÓN ==========
print("\n" + "="*50)
print("RESUMEN DE VALIDACIÓN")
print("="*50)
print(f"✓ Diferentes distancias: ARI = {ari_dist:.3f}")
print(f"✓ Diferentes métodos: ARI = {ari_metodos:.3f}")
print(f"✓ Split-half: Diferencia = {abs(sil_1 - sil_2):.3f}")
print(f"✓ K-means estabilidad: ARI promedio = {np.mean(aris_km):.3f}")
print(f"✓ Silueta final: {silhouette_score(X_scaled, clusters_ward):.3f}")
```

---

### **🔑 CRITERIOS DE DECISIÓN**

| Métrica | Valor | Interpretación |
|---------|-------|----------------|
| **ARI entre métodos** | > 0.7 | ✅ Clusters estables |
|  | 0.5 - 0.7 | ⚠️ Estructura moderada |
|  | < 0.5 | ❌ Resultados inconsistentes |
| **Diferencia Silueta** | < 0.2 | ✅ Clusters robustos |
| (Split-half) | 0.2 - 0.3 | ⚠️ Moderadamente estables |
|  | > 0.3 | ❌ Muy inestables |
| **Silueta absoluta** | > 0.7 | ✅ Excelente separación |
|  | 0.5 - 0.7 | ✅ Buena separación |
|  | 0.3 - 0.5 | ⚠️ Estructura débil |
|  | < 0.3 | ❌ Clusters poco claros |

---

**FIN DEL COMPENDIO** 📘

---

**Autor:** Claude (Anthropic)  
**Fecha:** Noviembre 2025  
**Tema:** Análisis de Conglomerados en Python  
**Librerías:** scipy, scikit-learn, pandas, numpy, matplotlib
