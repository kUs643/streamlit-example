import streamlit as st
from PIL import Image, ImageOps
import os
import shutil
import zipfile
import base64
import cv2
import numpy as np
import requests
import pandas as pd
from io import BytesIO

# Coordenadas de corte para las diferentes partes
PARTS = {
    'part1': (55, 79, 55+197, 79+96),
    'part2': (743, 72, 743+379, 72+91),
    'part3': (332, 299, 332+1257, 299+298)
}

def cut_image(image, coords):
    """Corta la imagen en las coordenadas dadas"""
    return image.crop(coords)

def save_images(images, folder_name):
    """Guarda las imágenes en la carpeta dada"""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for img_name, img in images.items():
        img.save(os.path.join(folder_name, f"{img_name}.png"))

def handle_upload(file, part):
    """Maneja la subida de archivos"""
    if file is not None:
        image = Image.open(file)
        cut_images = {f"partida{part}-{part_name}": cut_image(image, coords) for part_name, coords in PARTS.items()}
        return cut_images
    return {}

def create_zip_folder(folder_name):
    """Crea un archivo ZIP de la carpeta dada"""
    zip_filename = f"{folder_name}.zip"
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_name):
            for file in files:
                zipf.write(os.path.join(root, file), arcname=os.path.basename(file))
    return zip_filename

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Descargar {file_label}</a>'
    return href

def app():
    st.title("Analizador de imágenes de Valorant")
    st.sidebar.title("Navegación")
    page = st.sidebar.selectbox("Elige una página", ["Organizador", "Página 2", "Página 3"])

    if page == "Organizador":
        st.header("Organizador de partidas")

        all_images = {}
        for i in range(1, 6):
            st.subheader(f"Partida {i}")
            uploaded_file = st.file_uploader(f"Sube la imagen para la partida {i}", type=['png', 'jpg', 'jpeg'])
            images = handle_upload(uploaded_file, i)
            all_images.update(images)

            if i < 5:
                st.markdown("---")  # Linea separadora

        if st.button("Crear archivos"):
            folder_name = 'descargas'
            save_images(all_images, folder_name)
            zip_filename = create_zip_folder(folder_name)
            st.markdown(get_binary_file_downloader_html(zip_filename, 'ZIP'), unsafe_allow_html=True)

    elif page == "Extractor":
        st.header("Extractor")
        # Implementa la funcionalidad de la página 2 aquí
def process_img_1(img):
    img_gray = img.convert("L")
    img_darkened = img_gray.point(lambda p: p * 0.9)
    img_enhanced = img_darkened.point(lambda p: 255 * (p / 255) ** 0.8)
    return img_enhanced

def process_img_2(img):
    img_gray = img.convert("L")
    threshold = 100
    img_binary = img_gray.point(lambda p: p > threshold and 255)
    img_inverted = Image.fromarray(np.array(img_binary) ^ 255)
    final_img = img_inverted.convert("RGB")
    return final_img

def process_img_3(img):
    img_gray = img.convert('L')
    _, img_binary = cv2.threshold(np.array(img_gray), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    img_binary_pil = Image.fromarray(img_binary)
    img_inverted = ImageOps.invert(img_binary_pil)
    erosion_kernel = np.ones((3,3),np.uint8)
    img_eroded = cv2.erode(np.array(img_inverted), erosion_kernel, iterations = 1)
    return img_eroded

def ocr_space(image, overlay=False, api_key='YOUR_OCR_SPACE_API_KEY', language='eng', ocr_engine='2'):
    payload = {'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': language,
               'OCREngine': ocr_engine}
    response = requests.post('https://api.ocr.space/parse/image',
                             files={filename: image},
                             data=payload)
    result = response.json()
    text_detected = result.get('ParsedResults')[0].get('ParsedText')
    return text_detected

def main():
    st.title("Image Manipulator")
    uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True)
    
    if uploaded_files:
        if st.button('Convert'):
            ocr_results = []
            for file in uploaded_files:
                img = Image.open(file)
                if 'part1' in file.name:
                    processed_img = process_img_1(img)
                elif 'part2' in file.name:
                    processed_img = process_img_2(img)
                else:
                    processed_img = process_img_3(img)
                
                ocr_result = ocr_space(processed_img)
                ocr_results.append({file.name: ocr_result})
            
            st.write(ocr_results)

        if st.button('Download CSV'):
            df = pd.DataFrame(ocr_results)
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            href = f'<a href="data:file/csv;base64,{b64}" download="ocr_results.csv">Download CSV File</a>'
            st.markdown(href, unsafe_allow_html=True)

    elif page == "Página 3":
        st.header("Página 3")
        # Implementa la funcionalidad de la página 3 aquí



if __name__ == "__main__":
    app()

