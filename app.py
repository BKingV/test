import streamlit as st
import pandas as pd
from docx import Document
import io

def extract_questions_from_docx(file):
    doc = Document(file)
    data = []
    block = ""
    theme = ""
    
    for table in doc.tables:
        rows = table.rows
        if len(rows) < 2:
            continue  # Пропускаем слишком маленькие таблицы
        
        question = ""
        answers = []
        correct_answers = []
        
        for row in rows[1:]:  # Пропускаем заголовок
            cells = row.cells
            
            if len(cells) >= 4:
                if cells[0].text.strip():  # Новый вопрос
                    if question:
                        data.append([block, theme, question, " | ".join(answers), " | ".join(correct_answers)])
                    
                    question = cells[1].text.strip()
                    answers = []
                    correct_answers = []
                
                answer = cells[2].text.strip()
                answers.append(answer)
                if 'Эталон' in cells[3].text.strip():
                    correct_answers.append(answer)
        
        if question:
            data.append([block, theme, question, " | ".join(answers), " | ".join(correct_answers)])
    
    return pd.DataFrame(data, columns=["Блок", "Тема", "Вопрос", "Варианты ответов", "Правильные ответы"])

st.title("Извлечение вопросов из Word")
uploaded_file = st.file_uploader("Загрузите файл .docx", type=["docx"])

if uploaded_file:
    df = extract_questions_from_docx(uploaded_file)
    st.write("### Извлечённые вопросы:")
    st.dataframe(df)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name="Тест")
        writer.close()
    output.seek(0)
    
    st.download_button("Скачать Excel", data=output, file_name="test_questions.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
