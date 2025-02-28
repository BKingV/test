import pandas as pd
import streamlit as st
import openpyxl  # Убедимся, что библиотека установлена и импортирована

@st.cache_data
def load_questions_from_excel(file):
    """Загружает вопросы из Excel, начиная с первой ячейки в столбце A, равной 1."""
    st.write("📂 Читаем файл Excel...")
    df = pd.read_excel(file, sheet_name=None, engine="openpyxl")  # Загружаем все листы
    questions = []

    for sheet_name, data in df.items():
        st.write(f"🔍 Обрабатываем лист: {sheet_name}")

        # Ищем строку, где в столбце A есть "1"
        start_row = None
        for i, value in enumerate(data.iloc[:, 0]):  
            if pd.notna(value) and str(value).strip() == "1":
                start_row = i
                break  

        if start_row is None:
            st.warning(f"⚠️ Лист '{sheet_name}' пропущен (не найдено значение '1' в первой колонке).")
            continue  

        # Обрезаем данные
        data = data.iloc[start_row:].reset_index(drop=True)
        data.columns = data.iloc[0]  # Делаем первую строку заголовком
        data = data[1:].reset_index(drop=True)  

        required_columns = ["№ п/п", "Тема", "Текст вопроса", "Варианты ответа", "Эталон"]
        if not all(col in data.columns for col in required_columns):
            st.error(f"❌ Ошибка: На листе '{sheet_name}' не хватает нужных столбцов! Пропускаем.")
            continue

        # Читаем данные
        for _, row in data.iterrows():
            number = str(row["№ п/п"]).strip()
            if not number.endswith("."):
                number += "."  # Добавляем точку, если её нет

            questions.append({
                "block": sheet_name,  
                "topic": row["Тема"],  
                "number": number,  
                "question": row["Текст вопроса"],  
                "options": str(row["Варианты ответа"]).split(";"),  
                "correct_answers": str(row["Эталон"]).split(";")  
            })

    st.write(f"✅ Загружено {len(questions)} вопросов!")
    return questions

def main():
    """Основная логика работы теста."""
    st.title("📝 Тренажер для подготовки к тесту")
    uploaded_file = st.file_uploader("📂 Загрузите файл Excel с вопросами", type=["xlsx", "xls"])

    if uploaded_file:
        with st.spinn
