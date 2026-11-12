# Script de Transformación de Similitud 2D para QGIS (`align.py`)

Este script de Python está diseñado para ejecutarse dentro de **QGIS** (Python Console). Permite realizar una **Transformación de Similitud 2D** (que incluye rotación, traslación y escala uniforme) calculada por mínimos cuadrados, utilizando líneas de control para alinear elementos geográficos con precisión.

---

## Características Principales

- **Proyección en Metros (EPSG:22195):** Reproyecta temporalmente las coordenadas geográficas para realizar los cálculos matemáticos en metros, evitando distorsiones y errores numéricos.
- **Mínimos Cuadrados:** Soporta 2 o más líneas de control para optimizar la transformación geométrica.
- **Soporte de Geometrías:** Transforma tanto elementos puntuales (`Point`) como líneas (`LineString`) de la capa activa seleccionada en QGIS.

---

## Requisitos Previos

1. **Capa de Líneas de Control:** Es indispensable que el proyecto cuente con una capa vectorial de líneas nombrada exactamente **`lineas_control`**.
2. **Selección de Líneas:** Debes seleccionar **al menos 2 líneas** en la capa `lineas_control`. 
   - El punto inicial de cada línea (`line[0]`) actúa como el origen (posición actual / desalineada).
   - El punto final de cada línea (`line[-1]`) actúa como el destino (posición correcta / objetivo).
3. **Capa Activa a Transformar:** Debes tener una capa activa en el panel de capas de QGIS y **seleccionar los elementos** (puntos o líneas) que deseas transformar.

---

## ¿Cómo Correr el Script en QGIS?

1. Abre tu proyecto en **QGIS**.
2. Asegúrate de tener creada la capa **`lineas_control`** y selecciona al menos **2 líneas de control** utilizando la herramienta de selección.
3. Selecciona en el panel de capas de QGIS la capa cuyos elementos deseas alinear/transformar, y selecciona los elementos específicos que quieres mover.
4. Abre la **Consola de Python** en QGIS (`Plugins` > `Python Console` o `Ctrl + Alt + P`).
5. Copia y pega el contenido de `align.py` (o cárgalo como script) y ejecútalo.

El script validará la existencia de la capa, calculará la matriz de similitud basada en las líneas seleccionadas y aplicará la transformación a los elementos seleccionados de la capa activa dentro de una sesión de edición.
