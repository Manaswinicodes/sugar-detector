import streamlit as st
import pandas as pd

st.title("Sugar Detector App")
st.write("This is a demo app for detecting sugar content in food items.")

# Example: Load some sample data (or integrate your OCR/Flask backend later)
data = pd.DataFrame({
    "Product": ["Apple Juice", "Soda", "Yogurt"],
    "Sugar (g)": [24, 39, 18]
})

st.table(data)
