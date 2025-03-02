import streamlit as st
import pandas as pd
from docx import Document

st.title("📄 Онлайн-тестирование по темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_themes_and_questions(doc):
    """Извлекает темы и вопросы, начиная обработку только с первой темы, после которой идет таблица"""
    themes = {}
    tables_iter = iter(doc.tables)

    for para in doc.paragraphs:
        text = para.text.strip()

        if text.startswith("ТЕМА:"):
            current_theme = text.replace("ТЕМА:", "").strip()
            themes[current_theme] = []

            try:
                table = next(tables_iter)
                headers = [cell.text.strip().lower() for cell in table.rows[0].cells]
                if "текст вопроса" not in headers or "варианты ответов" not in headers:
                    continue  

                question_idx = headers.index("текст вопроса")
                answers_idx = headers.index("варианты ответов")
                correct_idx = headers.index("эталон") if "эталон" in headers else None

                current_subtheme = None  # Для хранения подтемы

                for row in table.rows[1:]:
                    first_cell_text = row.cells[0].text.strip()
                    question_text = row.cells[question_idx].text.strip()
                    answer_text = row.cells[answers_idx].text.strip()
                    correct_text = row.cells[correct_idx].text.strip() if correct_idx else ""

                    # Проверяем, является ли строка подзаголовком (например, "Общие вопросы")
                    if first_cell_text and not question_text:
                        current_subtheme = first_cell_text
                        continue

                    # Если встречается вопрос, добавляем его в тему и подтему
                    if question_text:
                        question_data = {
                            "question": question_text,
                            "answers": [],
                            "correct": [],
                            "subtheme": current_subtheme  # Сохраняем подтему
                        }
                        themes[current_theme].append(question_data)

                    # Добавляем варианты ответов к последнему вопросу
                    if themes[current_theme] and "question" in themes[current_theme][-1]:
                        themes[current_theme][-1]["answers"].append(answer_text)
                        if correct_text:
                            themes[current_theme][-1]["correct"].append(answer_text)

            except StopIteration:
                pass  

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
            st.session_state["questions"] = []
            st.session_state["current_question"] = 0
            st.session_state["test_started"] = False
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {}
            st.session_state["show_confirm_exit"] = False  # Добавлено окно подтверждения выхода

        if not st.session_state.get("test_started", False):
            st.subheader("📚 Выберите тему для тестирования:")
            selected_theme = st.selectbox("Выберите тему", list(st.session_state["themes"].keys()))

            if st.button("▶️ Начать тест"):
                st.session_state["selected_theme"] = selected_theme
                st.session_state["questions"] = st.session_state["themes"][selected_theme]
                st.session_state["current_question"] = 0
                st.session_state["test_started"] = True
                st.session_state["show_result"] = False
                st.session_state["selected_answers"] = {}
                st.rerun()

        if st.session_state.get("test_started", False):
            col1, col2 = st.columns([2, 8])
            with col1:
                if st.button("🔙 Вернуться к выбору темы"):
                    st.session_state["show_confirm_exit"] = True

        # --- Окно подтверждения выхода ---
        if st.session_state.get("show_confirm_exit", False):
            st.warning("❓ Вы уверены, что хотите выйти? Ваши ответы не сохранятся.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("✅ Да, выйти"):
                    st.session_state["test_started"] = False
                    st.session_state["selected_theme"] = None
                    st.session_state["questions"] = []
                    st.session_state["current_question"] = 0
                    st.session_state["show_result"] = False
                    st.session_state["selected_answers"] = {}
                    st.session_state["show_confirm_exit"] = False
                    st.rerun()
            with c2:
                if st.button("❌ Отмена"):
                    st.session_state["show_confirm_exit"] = False
                    st.rerun()

        if st.session_state.get("test_started", False) and not st.session_state.get("show_result", False):
            q_idx = st.session_state["current_question"]
            question_data = st.session_state["questions"][q_idx]

            st.subheader(f"Вопрос {q_idx + 1} из {len(st.session_state['questions'])}")
            st.write(question_data["question"])

            selected_answers = st.session_state["selected_answers"].get(q_idx, [])

            for i, answer in enumerate(question_data["answers"]):
                key = f"q{q_idx}_a{i}"
                checked = answer in selected_answers
                if st.checkbox(answer, key=key, value=checked):
                    if answer not in selected_answers:
                        selected_answers.append(answer)
                else:
                    if answer in selected_answers:
                        selected_answers.remove(answer)

            st.session_state["selected_answers"][q_idx] = selected_answers

            col1, col2, col3 = st.columns([1, 2, 1])
            
            with col1:
                if q_idx > 0:
                    if st.button("⬅️ Предыдущий вопрос"):
                        st.session_state["current_question"] -= 1
                        st.rerun()

            with col3:
                if q_idx + 1 < len(st.session_state["questions"]):
                    if st.button("➡️ Следующий вопрос"):
                        st.session_state["current_question"] += 1
                        st.rerun()
                else:
                    if st.button("✅ Завершить тест"):
                        st.session_state["show_result"] = True
                        st.rerun()

import pandas as pd
import streamlit as st

import streamlit as st

if st.session_state.get("show_result", False):
    st.subheader("📊 Результаты теста")

    incorrect_answers = []
    correct_count = 0
    total_questions = len(st.session_state["questions"])

    for q_idx, question_data in enumerate(st.session_state["questions"]):
        user_answers = st.session_state["selected_answers"].get(q_idx, [])
        correct_answers = question_data["correct"]

        is_correct = set(user_answers) == set(correct_answers)

        if not is_correct:  # Если ответ неверный, добавляем в список ошибок
            incorrect_answers.append({
                "Вопрос": question_data["question"],
                "Ваш ответ": ", ".join(user_answers) if user_answers else "—",
                "Правильный ответ": ", ".join(correct_answers)
            })
        else:
            correct_count += 1

    # Выводим общий результат
    st.success(f"✅ Вы ответили правильно на {correct_count} из {total_questions} вопросов.")

    # Если есть ошибки, добавляем кнопку для их раскрытия
    if incorrect_answers:
        with st.expander("🔍 Показать ошибки", expanded=False):
            for error in incorrect_answers:
                with st.container():
                    st.markdown(f"**❓ Вопрос:** {error['Вопрос']}", unsafe_allow_html=True)
                    st.markdown(f"**❌ Ваш ответ:** {error['Ваш ответ']}", unsafe_allow_html=True)
                    st.markdown(f"**✅ Правильный ответ:** {error['Правильный ответ']}", unsafe_allow_html=True)
                    st.markdown("---")  # Разделитель между карточками

    else:
        st.success("🎉 Поздравляем! Все ответы верны!")

    if st.button("🔄 Пройти еще раз"):
        st.session_state["test_started"] = False
        st.session_state["selected_theme"] = None
        st.session_state["questions"] = []
        st.session_state["current_question"] = 0
        st.session_state["show_result"] = False
        st.session_state["selected_answers"] = {}
        st.rerun()



