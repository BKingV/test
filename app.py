import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование по темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_themes_and_questions(doc):
    """Извлекает темы, подтемы и вопросы из таблицы документа Word."""
    themes = {}

    st.write("📌 Количество таблиц в документе:", len(doc.tables))  # Проверка количества таблиц

    # Получаем первую тему из документа
    current_theme = None
    for para in doc.paragraphs:
        text = para.text.strip()
        if text.startswith("ТЕМА:"):  
            current_theme = text.replace("ТЕМА:", "").strip()
            break  # Берём только первую найденную тему

    if not current_theme:
        current_theme = "Неизвестная тема"

    st.write("📌 Найденная тема:", current_theme)  # Вывод темы для отладки

    # Берем последнюю таблицу (где подтемы и вопросы)
    table = doc.tables[-1]

    # Вывод содержимого таблицы для диагностики
    for i, row in enumerate(table.rows):
        row_data = [cell.text.strip() for cell in row.cells]
        st.write(f"📌 Строка {i}:", row_data)

    current_subtheme = None  # Хранение текущей подтемы

    for row in table.rows[2:]:  # Пропускаем заголовок таблицы
        row_data = [cell.text.strip() for cell in row.cells]

        # Если строка содержит одинаковый текст во всех колонках — это подтема!
        if len(set(row_data)) == 1 and row_data[0]:  
            current_subtheme = row_data[0]
            continue  # Не добавляем подтему в вопросы

        # Проверяем, является ли строка вопросом (должны быть текст вопроса и варианты ответа)
        if len(row_data) >= 3 and row_data[1] and row_data[2]:  
            question_text = row_data[1]
            answer_text = row_data[2]
            correct_text = row_data[3] if len(row_data) > 3 else ""

            # Добавляем вопрос в список
            question_data = {
                "question": question_text,
                "answers": [answer_text],
                "correct": [answer_text] if correct_text else [],
                "subtheme": current_subtheme  # Привязываем к подтеме
            }
            themes.setdefault(current_theme, []).append(question_data)

    st.write("📌 Итоговая структура данных:", themes)  # Проверка структуры данных

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

            # Кнопка "Начать тест"
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
