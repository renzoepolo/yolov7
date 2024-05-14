#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from osgeo import ogr, gdal


# In[2]:


def create_raster_bbox(raster):
    geotransform = raster.GetGeoTransform()
    min_x = geotransform[0]
    max_y = geotransform[3]
    max_x = min_x + geotransform[1] * raster.RasterXSize
    min_y = max_y + geotransform[5] * raster.RasterYSize

    bbox = ogr.Geometry(ogr.wkbLinearRing)
    bbox.AddPoint(min_x, max_y)
    bbox.AddPoint(max_x, max_y)
    bbox.AddPoint(max_x, min_y)
    bbox.AddPoint(min_x, min_y)
    bbox.AddPoint(min_x, max_y)  # Cerrar el anillo
    raster_bbox = ogr.Geometry(ogr.wkbPolygon)
    raster_bbox.AddGeometry(bbox)
    return raster_bbox

def intersects_raster_bbox(geometry, raster_bbox):
    return geometry.Intersects(raster_bbox)

def geo_to_pixel(x, y, raster_geo):
    pixel_x = int((x - raster_geo[0]) / raster_geo[1])
    pixel_y = int((y - raster_geo[3]) / -raster_geo[5])  # El factor de escala Y es NEGATIVO!
    return pixel_x, pixel_y

def transform_geometries(shapefile_path, raster_path, output_path, annotation_file):
    try:
        # Abrir el shapefile
        shapefile = ogr.Open(shapefile_path)
        layer = shapefile.GetLayer()

        # Abrir el raster
        raster = gdal.Open(raster_path)
        raster_geo = raster.GetGeoTransform()

        # Crear el bounding box del raster
        raster_bbox = create_raster_bbox(raster)

        # Crear el archivo Geopackage de salida
        driver = ogr.GetDriverByName("GPKG")
        output_ds = driver.CreateDataSource(output_path)
        output_layer = output_ds.CreateLayer("transformed_geometries", geom_type=ogr.wkbPolygon)

        # No asignar sistema de coordenadas espaciales
        output_layer_defn = output_layer.GetLayerDefn()
        output_layer_defn.SetGeomType(ogr.wkbPolygon)
        output_layer.CreateField(ogr.FieldDefn("id", ogr.OFTInteger))

        annotations_list = []  # Lista para almacenar anotaciones para esta imagen

        # Iterar sobre las características y obtener las geometrías
        for feature in layer:
            geometry = feature.GetGeometryRef()
            if intersects_raster_bbox(geometry, raster_bbox):
                for i in range(geometry.GetGeometryCount()):
                    sub_geometry = geometry.GetGeometryRef(i)
                    sub_geometry = sub_geometry.Intersection(raster_bbox)  # Si existe intersección, obtener la geometría
                    for j in range(sub_geometry.GetGeometryCount()):
                        polygon = sub_geometry.GetGeometryRef(j)
                        transformed_polygon = ogr.Geometry(ogr.wkbPolygon)
                        ring = ogr.Geometry(ogr.wkbLinearRing)
                        pixel_coords = []  # Lista para almacenar coordenadas de píxeles del bounding box
                        for k in range(polygon.GetPointCount()):
                            x, y, _ = polygon.GetPoint(k)
                            pixel_x, pixel_y = geo_to_pixel(x, y, raster_geo)
                            ring.AddPoint(pixel_x, pixel_y)
                            pixel_coords.append((pixel_x, pixel_y))  # Almacenar coordenadas de píxeles
                        ring.CloseRings()
                        transformed_polygon.AddGeometry(ring)
                        output_feature = ogr.Feature(output_layer_defn)
                        output_feature.SetGeometry(transformed_polygon)
                        output_feature.SetField("id", feature.GetFID())
                        output_layer.CreateFeature(output_feature)
                        output_feature = None

                        # Agregar la anotación a la lista de anotaciones
                        tipo = feature.GetField("TIPO")

                        # Calcular bounding box en coordenadas de píxeles
                        if pixel_coords:
                            min_x = min(pixel_coords, key=lambda item: item[0])[0]
                            max_x = max(pixel_coords, key=lambda item: item[0])[0]
                            min_y = min(pixel_coords, key=lambda item: item[1])[1]
                            max_y = max(pixel_coords, key=lambda item: item[1])[1]

                            # Agregar información del bounding box a la lista de anotaciones
                            annotations_list.append(f"{tipo} {min_x} {min_y} {max_x} {max_y}\n")

        output_ds = None
        print("Geometrías transformadas guardadas en:", output_path)

        # Escribir todas las anotaciones en el archivo de anotaciones correspondiente
        with open(annotation_file, 'w') as f:
            for annotation in annotations_list:
                f.write(annotation)

    except Exception as e:
        print(f"Error procesando {shapefile_path} con {raster_path}: {e}")


# In[3]:


def main():
    rois = "rois/rois.gpkg"
    dir_raster = "teselas_tif"
    dir_rois_output = "rois/transformed/"
    annotations_dir = "labels/"

    if not os.path.exists(dir_rois_output):
        os.makedirs(dir_rois_output)

    if not os.path.exists(annotations_dir):
        os.makedirs(annotations_dir)

    for tif_file in os.listdir(dir_raster):
        if tif_file.endswith('.tif'):
            input_tif = os.path.join(dir_raster, tif_file)
            output_roi = os.path.join(dir_rois_output, os.path.splitext(tif_file)[0] + '.gpkg')
            annotation_file = os.path.join(annotations_dir, os.path.splitext(tif_file)[0] + '.txt')
            
            # Aplicar transformación a cada geometría
            transform_geometries(rois, input_tif, output_roi, annotation_file)

    print("Proceso completado.")

if __name__ == "__main__":
    main()


# In[ ]:




