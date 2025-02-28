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

        # Заполнение объединенных ячеек значением
        data = data.ffill(axis=0)  # Заполняем пустые ячейки значением из предыдущих строк

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
                "question": row.iloc[2] if pd.notna(row.iloc[2]) else "Вопрос не указан",  
                "options": str(row.iloc[3]).split(";") if pd.notna(row.iloc[3]) else [],  
                "correct_answers": str(row.iloc[4]).split(";") if pd.notna(row.iloc[4]) else []  
            })

    st.write(f"✅ Загружено {len(questions)} вопросов!")
    return questions

def main():
    """Основная логика работы теста."""
    st.title("📝 Тренажер для подготовки к тесту")
    uploaded_file = st.file_uploader("📂 Загрузите файл Excel с вопросами", type=["xlsx", "xls"])

    if uploaded_file:
        with st.spinner("⏳ Загружаем вопросы..."):
            questions = load_questions_from_excel(uploaded_file)

        if not questions:
            st.error("❌ Ошибка: вопросы не загружены.")
            return

        blocks = list(set(q['block'] for q in questions))
        selected_block = st.selectbox("Выберите блок", blocks)
        block_questions = [q for q in questions if q['block'] == selected_block]

        topics = list(set(q['topic'] for q in block_questions))
        topic_dict = {topic: [q for q in block_questions if q['topic'] == topic] for topic in topics}

        score = 0
        for topic, topic_questions in topic_dict.items():
            st.write(f"### Тема: {topic}")

            for idx, q in enumerate(topic_questions):
                st.write(f"**{q['number']} {q['question']}**")
                selected_option = st.radio("Выберите ответ:", q['options'], key=f"q_{idx}", index=None)

                if st.button(f"Проверить {q['number']}", key=f"check_{idx}"):
                    if selected_option and selected_option in q['correct_answers']:
                        st.success("✅ Правильно!")
                        score += 1
                    elif selected_option:
                        st.error(f"❌ Неправильно. Правильный ответ: {', '.join(q['correct_answers'])}")
                    else:
                        st.warning("⚠️ Выберите вариант ответа перед проверкой.")

        st.write(f"🏆 Тест завершен!
