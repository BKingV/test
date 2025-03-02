import streamlit as st
import pandas as pd
from docx import Document

st.title("📄 Онлайн-тестирование из Word-файла")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)
    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    
    st.text_area("Содержимое файла:", text, height=300)
