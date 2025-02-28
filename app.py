import pandas as pd
import streamlit as st
import openpyxl

@st.cache_data
def load_questions_from_excel(file):
    """Загружает вопросы из Excel, начиная с первой ячейки в столбце A, равной 1."""
    st.write("📂 Читаем файл Excel...")
    df = pd.read_excel(file, sheet_name=None, engine="openpyxl")  
    questions = []

    # Проходим по всем листам Excel
    for sheet_name, data in df.items():
        st.write(f"🔍 Обрабатываем лист: {sheet_name}")

        # Ищем строку, где в первом столбце есть "1"
        start_row = None
        for i, value in enumerate(data.iloc[:, 0]):  
            if pd.notna(value) and str(value).strip() == "1":
                start_row = i
                break  

        if start_row is None:
            st.warning(f"⚠️ Лист '{sheet_name}' пропущен (не найдено значение '1' в первой колонке).")
            continue  

        # Обрезаем данные, чтобы заголовки были из первой строки после "1"
        data = data.iloc[start_row:].reset_index(drop=True)
        data.columns = data.iloc[0]  # Делаем первую строку заголовками
        data = data[1:].reset_index(drop=True)  

        # Заменяем NaN значения на пустую строку
        data = data.fillna("")  # Заполняем пустые ячейки пустыми строками

        # Убираем строки, в которых все столбцы пустые
        data = data.dropna(how='all')

        # Проверяем структуру данных
        st.write(f"📊 Структура данных на листе '{sheet_name}':")
        st.write(data.head())

        # Перебираем строки и загружаем вопросы
        for _, row in data.iterrows():
            # Проверяем, хватает ли колонок
            if len(row) < 5:
                st.warning(f"⚠️ В строке пропущены некоторые данные: {row}")
                continue  

            number = str(row.iloc[0]).strip()  # Номер вопроса
            if not number.endswith("."):
                number += "."  

            questions.append({
                "block": sheet_name,  
                "topic": row.iloc[1] if pd.notna(row.iloc[1]) else "Без темы",  
                "number": number,  
                "question": row.iloc[2] if pd.notna(r
