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
                        data.append([question, " | ".join(answers), " | ".join(correct_answers)])
                    
                    question = cells[1].text.strip()
                    answers = []
                    correct_answers = []
                
                answer = cells[2].text.strip()
                answers.append(answer)
                if len(cells) > 3 and 'Эталон' in cells[3].text.strip():
                    correct_answers.append(answer)
        
        if question:
            data.append([question, " | ".join(answers), " | ".join(correct_answers)])
    
    return pd.DataFrame(data, columns=["Вопрос", "Варианты ответов", "Правильные ответы"])

def run_test(questions):
    st.subheader("Тестирование")
    score = 0
    total = len(questions)
    user_answers = {}
    
    for i, (question, answers, correct_answers) in questions.iterrows():
        st.write(f"**{i+1}. {question}**")
        selected = st.radio("Выберите ответ:", answers.split(" | "), key=f"q_{i}")
        user_answers[question] = selected
        
        if selected in correct_answers.split(" | "):
            score += 1
    
    if st.button("Завершить тест"):  
        st.write(f"Вы правильно ответили на {score} из {total} вопросов!")
        st.write("## Ваши ответы:")
        for question, selected in user_answers.items():
            st.write(f"{question}: {selected}")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        questions.to_excel(writer, index=False, sheet_name="Результаты теста")
        writer.close()
    output.seek(0)
    
    st.download_button("Скачать результаты теста", data=output, file_name="test_results.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.title("Тестирование из Word")
uploaded_file = st.file_uploader("Загрузите файл .docx", type=["docx"])

if uploaded_file:
    questions = extract_questions_from_docx(uploaded_file)
    if not questions.empty:
        run_test(questions)
    else:
        st.error("Не удалось извлечь вопросы. Проверьте формат таблицы в файле.")
