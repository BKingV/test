import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование по темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_themes_and_questions(doc):
    """Извлекает темы и вопросы, начиная обработку только с первой темы, за которой идет таблица"""
    themes = {}
    current_theme = None
    processing_started = False  # Флаг, который говорит, что можно начинать обработку

    paragraphs = [para.text.strip() for para in doc.paragraphs if para.text.strip()]  # Убираем пустые строки
    tables = iter(doc.tables)  # Создаем итератор по таблицам

    for text in paragraphs:
        if text.startswith("ТЕМА:"):  
            current_theme = text.replace("ТЕМА:", "").strip()

            try:
                # Проверяем, есть ли таблица сразу после темы
                table = next(tables)  
                themes[current_theme] = []

                rows = table.rows
                if len(rows) < 2:
                    continue  # Пропускаем пустые таблицы

                headers = [cell.text.strip().lower() for cell in rows[0].cells]
                if "текст вопроса" not in headers or "варианты ответов" not in headers:
                    continue  # Пропускаем таблицы без заголовков

                question_idx = headers.index("текст вопроса")
                answers_idx = headers.index("варианты ответов")
                correct_idx = headers.index("эталон") if "эталон" in headers else None

                for row in rows[1:]:  # Пропускаем заголовки
                    question_text = row.cells[question_idx].text.strip()
                    answer_text = row.cells[answers_idx].text.strip()
                    correct_text = row.cells[correct_idx].text.strip() if correct_idx else ""

                    themes[current_theme].append({
                        "question": question_text,
                        "answers": answer_text.split("\n"),  # Разделяем ответы по строкам
                        "correct": correct_text.split("\n")  # Разделяем правильные ответы
                    })

                processing_started = True  # Теперь можно обрабатывать темы

            except StopIteration:
                continue  # Если после темы нет таблицы, продолжаем искать дальше

    if not processing_started:
        st.warning("⚠️ В файле не найдены темы с таблицами. Проверьте формат документа.")

    return themes

if uploaded_file:
    doc = Document(uploaded_file)
    themes = extract_themes_and_questions(doc)

    if not themes:
        st.warning("Не удалось извлечь темы и вопросы. Проверьте формат документа.")
    else:
        if "themes" not in st.session_state:
            st.session_state["themes"] = themes
            st.session_state["selected_theme"] = None
            st.session_state["questions"] = []
            st.session_state["current_question"] = 0
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {}

        # Выбор темы
        st.header("Выберите тему")
        theme = st.selectbox("Тема:", list(themes.keys()), index=0 if not st.session_state["selected_theme"] else list(themes.keys()).index(st.session_state["selected_theme"]))

        if theme:
            st.session_state["selected_theme"] = theme

            # Проверяем, есть ли вопросы в теме
            if len(themes[theme]) > 0:
                st.session_state["questions"] = themes[theme]
                st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}

                if st.button("Начать тест"):
                    st.session_state["current_question"] = 0
                    st.session_state["show_result"] = False
                    st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}
                    st.rerun()
            else:
                st.warning("⚠️ В этой теме пока нет вопросов. Проверьте, правильно ли заголовки идут перед таблицами.")
