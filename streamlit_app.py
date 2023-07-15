import streamlit as st
import cv2
import pytesseract
import pandas as pd
from PIL import Image
import io
import base64

# 1. Drag and drop images
uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded Image.', use_column_width=True)
    
    # 2. Optimize the image for OCR
    # Convert the image to grayscale
    grayscale = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)
    
    # Apply dilation and erosion to remove some noise
    kernel = np.ones((1, 1), np.uint8)
    img = cv2.dilate(grayscale, kernel, iterations=1)
    img = cv2.erode(img, kernel, iterations=1)
    
    # Apply blur to smooth out the edges
    img = cv2.GaussianBlur(img, (5, 5), 0)
    
    # 3. OCR to extract the information
    # Remember to add your tesseract path here
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract' 
    result = pytesseract.image_to_string(img)
    st.write(result)
    
    # 4. Store into a CSV
    df = pd.DataFrame([result], columns=['Text'])
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    href = f'<a href="data:file/csv;base64,{b64}">Download CSV File</a> (right-click and save as &lt;some_name&gt;.csv)'
    st.markdown(href, unsafe_allow_html=True)

