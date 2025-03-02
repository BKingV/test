import streamlit as st
from docx import Document

st.title("📋 Проверка структуры файла")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)

    # Выводим текст с указанием стиля (обычный текст, заголовки и т. д.)
    st.subheader("📜 Весь текст из файла с указанием стиля:")
    for para in doc.paragraphs:
        st.write(f"[{para.style.name}] {para.text}")
