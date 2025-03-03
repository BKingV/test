import streamlit as st
import json

# Загружаем вопросы из JSON-файла
with open("full_test_questions.json", "r", encoding="utf-8") as file:
    questions_data = json.load(file)

# Заголовок приложения
st.title("Тестирование по темам")

# 1️⃣ Выбор темы тестирования
selected_topic = st.selectbox("Выберите тему теста:", list(questions_data.keys()))

if selected_topic:
    st.write(f"Вы выбрали тему: **{selected_topic}**")

    # 2️⃣ Получаем вопросы по выбранной теме
    questions = questions_data[selected_topic]

    # Словарь для хранения ответов пользователя
    user_answers = {}

    # 3️⃣ Выводим вопросы и варианты ответов
    for i, question in enumerate(questions):
        st.subheader(f"Вопрос {i+1}: {question['question']}")
        user_answers[i] = st.radio("Выберите ответ:", question["options"], key=i)

    # 4️⃣ Кнопка "Проверить результаты"
    if st.button("Проверить результаты"):
        correct_count = sum(
            1 for i, question in enumerate(questions) if user_answers[i] == question["answer"]
        )

        total_questions = len(questions)
        st.success(f"Вы ответили правильно на {correct_count} из {total_questions} вопросов!")

        # 5️⃣ Показываем правильные ответы
        st.subheader("Правильные ответы:")
        for i, question in enumerate(questions):
            st.write(f"**{i+1}. {question['question']}**")
            st.write(f"✅ Правильный ответ: **{question['answer']}**")
            st.write("---")
