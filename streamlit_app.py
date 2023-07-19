import streamlit as st
from PIL import Image
import os

# Crear una lista para almacenar todas las imágenes de las partidas
imagenes_partidas = [None]*5

# Crear directorio para almacenar imágenes cortadas
if not os.path.exists('cortadas'):
    os.makedirs('cortadas')

# Crear la barra de navegacion
st.sidebar.title("Navegación")
navigation = st.sidebar.radio("Ir a", ['Organizador', 'Otro', 'Inyector'])

if navigation == 'Organizador':
    # Crear los recuadros para subir las imágenes
    for i in range(5):
        st.header(f"Partida {i+1}")
        uploaded_file = st.file_uploader(f"Sube la imagen para la partida {i+1}", type=['png', 'jpg', 'jpeg'])
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            imagenes_partidas[i] = image
            st.image(image, caption=f"Imagen subida para la partida {i+1}.", use_column_width=True)

    # Botón para cortar y guardar las imágenes
    if st.button('Cortar y guardar imágenes'):
        for i, image in enumerate(imagenes_partidas):
            if image is not None:
                # Definir las regiones a cortar
                box1 = (55, 79, 55+197, 79+96)
                box2 = (743, 72, 743+379, 72+91)
                box3 = (332, 299, 332+1257, 299+298)

                # Cortar las imágenes
                cropped1 = image.crop(box1)
                cropped2 = image.crop(box2)
                cropped3 = image.crop(box3)

                # Guardar las imágenes cortadas
                cropped1.save(f"cortadas/partida{i+1}-parte1.jpg")
                cropped2.save(f"cortadas/partida{i+1}-parte2.jpg")
                cropped3.save(f"cortadas/partida{i+1}-parte3.jpg")

        st.success('¡Imágenes cortadas y guardadas!')

elif navigation == 'Otro':
    st.write("Esta es la sección Otro.")

elif navigation == 'Inyector':
    st.write("Esta es la sección Inyector.")

