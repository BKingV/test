import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование по темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_themes_and_questions(doc):
    """Извлекает темы и вопросы, начиная обработку только с первой темы, после которой идет таблица"""
    themes = {}
    current_theme = None
    processing_started = False  
    tables_iter = iter(doc.tables)  

    for para in doc.paragraphs:
        text = para.text.strip()

        if text.startswith("ТЕМА:"):  
            current_theme = text.replace("ТЕМА:", "").strip()

            try:
                table = next(tables_iter)  
                themes[current_theme] = []

                rows = table.rows
                if len(rows) < 2:
                    continue  

                headers = [cell.text.strip().lower() for cell in rows[0].cells]
                if "текст вопроса" not in headers or "варианты ответов" not in headers:
                    continue  

                question_idx = headers.index("текст вопроса")
                answers_idx = headers.index("варианты ответов")
                correct_idx = headers.index("эталон") if "эталон" in headers else None

                current_question = None

                for row in rows[1:]:  
                    question_text = row.cells[question_idx].text.strip()
                    answer_text = row.cells[answers_idx].text.strip()
                    correct_text = row.cells[correct_idx].text.strip() if correct_idx else ""

                    if current_question is None or current_question["question"] != question_text:
                        current_question = {
                            "question": question_text,
                            "answers": [],
                            "correct": []
                        }
                        themes[current_theme].append(current_question)

                    current_question["answers"].append(answer_text)
                    if correct_text:
                        current_question["correct"].append(answer_text)

                processing_started = True  

            except StopIteration:
                continue  

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
            st.session_state["test_started"] = False
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {}

        if not st.session_state["test_started"]:  
            st.header("Выберите тему")
            theme = st.selectbox("Тема:", list(themes.keys()), index=0 if not st.session_state["selected_theme"] else list(themes.keys()).index(st.session_state["selected_theme"]), disabled=st.session_state["test_started"])

            if theme:
                st.session_state["selected_theme"] = theme

                if st.button("Начать тест"):
                    st.session_state["test_started"] = True
                    st.session_state["current_question"] = 0
                    st.session_state["show_result"] = False
                    st.session_state["selected_answers"] = {i: [] for i in range(len(themes[theme]))}
                    st.rerun()
        else:
            # Размещаем кнопку "Вернуться к выбору темы" ВВЕРХУ рядом с заголовком темы
            col1, col2 = st.columns([5, 1])
            with col2:
                if st.button("🔙 Вернуться к выбору темы"):
                    if st.confirm_dialog(f"Вы уверены, что хотите выйти? Ваши ответы не сохранятся.", ["Да", "Отмена"]) == "Да":
                        st.session_state["test_started"] = False
                        st.session_state["selected_theme"] = None
                        st.session_state["questions"] = []
                        st.session_state["current_question"] = 0
                        st.session_state["show_result"] = False
                        st.session_state["selected_answers"] = {}
                        st.rerun()

# Проверяем, какие вопросы загружены для выбранной темы
if st.session_state.get("test_started", False) and "questions" in st.session_state and len(st.session_state["questions"]) > 0 and not st.session_state.get("show_result", False):
    q_idx = st.session_state["current_question"]
    question_data = st.session_state["questions"][q_idx]

    st.subheader(f"{st.session_state['selected_theme']} - Вопрос {q_idx + 1} из {len(st.session_state['questions'])}")
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
                if st.confirm_dialog("Вы уверены, что хотите завершить тест?", ["Да", "Отмена"]) == "Да":
                    st.session_state["show_result"] = True
                    st.rerun()

# Отображение результата теста после завершения
if st.session_state.get("show_result", False):
    st.success("✅ Тест завершен!")

    total_questions = len(st.session_state["questions"])
    correct_count = 0

    for idx, question in enumerate(st.session_state["questions"]):
        correct_set = set(question["correct"])
        selected_set = set(st.session_state["selected_answers"].get(idx, []))

        if selected_set == correct_set:
            correct_count += 1

    st.write(f"📊 Ваш результат: **{correct_count} из {total_questions}** правильных ответов.")  

    if st.button("Пройти снова"):
        st.session_state["test_started"] = False
        st.session_state["selected_theme"] = None
        st.session_state["questions"] = []
        st.session_state["current_question"] = 0
        st.session_state["show_result"] = False
        st.session_state["selected_answers"] = {}
        st.rerun()
