import streamlit as st
import pytesseract
import requests
import cv2
import numpy as np
from PIL import Image
import re

def preprocess_image(image):
    """Convert image to grayscale, apply thresholding and blur for better OCR results."""
    gray = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    return cv2.GaussianBlur(thresh, (3, 3), 0)

def extract_text(image):
    """Extract text from preprocessed image using pytesseract."""
    processed_image = preprocess_image(image)
    return pytesseract.image_to_string(processed_image)

def get_nutrition_info(query):
    """Fetch nutrition info from Open Food Facts API."""
    food_terms = extract_food_terms(query)
    if not food_terms:
        return None
    
    search_term = "+".join(food_terms.split())
    api_url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={search_term}&json=true"
    
    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("products", [{}])[0]  # Return first matching product or empty dict
    except requests.RequestException:
        return None

def extract_food_terms(text):
    """Extract product name from OCR text while ignoring unnecessary lines."""
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    for line in lines:
        if not re.search(r'(ingredients|nutrition facts|serving size)', line.lower()) and 3 < len(line) < 50:
            return line
    return lines[0] if lines else ""

def extract_sugar_content(data, ocr_text):
    """Extract sugar content from API data or OCR text."""
    if data:
        sugar_value = data.get("nutriments", {}).get("sugars_100g")
        if sugar_value is not None:
            return f"{sugar_value}g per 100g"
    
    for pattern in [r'Sugars?\s*[:]+\s*([0-9.]+)\s*g', r'of which sugars\s*[:]+\s*([0-9.]+)\s*g']:
        match = re.search(pattern, ocr_text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}g (from label)"
    
    return "Not found"

def analyze_sugar_level(sugar_str):
    """Analyze sugar level and return category with corresponding color."""
    match = re.search(r'([0-9.]+)', sugar_str)
    if match:
        sugar_val = float(match.group(1))
        if sugar_val < 5:
            return "Low", "green"
        elif sugar_val < 10:
            return "Medium", "orange"
        return "High", "red"
    return "Unknown", "gray"

def main():
    st.title("Sugar Detector - Nutritional Label Scanner")
    st.markdown("Upload a food label image to analyze sugar content.")
    
    uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
    
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image', use_column_width=True)
        
        with st.spinner("Extracting text..."):
            text = extract_text(image)
        
        st.expander("View Extracted Text").text(text)
        
        if st.button("Analyze Sugar Content"):
            with st.spinner("Analyzing..."):
                data = get_nutrition_info(text)
                product_name = data.get('product_name', 'Unknown Product') if data else "Unknown"
                st.info(f"Identified Product: **{product_name}**")
                
                sugar_content = extract_sugar_content(data, text)
                st.markdown(f"**Sugar Content:** {sugar_content}")
                
                level, color = analyze_sugar_level(sugar_content)
                st.markdown(f"**Sugar Level:** <span style='color:{color};font-weight:bold'>{level}</span>", unsafe_allow_html=True)
                
                st.subheader("Health Recommendations")
                if level == "High":
                    st.warning("⚠️ High sugar content. Consider alternatives.")
                elif level == "Medium":
                    st.info("🔍 Moderate sugar level. Consume in moderation.")
                elif level == "Low":
                    st.success("✅ Low sugar content. Good choice!")
                else:
                    st.info("⚠️ Could not determine sugar level. Check manually.")
                
                if data:
                    st.expander("View Full Nutrition Data").json(data.get("nutriments", {}))

if __name__ == "__main__":
    main()
