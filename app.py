import streamlit as st
from docx import Document
import pandas as pd
import re
import io

def extract_questions_from_docx(docx_content):
    # Чтение Word-документа из загруженного контента
    doc = Document(io.BytesIO(docx_content))
    data = []

    current_block = ""
    current_topic = ""

    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]

    for i in range(len(paragraphs)):
        text = paragraphs[i]

        if text.isupper() and "БЛОК" in text:
            current_block = text
            current_topic = ""
            continue

        if text.startswith("ТЕМА:"):
            current_topic = text.replace("ТЕМА:", "").strip()
            continue

        if re.match(r"^\d+[\.)]", text):
            question_text = re.sub(r"^\d+[\.)]\s*", "", text)
            options = []
            correct_answers = []

            j = i + 1
            while j < len(paragraphs) - 1:
                option_text = paragraphs[j]
                next_text = paragraphs[j + 1]

                if re.match(r"^\d+[\.)]", option_text) or option_text.startswith("ТЕМА:") or "БЛОК" in option_text:
                    break

                if "Эталон" in next_text:
                    correct_answers.append(option_text)

                options.append(option_text)
                j += 2

            options_text = ";".join(options)
            correct_answers_text = ";".join(correct_answers)
            data.append([current_block, current_topic, question_text, options, correct_answers])

    return pd.DataFrame(data, columns=["Блок", "Тема", "Вопрос", "Варианты ответов", "Эталон"])

def main():
    st.title("Тестирование из Word-файла")
    
    uploaded_file = st.file_uploader("Загрузите файл Word", type="docx")
    
    if uploaded_file is not None:
        docx_content = uploaded_file.read()
        df = extract_questions_from_docx(docx_content)
        
        st.write("Извлеченные данные:")
        st.dataframe(df)
        
        if not df.empty:
            st.subheader("Начнем тестирование!")
            score = 0
            total_questions = len(df)

            for index, row in df.iterrows():
                st.write(f"**{row['Вопрос']}**")
                answers = row['Варианты ответов']
                correct_answers = row['Эталон']
                
                # Getting user response
                selected_option = st.radio("Выберите вариант:", options=answers)

                # Check if the selected option is among the correct ones
                if selected_option in correct_answers:
                    score += 1
            
            # Show results
            st.write("### Результаты")
            st.write(f"Вы правильно ответили на {score} из {total_questions} вопросов.")

if __name__ == "__main__":
    main()
