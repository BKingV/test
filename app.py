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
            data.append([current_block, current_topic, question_text, options_text, correct_answers_text])

    return pd.DataFrame(data, columns=["Блок", "Тема", "Вопрос", "Варианты ответов", "Эталон"])

def main():
    st.title("Конвертер тестов из Word в Excel")
    st.write("Загрузите файл Word, чтобы извлечь блоки, темы и вопросы")

    # Разрешаем пользователю загрузить файл
    uploaded_file = st.file_uploader("Выберите файл Word", type="docx")

    if uploaded_file is not None:
        # Обрабатываем файл
        df = extract_questions_from_docx(uploaded_file.read())
        
        st.write("Извлеченные данные:")
        st.dataframe(df)

        # Сохранение в Excel
        excel_io = io.BytesIO()
        with pd.ExcelWriter(excel_io, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Тесты')
        excel_io.seek(0)

        # Предоставляем ссылку для скачивания эксель файла
        st.download_button(
            label="Скачать как Excel",
            data=excel_io,
            file_name="questions.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == "__main__":
    main()
