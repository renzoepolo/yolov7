#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from osgeo import gdal
import samgeo
import geopandas as gpd


# In[3]:


def descargar_imagenes(poligonos, download_dir):
  """
  Descarga imágenes completas para cada polígono en la capa de polígonos.

  Args:
    poligonos: Capa de polígonos GeoPandas.
    download_dir: Directorio de salida para guardar las imágenes.
  """
  os.makedirs(download_dir, exist_ok=True)
    
  for index, poligono in poligonos.iterrows():
    bbox = list(poligono.geometry.bounds)
    filename = os.path.join(download_dir, f"bbox_{index}.tif")
    samgeo.tms_to_geotiff(output=filename, bbox=bbox, zoom=18, source="Satellite", overwrite=True)

def split_raster(filename, out_dir, tile_size, overlap):
    """Split a raster into tiles.

    Args:
        filename (str): The path or http URL to the raster file.
        out_dir (str): The path to the output directory.
        tile_size (int | tuple, optional): The size of the tiles. Can be an integer or a tuple of (width, height). Defaults to 256.
        overlap (int, optional): The number of pixels to overlap between tiles. Defaults to 0.

    Raises:
        ImportError: Raised if GDAL is not installed.
    """

    # Open the input GeoTIFF file
    ds = gdal.Open(filename)
    img_name = os.path.splitext(os.path.basename(filename))[0]

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    if isinstance(tile_size, int):
        tile_width = tile_size
        tile_height = tile_size
    elif isinstance(tile_size, tuple):
        tile_width = tile_size[0]
        tile_height = tile_size[1]

    # Get the size of the input raster
    width = ds.RasterXSize
    height = ds.RasterYSize

    # Calculate the number of tiles needed in both directions, taking into account the overlap
    num_tiles_x = (width - overlap) // (tile_width - overlap) + int(
        (width - overlap) % (tile_width - overlap) > 0
    )
    num_tiles_y = (height - overlap) // (tile_height - overlap) + int(
        (height - overlap) % (tile_height - overlap) > 0
    )

    # Get the georeferencing information of the input raster
    geotransform = ds.GetGeoTransform()

    # Loop over all the tiles
    for i in range(num_tiles_x):
        for j in range(num_tiles_y):
            # Calculate the pixel coordinates of the tile, taking into account the overlap and clamping to the edge of the raster
            x_min = i * (tile_width - overlap)
            y_min = j * (tile_height - overlap)
            x_max = min(x_min + tile_width, width)
            y_max = min(y_min + tile_height, height)

            # Adjust the size of the last tile in each row and column to include any remaining pixels
            if i == num_tiles_x - 1:
                x_min = max(x_max - tile_width, 0)
            if j == num_tiles_y - 1:
                y_min = max(y_max - tile_height, 0)

            # Calculate the size of the tile, taking into account the overlap
            tile_width = x_max - x_min
            tile_height = y_max - y_min

            # Set the output file name
            output_file = f"{out_dir}/{img_name}_{i}_{j}.tif"

            # Create a new dataset for the tile
            driver = gdal.GetDriverByName("GTiff")
            tile_ds = driver.Create(
                output_file,
                tile_width,
                tile_height,
                ds.RasterCount,
                ds.GetRasterBand(1).DataType,
            )

            # Calculate the georeferencing information for the output tile
            tile_geotransform = (
                geotransform[0] + x_min * geotransform[1],
                geotransform[1],
                0,
                geotransform[3] + y_min * geotransform[5],
                0,
                geotransform[5],
            )

            # Set the geotransform and projection of the tile
            tile_ds.SetGeoTransform(tile_geotransform)
            tile_ds.SetProjection(ds.GetProjection())

            # Read the data from the input raster band(s) and write it to the tile band(s)
            for k in range(ds.RasterCount):
                band = ds.GetRasterBand(k + 1)
                tile_band = tile_ds.GetRasterBand(k + 1)
                tile_data = band.ReadAsArray(x_min, y_min, tile_width, tile_height)
                tile_band.WriteArray(tile_data)

            # Close the tile dataset
            tile_ds = None

    # Close the input dataset
    ds = None

def teselar_imagenes(input_dir, output_dir, tile_size, overlap):
    # Iterar sobre las imágenes en el directorio de entrada
    for filename in os.listdir(input_dir):
        if filename.endswith('.tif'):
            # Ruta completa de la imagen de entrada
            input_path = os.path.join(input_dir, filename)
            print(input_path)
            # Llamar a la función split_raster para generar las teselas
            split_raster(input_path, output_dir, tile_size, overlap) # Script proveniente de samgeo. Se copio para acomodar el nombre del archivo de salida


# In[4]:


def main():
    poligonos = gpd.read_file('bbox_download/cuadros_delimitadores.gpkg')
    download_dir = 'images_tif'
    tile_dir = 'teselas_tif'
    tile_size = 640  # Ajusta el tamaño de la tesela según tus necesidades
    tile_overlap = 0

    # Descargar imágenes
    descargar_imagenes(poligonos, download_dir)

    # Teselar imágenes
    teselar_imagenes(download_dir, tile_dir, tile_size, tile_overlap)

if __name__ == "__main__":
    main()


# In[ ]:




