import streamlit as st
import os
from PIL import Image, ImageOps
import cv2
import numpy as np
import requests
import pandas as pd

# Define las funciones para procesar las imágenes

def process_image_part1(image_path):
    # Cargar imagen
    img = Image.open(image_path)
    
    # Convertir la imagen a escala de grises
    img_gray = img.convert("L")

    # Oscurecer la imagen ligeramente
    img_darkened = img_gray.point(lambda p: p * 0.9)

    # Mejorar el contraste en la imagen
    img_enhanced = img_darkened.point(lambda p: 255 * (p / 255) ** 0.8)
    
    return img_enhanced

# Repite esto para process_image_part2 y process_image_part3 con las modificaciones correspondientes

# Define una función para extraer texto de la imagen usando OCR.space

def ocr_space(image_path, api_key):
    # Prepara la imagen para enviarla a OCR.space
    with open(image_path, 'rb') as image_file:
        img_data = image_file.read()
    
    # Define los parámetros de la API de OCR.space
    url = 'https://api.ocr.space/parse/image'
    headers = {'K82787541488957': api_key}
    data = {'file': img_data, 'OCREngine': 2}
    
    # Envia la solicitud y recupera la respuesta
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    
    # Extrae el texto de la respuesta
    result = response.json()
    text = result['ParsedResults'][0]['ParsedText']
    
    return text

# Crea la interfaz de usuario de Streamlit

st.title('Extractor de imágenes')

uploaded_files = st.file_uploader('Sube tus imágenes', type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

if uploaded_files:
    convert_button = st.button('Convertir')
    if convert_button:
        # Prepara un dataframe para almacenar los resultados
        df = pd.DataFrame(columns=['Imagen', 'Texto'])
        
        # Procesa cada archivo subido
        for uploaded_file in uploaded_files:
            # Guarda el archivo temporalmente
            with open(uploaded_file.name, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            # Procesa la imagen
            if 'part1' in uploaded_file.name:
                img = process_image_part1(uploaded_file.name)
            elif 'part2' in uploaded_file.name:
                img = process_image_part2(uploaded_file.name)
            else:
                img = process_image_part3(uploaded_file.name)
            
            # Guarda la imagen procesada
            img.save('processed_' + uploaded_file.name)
            
            # Extrae el texto de la imagen procesada
            text = ocr_space('processed_' + uploaded_file.name, YOUR_API_KEY)
            
            # Añade el resultado al dataframe
            df = df.append({'Imagen': uploaded_file.name, 'Texto': text}, ignore_index=True)
        
        # Muestra el dataframe de resultados
        st.dataframe(df)
        
        # Permite descargar el dataframe como CSV
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()  
        href = f'<a href="data:file/csv;base64,{b64}" download="text.csv">Descargar CSV</a>'
        st.markdown(href, unsafe_allow_html=True)


