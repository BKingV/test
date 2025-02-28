import pandas as pd
import streamlit as st
import openpyxl  # Убедимся, что библиотека установлена и импортирована

def load_questions_from_excel(file):
    """Загружает вопросы из файла Excel и структурирует данные."""
    df = pd.read_excel(file, sheet_name=None, engine="openpyxl")  # Указываем движок для работы с .xlsx
    questions = []
    
    for sheet_name, data in df.items():
        print(f"Заголовки колонок в листе '{sheet_name}':", data.columns)  # Выводим заголовки для отладки
        
        if "№ п/п" not in data.columns:
            raise ValueError('Столбец "№ п/п" не найден в одном из листов Excel!')
        
        for _, row in data.iterrows():
            if pd.notna(row["№ п/п"]):
                questions.append({
                    "block": sheet_name,  # Название блока
                    "topic": row["Тема"],  # Название темы
                    "number": row["№ п/п"],  # Номер вопроса
                    "question": row["Текст вопроса"],  # Текст вопроса
                    "options": str(row["Варианты ответа"]).split(";"),  # Разделяем варианты ответа
                    "correct_answers": str(row["Эталон"]).split(";")  # Разделяем правильные ответы
                })
    return questions

def main():
    """Основная логика работы теста."""
    st.title("📝 Тренажер для подготовки к тесту")
    uploaded_file = st.file_uploader("📂 Загрузите файл Excel с вопросами", type=["xlsx", "xls"])
    
    if uploaded_file:
        questions = load_questions_from_excel(uploaded_file)
        if not questions:
            st.error("❌ Ошибка: вопросы не загружены.")
            return
        
        blocks = list(set(q['block'] for q in questions))
        selected_block = st.selectbox("Выберите блок", blocks)
        block_questions = [q for q in questions if q['block'] == selected_block]
        
        topics = list(set(q['topic'] for q in block_questions))
        selected_topic = st.selectbox("
