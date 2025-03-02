import streamlit as st
import pandas as pd
from docx import Document
import re

st.title("📄 Онлайн-тестирование из Word-файла")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_questions_from_docx(doc):
    """Извлекает вопросы и варианты ответов из Word-файла."""
    questions = []
    current_question = None
    answers = []

    question_pattern = re.compile(r"^\d+[\.\)]|\b[№]\s*\d+")  # Ищем номера вопросов (1., 2), (№ 1, №2)

    for para in doc.paragraphs:
        text = para.text.strip()
        
        if question_pattern.match(text) or text.endswith("?"):
            # Новый вопрос найден
            if current_question:
                questions.append({"question": current_question, "answers": answers})
            current_question = text
            answers = []
        elif text and current_question:
            answers.append(text)
    
    if current_question and answers:
        questions.append({"question": current_question, "answers": answers})

    return questions

if uploaded_file:
    doc = Document(uploaded_file)
    questions = extract_questions_from_docx(doc)

    if not questions:
        st.warning("Не удалось извлечь вопросы. Проверьте формат документа.")
    else:
        st.session_state["questions"] = questions
        st.success(f"Найдено {len(questions)} вопросов. Можно начинать тест!")
        if st.button("Начать тест"):
            st.session_state["current_question"] = 0
            st.session_state["score"] = 0
            st.rerun()

# Отображение теста
if "questions" in st.session_state and "current_question" in st.session_state:
    q_idx = st.session_state["current_question"]
    question_data = st.session_state["questions"][q_idx]

    st.subheader(question_data["question"])
    selected_answer = st.radio("Выберите ответ:", question_data["answers"])

    if st.button("Ответить"):
        # Переход к следующему вопросу
        if q_idx + 1 < len(st.session_state["questions"]):
            st.session_state["current_question"] += 1
            st.rerun()
        else:
            st.success("Тест завершен!")
            st.write(f"Вы ответили на {len(st.session_state['questions'])} вопросов.")
