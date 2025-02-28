import pandas as pd
import streamlit as st
import openpyxl  # Убедимся, что библиотека установлена и импортирована

def load_questions_from_excel(file):
    """Загружает вопросы из файла Excel и структурирует данные, начиная с ячейки с '№ п/п'."""
    df = pd.read_excel(file, sheet_name=None, engine="openpyxl")  # Указываем движок для работы с .xlsx
    questions = []

    for sheet_name, data in df.items():
        # Пропускаем текст до столбца "№ п/п"
        if "№ п/п" not in data.columns:
            continue  # Если нет столбца "№ п/п", переходим к следующему листу

        # Читаем только те строки, которые содержат данные
        for _, row in data.iterrows():
            if pd.notna(row["№ п/п"]):  # Если в строке есть номер вопроса
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

        # Группируем вопросы по темам
        topics = list(set(q['topic'] for q in block_questions))
        topic_dict = {topic: [q for q in block_questions if q['topic'] == topic] for topic in topics}

        score = 0
        for block in topic_dict:
            st.write(f"### Блок: {block}")
            
            for topic in topic_dict[block]:
                st.write(f"**Тема: {topic['topic']}**")
                topic_questions = [q for q in topic_dict[block] if q['topic'] == topic['topic']]

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
