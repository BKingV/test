import pandas as pd
import streamlit as st
import openpyxl  # Убедимся, что библиотека установлена и импортирована

def load_questions_from_excel(file):
    """Загружает вопросы из Excel, начиная с первой ячейки в столбце A, равной 1."""
    df = pd.read_excel(file, sheet_name=None, engine="openpyxl")  # Загружаем все листы
    questions = []

    for sheet_name, data in df.items():
        st.write(f"🔍 Обрабатываем лист: {sheet_name}")  # Для отладки выводим имя листа

        # Ищем строку, в которой в первой колонке (A) есть число 1
        start_row = None
        for i, value in enumerate(data.iloc[:, 0]):  # Перебираем первый столбец (A)
            if pd.notna(value) and str(value).strip() == "1":
                start_row = i
                break  # Нашли начало теста

        if start_row is None:
            st.warning(f"⚠️ На листе '{sheet_name}' не найдено начало теста (значение '1' в первом столбце). Пропускаем.")
            continue  # Если не нашли начало теста, пропускаем лист

        # Загружаем вопросы, начиная с найденной строки
        data = data.iloc[start_row:]  # Обрезаем все строки до начала теста
        data.columns = data.iloc[0]  # Устанавливаем первую строку в качестве заголовков
        data = data[1:].reset_index(drop=True)  # Удаляем строку-заголовок из данных

        # Проверяем, содержатся ли нужные столбцы
        required_columns = ["№ п/п", "Тема", "Текст вопроса", "Варианты ответа", "Эталон"]
        if not all(col in data.columns for col in required_columns):
            st.error(f"❌ Ошибка: На листе '{sheet_name}' не хватает нужных столбцов! Пропускаем.")
            continue

        # Читаем данные и формируем список вопросов
        for _, row in data.iterrows():
            questions.append({
                "block": sheet_name,  # Название блока (лист)
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

        # Группируем вопросы по темам
        topics = list(set(q['topic'] for q in block_questions))
        topic_dict = {topic: [q for q in block_questions if q['topic'] == topic] for topic in topics}

        score = 0
        for topic, topic_questions in topic_dict.items():
            st.write(f"### Тема: {topic}")

            for idx, q in enumerate(topic_questions):
                st.write(f"**{q['number']}. {q['question']}**")
                selected_option = st.radio("Выберите ответ:", q['options'], key=f"q_{idx}", index=None)

                if st.button(f"Проверить {q['number']}", key=f"check_{idx}"):
                    if selected_option and selected_option in q['correct_answers']:
                        st.success("✅ Правильно!")
                        score += 1
                    elif selected_option:
                        st.error(f"❌ Неправильно. Правильный ответ: {', '.join(q['correct_answers'])}")
                    else:
                        st.warning("⚠️ Выберите вариант ответа перед проверкой.")

        st.write(f"🏆 Тест завершен! Ваш результат: {score}/{len(questions)}")

if __name__ == "__main__":
    main()
