import streamlit as st
import pandas as pd
from docx import Document

st.title("📄 Онлайн-тестирование по темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_themes_and_questions(doc):
    """Извлекает темы, подтемы и вопросы, начиная обработку только с первой темы, после которой идет таблица"""
    themes = {}

    st.write("📌 Количество таблиц в документе:", len(doc.tables))  # Проверяем количество таблиц

    # Берем последнюю таблицу, так как в ней находятся подтемы
    table = doc.tables[-1]

    st.write("📌 Содержимое последней таблицы:", [[cell.text for cell in row.cells] for row in table.rows])

    current_subtheme = None  # Переменная для хранения текущей подтемы

    for row in table.rows[1:]:
        first_cell_text = row.cells[0].text.strip()  # Первый столбец
        question_text = row.cells[1].text.strip()  # Вопрос
        answer_text = row.cells[2].text.strip()  # Вариант ответа
        correct_text = row.cells[3].text.strip() if len(row.cells) > 3 else ""  # Правильный ответ

        # Если строка содержит заголовок (подтему), обновляем current_subtheme
        if first_cell_text and all(cell.text.strip() == first_cell_text for cell in row.cells):
            current_subtheme = first_cell_text  # Сохраняем новую подтему
            continue  # Пропускаем строку, не добавляя её в вопросы

        # Если строка содержит вопрос, добавляем его с подтемой
        if question_text:
            question_data = {
                "question": question_text,
                "answers": [],
                "correct": [],
                "subtheme": current_subtheme  # Привязываем вопрос к текущей подтеме
            }
            themes.setdefault("Тема", []).append(question_data)

        # Добавляем варианты ответов
        if themes["Тема"] and "question" in themes["Тема"][-1]:
            themes["Тема"][-1]["answers"].append(answer_text)
            if correct_text:
                themes["Тема"][-1]["correct"].append(answer_text)

    return themes

if uploaded_file:
    doc = Document(uploaded_file)
    themes = extract_themes_and_questions(doc)

    if not themes:
        st.warning("⚠️ Не удалось извлечь темы и вопросы. Проверьте формат документа.")
    else:
        if "themes" not in st.session_state:
            st.session_state["themes"] = themes
            st.session_state["selected_theme"] = None
            st.session_state["selected_subtheme"] = None
            st.session_state["questions"] = []
            st.session_state["current_question"] = 0
            st.session_state["test_started"] = False
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {}

        if not st.session_state.get("test_started", False):
            st.subheader("📚 Выберите тему:")
            selected_theme = st.selectbox("Выберите тему", list(st.session_state["themes"].keys()), key="theme_select")

            # Получаем список подтем (уникальные заголовки)
            subthemes = list(set(q["subtheme"] for q in st.session_state["themes"][selected_theme] if q["subtheme"]))

            selected_subtheme = None
            if subthemes:
                st.subheader("📂 Выберите подтему:")
                selected_subtheme = st.selectbox("Выберите подтему", subthemes, key="subtheme_select")

            # Кнопка "Начать тест" теперь ниже
            if st.button("▶️ Начать тест"):
                st.session_state["selected_theme"] = selected_theme
                st.session_state["selected_subtheme"] = selected_subtheme

                # Если выбрана подтема – берем только ее вопросы
                if selected_subtheme:
                    st.session_state["questions"] = [q for q in st.session_state["themes"][selected_theme] if q["subtheme"] == selected_subtheme]
                else:
                    st.session_state["questions"] = st.session_state["themes"][selected_theme]  # Берем все вопросы темы

                st.session_state["current_question"] = 0
                st.session_state["test_started"] = True
                st.session_state["show_result"] = False
                st.session_state["selected_answers"] = {}
                st.rerun()
