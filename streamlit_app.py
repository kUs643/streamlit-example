import streamlit as st
import os

# Streamlit configurations
st.set_option('deprecation.showfileUploaderEncoding', False)

def save_image(image, image_name):
    # Define the path where you want to save the images
    image_path = './cache/'

    # Check if the cache directory exists, if not, create it.
    if not os.path.exists(image_path):
        os.makedirs(image_path)

    # Save the image
    with open(os.path.join(image_path, image_name), 'wb') as f:
        f.write(image.getbuffer())
    return f"Image {image_name} saved!"

for i in range(5):
    st.write(f'### Game {i+1}')

    image1 = st.file_uploader("Drop your first image here", type=['png', 'jpg', 'jpeg'], key=f'1-{i}')
    image2 = st.file_uploader("Drop your second image here", type=['png', 'jpg', 'jpeg'], key=f'2-{i}')

    if image1 and image2:
        image1_name = f'partida{i+1}-imagen1.png'
        image2_name = f'partida{i+1}-imagen2.png'

        save_message1 = save_image(image1, image1_name)
        save_message2 = save_image(image2, image2_name)

        st.write(save_message1)
        st.write(save_message2)
