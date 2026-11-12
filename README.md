# 2D Similarity Transformation Script for QGIS (`align.py`)

This Python script is designed to run inside **QGIS** (Python Console). It performs a **2D Similarity Transformation** (including rotation, translation, and uniform scaling) calculated by least squares, using control lines to precisely align geographic features.

---

## Main Features

- **Projection in Meters (EPSG:22195):** Temporarily reprojects geographic coordinates to perform mathematical calculations in meters, avoiding distortions and numerical errors.
- **Least Squares:** Supports 2 or more control lines to optimize the geometric transformation.
- **Geometry Support:** Transforms both point (`Point`) and line (`LineString`) features from the active layer selected in QGIS.

---

## Prerequisites

1. **Control Lines Layer:** The project must contain a vector layer of lines named exactly **`lineas_control`**.
2. **Line Selection:** You must select **at least 2 lines** in the `lineas_control` layer. 
   - The starting point of each line (`line[0]`) acts as the origin (current / misaligned position).
   - The ending point of each line (`line[-1]`) acts as the destination (correct / target position).
3. **Active Layer to Transform:** You must have an active layer in the QGIS layer panel and **select the features** (points or lines) you wish to transform.

---

## How to Run the Script in QGIS?

1. Open your project in **QGIS**.
2. Make sure you have created the **`lineas_control`** layer and selected at least **2 control lines** using the selection tool.
3. Select the layer whose features you want to align/transform in the QGIS layer panel, and select the specific features you want to move.
4. Open the **Python Console** in QGIS (`Plugins` > `Python Console` or `Ctrl + Alt + P`).
5. Copy and paste the content of `align.py` (or load it as a script) and run it.

The script will validate the layer's existence, calculate the similarity matrix based on the selected lines, and apply the transformation to the selected features of the active layer within an edit session.
