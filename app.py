import streamlit as st
from docx import Document

st.title("📄 Проверка структуры файла")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)

    # Выводим весь текст документа
    st.subheader("📜 Весь текст из файла:")
    for para in doc.paragraphs:
        st.write(f"➡️ {para.text}")  # Выведем каждую строку
