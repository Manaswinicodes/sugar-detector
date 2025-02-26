import streamlit as st
import pytesseract
import requests
import cv2
import numpy as np
from PIL import Image

def extract_text(image):
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

def get_nutrition_info(query):
    api_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&json=true"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if "products" in data and data["products"]:
            return data["products"][0]  # Return the first matching product
    return None

def main():
    st.title("Nutritional Label Scanner")
    uploaded_file = st.file_uploader("Upload a food label image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        text = extract_text(image)
        st.subheader("Extracted Text:")
        st.text(text)
        
        if st.button("Analyze Nutrition"):
            data = get_nutrition_info(text)
            if data:
                st.subheader("Nutrition Information:")
                st.write(f"**Product Name:** {data.get('product_name', 'Unknown')}")
                st.write("**Nutrients:**")
                st.json(data.get("nutriments", {}))
            else:
                st.error("Could not fetch nutrition data.")

if __name__ == "__main__":
    main()
