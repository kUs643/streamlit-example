import streamlit as st
import numpy as np
from PIL import Image, ImageOps
import cv2
import requests
import pandas as pd
import base64

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

def ocr_space(image, overlay=False, api_key='K82787541488957', language='eng', ocr_engine='2'):
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

def extractor_page():
    st.header("Extractor")
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

def main():
    st.title("Image Manipulator")
    
    pages = {
        "Extractor": extractor_page,
        # Add more pages here if you have them
    }

    page = st.sidebar.selectbox("Choose a page", list(pages.keys()))
    pages[page]()

if __name__ == "__main__":
    main()

