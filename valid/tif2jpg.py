#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
from PIL import Image


# In[2]:


def tifs_to_jpgs(input_dir, output_dir):
    # Verificar si el directorio de salida existe, si no, crearlo
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Obtener la lista de archivos en el directorio de entrada
    tif_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]

    # Iterar sobre los archivos TIF y convertirlos a JPG
    for tif_file in tif_files:
        # Crear la ruta completa de entrada y salida
        input_tif = os.path.join(input_dir, tif_file)
        output_jpg = os.path.join(output_dir, os.path.splitext(tif_file)[0] + '.jpg')

        # Abrir la imagen TIF
        try:
            image = Image.open(input_tif)
        except IOError:
            print("No se pudo abrir el archivo:", input_tif)
            continue
        
        # Guardar la imagen como JPG
        try:
            image.save(output_jpg, "JPEG")
            print("Imagen convertida:", input_tif, "->", output_jpg)
        except IOError:
            print("No se pudo guardar la imagen como JPG:", output_jpg)

    print("Conversión completada.")


# In[3]:


def main():
    # Ejemplo de uso
    input_directory = "teselas_tif"
    output_directory = "teselas_jpg"
    tifs_to_jpgs(input_directory, output_directory)

if __name__ == "__main__":
    main()


# In[ ]:




