import math
import numpy as np
from qgis.core import (
    QgsProject, 
    QgsGeometry, 
    QgsPointXY, 
    QgsCoordinateReferenceSystem, 
    QgsCoordinateTransform
)

def calcular_transformacion_similitud(src_points_4326, dst_points_4326, project):
    """
    Calcula una Transformación de Similitud 2D (Rotación, Traslación y Escala Uniforme)
    por mínimos cuadrados, reproyectando a metros (EPSG:22195) para evitar errores.
    Funciona perfectamente con 2 o más líneas.
    """
    n = len(src_points_4326)
    if n < 2:
        print("¡Error! Se necesitan al menos 2 líneas de control seleccionadas.")
        return None, None, None

    # Configurar transformadores a metros (EPSG:22195)
    crs_4326 = QgsCoordinateReferenceSystem("EPSG:4326")
    crs_meters = QgsCoordinateReferenceSystem("EPSG:22195")
    
    trans_to_m = QgsCoordinateTransform(crs_4326, crs_meters, project)
    trans_to_deg = QgsCoordinateTransform(crs_meters, crs_4326, project)

    # Proyectar puntos a metros
    src_m = [(trans_to_m.transform(QgsPointXY(pt[0], pt[1])).x(), 
              trans_to_m.transform(QgsPointXY(pt[0], pt[1])).y()) for pt in src_points_4326]
    
    dst_m = [(trans_to_m.transform(QgsPointXY(pt[0], pt[1])).x(), 
              trans_to_m.transform(QgsPointXY(pt[0], pt[1])).y()) for pt in dst_points_4326]

    src_arr = np.array(src_m)
    dst_arr = np.array(dst_m)

    # 1. Centrar coordenadas (evita desbordes numéricos)
    src_centroid = np.mean(src_arr, axis=0)
    dst_centroid = np.mean(dst_arr, axis=0)

    src_centered = src_arr - src_centroid
    dst_centered = dst_arr - dst_centroid

    # 2. Armar matriz para Similitud: 4 parámetros [a, b, tx, ty]
    # x' = a*x - b*y + tx
    # y' = b*x + a*y + ty
    A = []
    B = []

    for (x, y), (x_prime, y_prime) in zip(src_centered, dst_centered):
        A.append([x, -y, 1.0, 0.0])
        A.append([y,  x, 0.0, 1.0])
        B.append(x_prime)
        B.append(y_prime)

    A_matrix = np.array(A)
    B_vector = np.array(B)

    # Resolver por mínimos cuadrados
    params, _, _, _ = np.linalg.lstsq(A_matrix, B_vector, rcond=None)
    a, b, tx, ty = params

    # Empaquetar resultados para aplicar la transformación directa
    transform_data = {
        'a': a, 'b': b, 'tx': tx, 'ty': ty,
        'src_centroid': src_centroid,
        'dst_centroid': dst_centroid
    }
    
    return transform_data, trans_to_m, trans_to_deg

def aplicar_transformacion(x, y, data, trans_to_m, trans_to_deg):
    # 1. Pasar a metros
    pt_m = trans_to_m.transform(QgsPointXY(x, y))
    xm, ym = pt_m.x(), pt_m.y()

    # 2. Descentrar origen
    xc = xm - data['src_centroid'][0]
    yc = ym - data['src_centroid'][1]

    # 3. Aplicar ecuaciones de similitud
    a, b, tx, ty = data['a'], data['b'], data['tx'], data['ty']
    x_prime_c = a * xc - b * yc + tx
    y_prime_c = b * xc + a * yc + ty

    # 4. Reincorporar centro de destino
    x_prime = x_prime_c + data['dst_centroid'][0]
    y_prime = y_prime_c + data['dst_centroid'][1]

    # 5. Volver a EPSG:4326 (grados)
    pt_deg = trans_to_deg.transform(QgsPointXY(float(x_prime), float(y_prime)))
    return pt_deg.x(), pt_deg.y()

# --- PROCESO PRINCIPAL ---
project = QgsProject.instance()

capa_control = project.mapLayersByName("lineas_control")
if not capa_control:
    print("No se encontró la capa 'lineas_control'.")
else:
    layer_ctrl = capa_control[0]
    selected_lines = layer_ctrl.selectedFeatures()
    
    if len(selected_lines) < 2:
        print("¡Atención! Selecciona al menos 2 líneas en la capa 'lineas_control'.")
    else:
        src_pts = []
        dst_pts = []
        
        for feat in selected_lines:
            geom = feat.geometry()
            line = geom.asMultiPolyline()[0] if geom.isMultipart() else geom.asPolyline()
            if len(line) >= 2:
                src_pts.append((line[0].x(), line[0].y())) # Origen (malo)
                dst_pts.append((line[-1].x(), line[-1].y())) # Destino (bueno)
        
        transform_data, trans_to_m, trans_to_deg = calcular_transformacion_similitud(src_pts, dst_pts, project)
        
        if transform_data is not None:
            active_layer = qgis.utils.iface.activeLayer()
            if not active_layer:
                print("Selecciona una capa activa en el panel de capas.")
            else:
                selected_elements = active_layer.selectedFeatures()
                if not selected_elements:
                    print(f"No hay elementos seleccionados en la capa '{active_layer.name}'.")
                else:
                    active_layer.startEditing()
                    count = 0
                    
                    for elem in selected_elements:
                        g = elem.geometry()
                        if g.isEmpty():
                            continue
                        
                        if g.type() == 0:  # Point
                            pt = g.asPoint()
                            nx, ny = aplicar_transformacion(pt.x(), pt.y(), transform_data, trans_to_m, trans_to_deg)
                            active_layer.changeGeometry(elem.id(), QgsGeometry.fromPointXY(QgsPointXY(nx, ny)))
                            count += 1
                        elif g.type() == 1:  # LineString
                            new_points = []
                            for pt in g.asPolyline():
                                nx, ny = aplicar_transformacion(pt.x(), pt.y(), transform_data, trans_to_m, trans_to_deg)
                                new_points.append(QgsPointXY(nx, ny))
                            active_layer.changeGeometry(elem.id(), QgsGeometry.fromPolylineXY(new_points))
                            count += 1
                            
                    print(f"¡Éxito! Se transformaron {count} elementos usando el método de Similitud (estilo ALIGN).")
                    print("Revisa el resultado: ahora sí deberían encajar perfecto en la cuadra.")