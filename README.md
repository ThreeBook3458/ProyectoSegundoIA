## Sistema Logístico de Búsqueda Inteligente y Toma de Decisiones Adversarias

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.28%2B-red.svg)](https://streamlit.io/)
[![Jupyter Notebook](https://img.shields.io/badge/Jupyter-Notebook-orange.svg)](https://jupyter.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## Descripción General

Este proyecto implementa una solución integral basada en Inteligencia Artificial y Teoría de Juegos para la **optimización logística de rutas de distribución y la toma de decisiones estratégicas adversarias**. 

El sistema modela una red logística en una cuadrícula de $12 \times 12$ con topografía heterogénea (diferentes costos de terreno y obstáculos insalvables). A través de 8 fases bien definidas, combina algoritmos de búsqueda informada, optimización combinatorial, metaheurísticas avanzadas, teoría de juegos no cooperativos y búsqueda advesaria con poda Alfa-Beta. Además, incluye un panel interactivo desarrollado en **Streamlit (`app.py`)** para la ejecución y visualización en tiempo real de los experimentos y datos generados.

---

## Arquitectura de Fases y Algoritmos

El proyecto se estructura modularmente a lo largo de las siguientes fases:

### 1. Entorno Logístico e Infraestructura (Fases 1 y 2)
* **Modelado del Mapa:** Representación mediante una cuadrícula de $12 \times 12$ exportada a `mapa_logistico.csv`. Incorpora celdas con costos de desplazamiento diferenciados ($c = 1$ llano, $c = 3$ congestión, $c = 5$ zona difícil) y obstáculos inaccesibles (`X`).
* **Puntos Clave:** Definición del origen de la flota ($S$), destino final ($F$) y tres puntos intermedios de entrega ($D_1, D_2, D_3$).
* **Búsqueda Heurística Informada:**
  * **Distancia de Manhattan:** Utilizada como función heurística admisible y consistente:
    $$h(n) = |x_n - x_{\text{objetivo}}| + |y_n - y_{\text{objetivo}}|$$
  * **Greedy Best-First Search:** Selección de nodos guiada prioritariamente por $h(n)$.
  * **Algoritmo $A^*$ (A-Star):** Garantía de optimidad evaluando la función de costo total:
    $$f(n) = g(n) + h(n)$$
    donde $g(n)$ representa el costo acumulado real desde el nodo inicial.

### 2. Búsqueda Local (Fase 3)
* **Optimización de Secuencia de Visita:** Determinación del orden óptimo para visitar los puntos $\{D_1, D_2, D_3\}$.
* **Algoritmo Hill Climbing:** Búsqueda en el espacio de permutaciones de entregas utilizando una matriz de costos mínimos precomputada por $A^*$ para evitar recálculos redundantes.
* **Manejo de Vecindades:** Exploración mediante intercambio de nodos (*2-opt swap*) y evaluación de convergencia ante óptimos locales y mesetas a partir de 10 puntos de inicio aleatorios.

### 3. Metaheurísticas Combinatoriales (Fase 4)
Ejecución estadística comparativa (20 repeticiones por algoritmo) para la resolución del problema de ruteo:
* **Recocido Simulado (Simulated Annealing):**
  * Esquema de enfriamiento geométrico: $T_{k+1} = \alpha \cdot T_k$ con $\alpha = 0.95$.
  * Criterio de aceptación Metropolis-Hastings para peores soluciones:
    $$P(\Delta E, T) = e^{-\frac{\Delta E}{T}}$$
* **Algoritmo Genético (AG):**
  * Representación cromosómica basada en permutaciones de la secuencia de entregas.
  * Selección por torneo ($k = 3$), Cruza de Orden (OX1) para preservar permutaciones válidas y Mutación por Intercambio (*Swap Mutation*).

### 4. Teoría de Juegos y Análisis Estratégico (Fase 5)
* **Matriz de Pagos $3 \times 3$:** Modelado de un juego simultáneo de dos jugadores en forma normal entre nuestro Agente Logístico (Filas) y un Competidor Rivals (Columnas).
* **Análisis Cuantitativo:**
  * Identificación de estrategias dominadas y estrictamente dominantes.
  * Cálculo de Mejores Respuestas (*Best Responses*).
  * Determinación de **Equilibrios de Nash puros** en el punto de intercepción estratégica.

### 5. Búsqueda Adversaria (Fase 6)
* **Negociación Logística por Turnos:** Juego de suma cero entre Agente (MAX) y Competidor (MIN) para la asignación de recursos limitados (ej. vales de combustible y pases de prioridad).
* **Algoritmo Minimax:** Evaluación exhaustiva del árbol de decisiones.
* **Poda Alfa-Beta ($\alpha$-$\beta$ Pruning):** Optimización del espacio de estados reduciendo ramas irrelevantes cuando se cumple el criterio de corte:
  $$\alpha \ge \beta$$
* **Métrica de Eficiencia:** Conteo explícito y comparación del número de nodos explorados vs. podados.

### 6. Visualización y Datos Experimentales (Fases 7 y 8)
* **Exportación de Métricas:** Generación automática de `datos_experimentales.csv` conteniendo los costos, rutas y tiempos de ejecución de cada réplica.
* **Visualización Estadística:** Generación de `graficas_resultados.png` que incluye:
  1. *Boxplot* para comparar la estabilidad y distribución del costo de ruta.
  2. *Gráfica de Barras* para el tiempo de procesamiento promedio (s).
* **Resiliencia y Casos Límite:** Validación y manejo controlado de entradas inválidas, coordenadas en obstáculos e imprevistos de inaccesibilidad sin detener el flujo de ejecución.

---

## Interfaz Gráfica Interactiva (`app.py`)

El proyecto incluye una aplicación web basada en **Streamlit** que sirve como panel de control interactivo para visualizar los resultados de la libreta Jupyter (`proyecto2.ipynb`) de forma limpia y estilizada.

### Características de `app.py`:
* **Ejecución Dinámica:** Carga el código de `proyecto2.ipynb`, ejecuta las celdas en tiempo real de forma segura y captura las salidas estándar de consola.
* **Navegación Modular:** Barra lateral (*sidebar*) interactiva que permite filtrar los resultados por cada Fase individual o revisar la libreta completa.
* **Renderizado de Artefactos:** 
  * Despliega y permite descargar la gráfica generada (`graficas_resultados.png`).
  * Visualiza en una tabla interactiva de datos y permite descargar el archivo experimental (`datos_experimentales.csv`).
  * Opción para exportar el resumen completo de logs en formato de texto plano (`resultados_proyecto2.txt`).

---

## Estructura del Repositorio

```text
.
├── proyecto2.ipynb           # Notebook principal con las 8 Fases del proyecto
├── app.py                    # Aplicación de interfaz gráfica con Streamlit
├── mapa_logistico.csv        # Representación de la cuadrícula de terreno (12x12)
├── datos_experimentales.csv  # Resultados de las 20 ejecuciones de metaheurísticas
├── graficas_resultados.png   # Gráfica comparativa (Boxplot de costo y barras de tiempo)
├── requirements.txt          # Lista de dependencias del proyecto
└── README.md                 # Documentación del proyecto
```

---

## Requisitos e Instalación

### Pre-requisitos
* Python 3.10 o superior.
* Gestor de paquetes `pip`.

### Instalación

1. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/tu-usuario/proyecto-logistico-ia.git
   cd proyecto-logistico-ia
   ```

2. **Crear y activar un entorno virtual (Recomendado):**
   ```bash
   # En Windows
   python -m venv venv
   .\venv\Scripts\activate

   # En Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instalar las dependencias:**
   ```bash
   pip install pandas matplotlib numpy streamlit
   ```

---

## Instrucciones de Uso

### Opción 1: Ejecutar desde Jupyter Notebook
Para revisar la lógica paso a paso, ejecutar experimentos o modificar parámetros:

```bash
jupyter notebook proyecto2.ipynb
```
*Ejecuta secuencialmente todas las celdas desde la Fase 1 hasta la Fase 8.*

---

### Opción 2: Desplegar la Interfaz Web con Streamlit
Para visualizar los resultados de forma gráfica e interactiva mediante el panel web:

```bash
streamlit run app.py
```
Una vez ejecutado el comando, se abrirá automáticamente en tu navegador predeterminado la dirección local:
`http://localhost:8501`

---

## Resultados Destacados

| Métrica / Algoritmo | Recocido Simulado | Algoritmo Genético |
| :--- | :---: | :---: |
| **Costo Mínimo Encontrado** | $36.0$ | $36.0$ |
| **Consistencia (Desviación)** | Alta (Baja variabilidad) | Presencia de *outliers* ($\sim 38.0$) |
| **Tiempo de Ejecución Promedio** | $\sim 0.00010\text{ s}$ | $\sim 0.00099\text{ s}$ |

### Búsqueda Adversaria (Poda Alfa-Beta vs Minimax):
* **Valor Óptimo del Juego:** Consistente en ambos métodos.
* **Eficiencia Computacional:** La Poda Alfa-Beta logra una **reducción significativa de nodos evaluados** respecto al Minimax clásico, optimizando el tiempo de decisión estratégica en entornos de competencia.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.14
* **Librerías Cuentas/Matemáticas:** `numpy`, `pandas`
* **Visualización:** `matplotlib`
* **Entorno de Trabajo:** Jupyter Notebook / IPython
* **Framework Web / GUI:** Streamlit

---

## Licencia y Créditos

Proyecto desarrollado para el módulo de **Sistemas Inteligentes / Inteligencia Artificial**. Distribuido bajo la licencia MIT.