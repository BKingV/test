import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование по темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_themes_and_questions(doc):
    """Извлекает темы, подтемы и вопросы, начиная обработку с первой темы, после которой идет таблица"""
    themes = {}

    st.write("📌 Количество таблиц в документе:", len(doc.tables))  # Проверяем количество таблиц

    # Получаем первую тему в документе
    current_theme = None
    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith("ТЕМА:"):  
            current_theme = text.replace("ТЕМА:", "").strip()
            break  # Берём только первую найденную тему

    # Если темы нет, используем "Неизвестная тема"
    if not current_theme:
        current_theme = "Неизвестная тема"

    st.write("📌 Найденная тема:", current_theme)  # Выводим тему для отладки

    # Берем последнюю таблицу, так как в ней находятся подтемы и вопросы
    table = doc.tables[-1]

    # Выводим каждую строку таблицы для проверки
    for i, row in enumerate(table.rows):
        row_data = [cell.text.strip() for cell in row.cells]
        st.write(f"📌 Строка {i}:", row_data)  

    current_subtheme = None  # Переменная для хранения текущей подтемы

    for row in table.rows[2:]:  # Пропускаем заголовок
        row_data = [cell.text.strip() for cell in row.cells]

        # Проверяем, является ли строка заголовком (подтемой)
        if len(set(row_data)) == 1 and row_data[0]:  # Если во всей строке один и тот же текст
            current_subtheme = row_data[0]
            continue  # Пропускаем строку, не добавляя её в вопросы

        # Проверяем, содержит ли строка вопрос (не пустая и не заголовок)
        if len(row_data) >= 2 and row_data[1] and row_data[2]:  
            question_text = row_data[1]
            answer_text = row_data[2]
            correct_text = row_data[3] if len(row_data) > 3 else ""

            # Добавляем вопрос в список
            question_data = {
                "question": question_text,
                "answers": [],
                "correct": [],
                "subtheme": current_subtheme
            }
            themes.setdefault(current_theme, []).append(question_data)

            # Добавляем варианты ответов
            themes[current_theme][-1]["answers"].append(answer_text)
            if correct_text:
                themes[current_theme][-1]["correct"].append(answer_text)

    st.write("📌 Итоговая структура данных:", themes)  # Проверяем, загружаются ли вопросы

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

                # Если выбрана подтема – берем только её вопросы
                if selected_subtheme:
                    st.session_state["questions"] = [q for q in st.session_state["themes"][selected_theme] if q["subtheme"] == selected_subtheme]
                else:
                    st.session_state["questions"] = st.session_state["themes"][selected_theme]  # Берем все вопросы темы

                st.session_state["current_question"] = 0
                st.session_state["test_started"] = True
                st.session_state["show_result"] = False
                st.session_state["selected_answers"] = {}
                st.rerun()
