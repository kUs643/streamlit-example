import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import cv2
import requests
import json
import pandas as pd
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
    import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import cv2
import requests
import json
import pandas as pd
import os

def process_image(img, part):
    if part == 1:
        # Convert the image to grayscale
        img_gray = img.convert("L")

        # Darken the image slightly
        img_darkened = img_gray.point(lambda p: p * 0.9)

        # Enhance contrast in the image
        img_enhanced = img_darkened.point(lambda p: 255 * (p / 255) ** 0.8)

        return img_enhanced

    elif part == 2:
        # Convert the image to grayscale
        img_gray = img.convert("L")

        # Binarize the image
        threshold = 100  # You might need to adjust this value based on your specific image
        img_binary = img_gray.point(lambda p: p > threshold and 255)

        # Invert the image (if necessary)
        img_inverted = Image.fromarray(np.array(img_binary) ^ 255)

        # Ensure the image is in the correct mode for saving
        final_img = img_inverted.convert("RGB")

        return final_img

    elif part == 3:
        # Convert the image to grayscale
        img_gray = img.convert('L')

        # Convert the grayscale image to binary using Otsu's binarization
        _, img_binary = cv2.threshold(np.array(img_gray), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

        # Convert the binary image back to PIL format
        img_binary_pil = Image.fromarray(img_binary)

        # Invert the colors of the binary image
        img_inverted = ImageOps.invert(img_binary_pil)

        # Define a structuring element for erosion
        erosion_kernel = np.ones((3,3),np.uint8)

        # Apply erosion to make the black regions thicker
        img_eroded = cv2.erode(np.array(img_inverted), erosion_kernel, iterations = 1)

        return img_eroded

def ocr_space(image, api_key='Your_API_Key', language='eng'):
    with open(image, 'rb') as image_file:
        img_data = image_file.read()
    url = 'https://api.ocr.space/parse/image'
    headers = {'apikey': api_key}
    data = {'language': language, 'isOverlayRequired': False, 'OCREngine': 2}
    response = requests.post(url, headers=headers, data=data, files={'image': img_data}).json()

    if response['IsErroredOnProcessing']:
        st.error("The OCR.space API returned an error:")
        st.write(response['ErrorMessage'])
        return None

    parsed_results = response['ParsedResults'][0]['ParsedText']
    return parsed_results

# Crear la barra de navegacion
st.sidebar.title("Navegación")
navigation = st.sidebar.radio("Ir a", ['Organizador', 'Extractor', 'Inyector'])

if navigation == 'Extractor':
    uploaded_files = st.file_uploader("Sube las imágenes", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

    if st.button('Convertir'):
        for uploaded_file in uploaded_files:
            with open(uploaded_file.name, "wb") as f:
                f.write(uploaded_file.getbuffer())
            img = Image.open(uploaded_file.name)
            part = int(uploaded_file.name.split("-")[-1][0])  # Assumes the name is in the format 'partidaN-parteM.jpg'
            img_processed = process_image(img, part)
            img_processed.save(f'processed/{uploaded_file.name}')

            result = ocr_space(f'processed/{uploaded_file.name}')

            if result is not None:
                st.write(f'Resultado para {uploaded_file.name}:')
                st.write(result)

        if st.button('Descargar resultados'):
            # Assuming all the results have been stored in a pandas DataFrame called 'df'
            df.to_csv('results.csv')
            st.success('¡Resultados descargados!')


elif navigation == 'Inyector':
    st.write("Esta es la sección Inyector.")

