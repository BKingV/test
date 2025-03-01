import streamlit as st
import pandas as pd
from docx import Document
import io

def extract_questions_from_docx(file):
    doc = Document(file)
    data = []
    
    for table in doc.tables:
        rows = table.rows
        if len(rows) < 2:
            continue  # Пропускаем слишком маленькие таблицы
        
        question = ""
        answers = []
        correct_answers = []
        
        for row in rows[1:]:  # Пропускаем заголовок
            cells = row.cells
            
            if len(cells) >= 3:
                if cells[0].text.strip():
                    if question:
                        data.append([question, answers, correct_answers])
                    
                    question = cells[1].text.strip()
                    answers = []
                    correct_answers = []
                
                answer = cells[2].text.strip()
                answers.append(answer)
                if len(cells) > 3 and 'Эталон' in cells[3].text.strip():
                    correct_answers.append(answer)
        
        if question:
            data.append([question, answers, correct_answers])
    
    return data

def run_test(questions):
    st.subheader("Тестирование")
    score = 0
    total = len(questions)
    user_answers = {}
    
    for i, (question, answers, correct_answers) in enumerate(questions):
        st.write(f"**{i+1}. {question}**")
        selected = st.radio("Выберите ответ:", answers, key=f"q_{i}")
        user_answers[question] = selected
        
        if selected in correct_answers:
            score += 1
    
    if st.button("Завершить тест"):  
        st.write(f"Вы правильно ответили на {score} из {total} вопросов!")
        st.write("## Ваши ответы:")
        for question, selected in user_answers.items():
            st.write(f"{question}: {selected}")

st.title("Тестирование из Word")
uploaded_file = st.file_uploader("Загрузите файл .docx", type=["docx"])

if uploaded_file:
    questions = extract_questions_from_docx(uploaded_file)
    if questions:
        run_test(questions)
    else:
        st.error("Не удалось извлечь вопросы. Проверьте формат таблицы в файле.")
