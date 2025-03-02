import streamlit as st
import pandas as pd
import docx

# Функция для извлечения вопросов из Word-файла
def extract_questions_from_docx(file):
    doc = docx.Document(file)
    questions = []
    current_question = None
    current_options = []
    correct_answers = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith("ТЕМА:"):  # Начало новой темы
            continue
        elif text and not text.startswith("№"):  # Если это новый вопрос
            if current_question:
                questions.append((current_question, current_options, correct_answers))
            current_question = text
            current_options = []
            correct_answers = []
        elif text.startswith("Эталон"):  # Помечаем правильный ответ
            if current_options:
                correct_answers.append(current_options[-1])
        elif text:  # Варианты ответов
            current_options.append(text)

    if current_question:
        questions.append((current_question, current_options, correct_answers))
    
    return questions

# Интерфейс Streamlit
st.title("📄 Онлайн тестирование из Word-файла")

# Загрузка файла
uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

if uploaded_file:
    st.success("Файл загружен успешно! Извлекаем вопросы...")
    questions = extract_questions_from_docx(uploaded_file)
    
    if questions:
        st.subheader("📋 Пройдите тест")

        user_answers = {}  # Словарь для хранения ответов пользователя

        for i, (question, options, correct) in enumerate(questions):
            user_choice = st.radio(question, options, key=f"q{i}")
            user_answers[i] = (question, user_choice, correct)

        if st.button("✅ Завершить тест"):
            correct_count = sum(1 for ans in user_answers.values() if ans[1] in ans[2])
            total_questions = len(questions)
            st.success(f"🎉 Тест завершен! Ваш результат: {correct_count} из {total_questions}.")

            # Создаем таблицу с результатами
            results_data = []
            for q_num, (question, user_choice, correct_answers) in user_answers.items():
                is_correct = "✅" if user_choice in correct_answers else "❌"
                results_data.append([question, user_choice, ", ".join(correct_answers), is_correct])

            df_results = pd.DataFrame(results_data, columns=["Вопрос", "Ваш ответ", "Правильный ответ", "Результат"])
            st.dataframe(df_results)  # Отображаем таблицу с результатами

            # Кнопка перезапуска теста
            if st.button("🔄 Пройти еще раз"):
                st.experimental_rerun()
    else:
        st.error("Не удалось извлечь вопросы из файла. Убедитесь, что формат правильный.")
