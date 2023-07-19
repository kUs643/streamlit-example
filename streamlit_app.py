import streamlit as st
import os
import numpy as np
from PIL import Image, ImageOps
import cv2
import requests
import pandas as pd
import base64

# API key for ocr.space
OCR_SPACE_API_KEY = 'K82787541488957'

# Define a function to make an OCR.space API call
def ocr_space(image_path):
    with open(image_path, 'rb') as img:
        response = requests.post(
            url='https://api.ocr.space/parse/image',
            files={'image': img},
            data={
                'isOverlayRequired': True,
                'apikey': OCR_SPACE_API_KEY,
                'OCREngine': 2
            }
        )
    return response.json()

# Define a function to download CSV file
def download_link(object_to_download, download_filename, download_link_text):
    if isinstance(object_to_download,pd.DataFrame):
        object_to_download = object_to_download.to_csv(index=False)

    b64 = base64.b64encode(object_to_download.encode()).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'

# Create a sidebar for image upload
st.set_option('deprecation.showfileUploaderEncoding', False) # Disable warning
uploaded_files = st.file_uploader("Upload Images", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# Apply image processing based on the part specified in the name
df_ocr = pd.DataFrame(columns=['Image Name', 'Part', 'OCR Text'])
for uploaded_file in uploaded_files:
    st.image(uploaded_file)
    img = Image.open(uploaded_file)
    img_name = uploaded_file.name
    img_part = img_name.split('_')[0]

    if img_part == 'first':
        img_gray = img.convert("L")
        img_darkened = img_gray.point(lambda p: p * 0.9)
        img_enhanced = img_darkened.point(lambda p: 255 * (p / 255) ** 0.8)
        img = img_enhanced
    elif img_part == 'second':
        img_gray = img.convert("L")
        threshold = 100
        img_binary = img_gray.point(lambda p: p > threshold and 255)
        img_inverted = Image.fromarray(np.array(img_binary) ^ 255)
        final_img = img_inverted.convert("RGB")
        img = final_img
    elif img_part == 'third':
        img_gray = img.convert('L')
        _, img_binary = cv2.threshold(np.array(img_gray), 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        img_binary_pil = Image.fromarray(img_binary)
        img_inverted = ImageOps.invert(img_binary_pil)
        erosion_kernel = np.ones((3,3),np.uint8)
        img_eroded = cv2.erode(np.array(img_inverted), erosion_kernel, iterations = 1)
        img = Image.fromarray(img_eroded)

    img.save(f'processed_{img_name}')
    ocr_result = ocr_space(f'processed_{img_name}')
    df_ocr = df_ocr.append({'Image Name': img_name, 'Part': img_part, 'OCR Text': ocr_result['ParsedResults'][0]['ParsedText']}, ignore_index=True)
    os.remove(f'processed_{img_name}')

if st.button("Convert"):
    st.write(df_ocr)

if st.button("Download CSV file"):
    tmp_download_link = download_link(df_ocr, 'ocr_output.csv', 'Click here to download your data!')
    st.markdown(tmp_download_link, unsafe_allow_html=True)


