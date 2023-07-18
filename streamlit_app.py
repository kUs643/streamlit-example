import streamlit as st
from PIL import Image
import os
import io

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

        if st.button("Descargar imágenes"):
            save_images(all_images, 'descargas')

    elif page == "Página 2":
        st.header("Página 2")
        # Implementa la funcionalidad de la página 2 aquí

    elif page == "Página 3":
        st.header("Página 3")
        # Implementa la funcionalidad de la página 3 aquí

if __name__ == "__main__":
    app()

