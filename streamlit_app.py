import streamlit as st
import requests
import csv
import base64

# OCR.space API key and endpoint
api_key = 'K82787541488957'
endpoint = 'https://api.ocr.space/parse/image'

# Initialize an empty list to store image URLs
image_urls = []

# Start of Streamlit application
st.title('OCR Application')

uploaded_file = st.file_uploader("Choose an image file")
if uploaded_file is not None:
    image_urls.append(uploaded_file.getvalue())

# Button to start OCR process
if st.button('Start OCR'):
    # Loop through image URLs and perform OCR on each image
    for url in image_urls:
        # Request OCR using API endpoint and image URL
        response = requests.post(endpoint, 
            files={'url': (None, url)},
            data={
                'apikey': api_key,
                'language': 'eng'
            })

        # Parse OCR results from response JSON
        result = response.json()
        if result['IsErroredOnProcessing']:
            st.write(f'OCR error: {result["ErrorMessage"]}')
        else:
            parsed_results = result['ParsedResults']
            if len(parsed_results) > 0:
                text = parsed_results[0]['ParsedText']
                st.write(f'OCR result for {url}: {text}')

                # Write results to CSV
                with open('ocr_results.csv', 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Image URL", "OCR Result"])
                    writer.writerow([url, text])
                    
    # Download CSV button
    if st.button('Download CSV'):
        with open('ocr_results.csv', 'r') as file:
            csv = file.read()
        b64 = base64.b64encode(csv.encode()).decode()  # some strings
        href = f'<a href="data:file/csv;base64,{b64}" download="ocr_results.csv">Download CSV File</a>'
        st.markdown(href, unsafe_allow_html=True)
