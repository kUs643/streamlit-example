import streamlit as st
import os
import cv2
import numpy as np
from PIL import Image, ImageOps
import requests
import pandas as pd
import base64
import tempfile

@st.cache(show_spinner=False)
def process_image(img_path, process_type):
    img = Image.open(img_path)
    
    if process_type == "part1":
        img_gray = img.convert("L")
        img_darkened = img_gray.point(lambda p: p * 0.9)
        img_enhanced = img_darkened.point(lambda p: 255 * (p / 255) ** 0.8)
        img_final = img_enhanced
    elif process_type == "part2":
        img_gray = img.convert("L")
        threshold = 100  
        img_binary = img_gray.point(lambda p: p > threshold and 255)
        img_inverted = Image.fromarray(np.array(img_binary) ^ 255)
        img_final = img_inverted.convert("RGB")
    else:
        img_gray = img.convert('L')
        _, img_binary = cv2.threshold(np.array(img_gray), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        img_binary_pil = Image.fromarray(img_binary)
        img_inverted = ImageOps.invert(img_binary_pil)
        erosion_kernel = np.ones((3,3),np.uint8)
        img_eroded = cv2.erode(np.array(img_inverted), erosion_kernel, iterations = 1)
        img_final = Image.fromarray(img_eroded)
    
    img_final.save(img_path)
    return img_path

@st.cache(show_spinner=False)
def ocr_space_url(url, overlay=False, api_key='YOUR_API_KEY'):
    payload = {'url': url,
               'isOverlayRequired': overlay,
               'apikey': api_key,
               'language': 'eng',
               'OCREngine': 2
               }
    r = requests.post('https://api.ocr.space/parse/image', data=payload,)
    return r.json()

def main():
    st.title("Extractor")
    uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    convert_button = st.button("Convertir")
    
    if convert_button:
        if uploaded_files is not None:
            image_list = []
            for uploaded_file in uploaded_files:
                tfile = tempfile.mkstemp(suffix=".png")[1] 
                with open(tfile, 'wb') as f:
                    f.write(uploaded_file.read())
                process_type = "part1" if "part1" in uploaded_file.name else "part2" if "part2" in uploaded_file.name else "part3"
                processed_img_path = process_image(tfile, process_type)
                image_list.append(processed_img_path)
            
            st.write("Las imágenes procesadas están disponibles en las siguientes URLs:")
            for img_path in image_list:
                st.write(f"URL: {img_path}")  # Substitute with actual hosted URLs
                json_response = ocr_space_url(img_path)  # Substitute with actual hosted URLs
                # Display parsed text
                for i in json_response.get("ParsedResults"):
                    st.write("Texto extraído:")
                    st.write(i.get("ParsedText"))

            download_button = st.button("Descargar CSV")
            
            if download_button:
                # Construct CSV from extracted text
                data = []
                for img_path in image_list:
                    json_response = ocr_space_url(img_path)
                    for i in json_response.get("ParsedResults"):
                        data.append([img_path, i.get("ParsedText")])

                df = pd.DataFrame(data, columns=["Image URL", "Extracted Text"])
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()  # some strings
                href = f'<a href="data:file/csv;base64,{b64}" download="extracted_text.csv">Download CSV File</a>'
                st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

