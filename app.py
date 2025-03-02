import streamlit as st
from docx import Document

st.title("📋 Проверка структуры файла")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)

    # Вывод содержимого таблиц
    st.subheader("📋 Таблицы в документе:")
    for table_idx, table in enumerate(doc.tables):
        st.write(f"🔹 Таблица {table_idx + 1}:")
        for row in table.rows:
            st.write([cell.text for cell in row.cells])  # Вывод строк таблицы
