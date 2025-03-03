import streamlit as st
from docx import Document

def extract_themes_and_questions(doc):
    """Извлекает темы, подтемы и вопросы из документа."""
    themes = {}
    tables = doc.tables
    
    for table in tables:
        rows = table.rows
        if len(rows) < 2:
            continue
        
        headers = [cell.text.strip().lower() for cell in rows[0].cells]
        if "текст вопроса" not in headers or "варианты ответа" not in headers:
            continue
        
        question_idx = headers.index("текст вопроса")
        answers_idx = headers.index("варианты ответа")
        correct_idx = headers.index("эталон") if "эталон" in headers else None
        
        current_theme = "Тема по умолчанию"
        current_subtheme = None
        themes[current_theme] = []
        
        for row in rows[1:]:
            first_cell_text = row.cells[0].text.strip()
            question_text = row.cells[question_idx].text.strip()
            answer_text = row.cells[answers_idx].text.strip()
            correct_text = row.cells[correct_idx].text.strip() if correct_idx else ""
            
            if first_cell_text and first_cell_text.lower() == first_cell_text:
                current_subtheme = first_cell_text
                continue
            
            question_data = {
                "question": question_text,
                "answers": [answer_text],
                "correct": [correct_text] if correct_text else [],
                "subtheme": current_subtheme,
            }
            themes[current_theme].append(question_data)
    
    return themes

st.title("📄 Онлайн-тестирование по темам")
uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

if uploaded_file:
    doc = Document(uploaded_file)
    themes = extract_themes_and_questions(doc)

    if not themes:
        st.warning("⚠️ Не удалось извлечь темы и вопросы. Проверьте формат документа.")
    else:
        st.session_state["themes"] = themes
        st.session_state["selected_theme"] = None
        st.session_state["selected_subtheme"] = None
        st.session_state["questions"] = []
        st.session_state["test_started"] = False

        selected_theme = st.selectbox("Выберите тему", list(themes.keys()), key="theme_select")
        subthemes = list(set(q["subtheme"] for q in themes[selected_theme] if q["subtheme"]))

        if subthemes:
            selected_subtheme = st.selectbox("Выберите подтему", subthemes, key="subtheme_select")
        
        if st.button("▶️ Начать тест"):
            st.session_state["selected_theme"] = selected_theme
            st.session_state["selected_subtheme"] = selected_subtheme if subthemes else None
            st.session_state["questions"] = [q for q in themes[selected_theme] if q["subtheme"] == selected_subtheme or not subthemes]
            st.session_state["test_started"] = True
            st.session_state["current_question"] = 0
            st.session_state["selected_answers"] = {}
            st.rerun()

if st.session_state.get("test_started", False):
    q_idx = st.session_state["current_question"]
    questions = st.session_state["questions"]

    if q_idx < len(questions):
        question_data = questions[q_idx]
        st.subheader(f"Вопрос {q_idx + 1} из {len(questions)}")
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
            if q_idx > 0 and st.button("⬅️ Предыдущий вопрос"):
                st.session_state["current_question"] -= 1
                st.rerun()
        with col3:
            if q_idx + 1 < len(questions):
                if st.button("➡️ Следующий вопрос"):
                    st.session_state["current_question"] += 1
                    st.rerun()
            else:
                if st.button("✅ Завершить тест"):
                    st.session_state["show_result"] = True
                    st.rerun()

if st.session_state.get("show_result", False):
    st.subheader("📊 Результаты теста")
    correct_count = sum(1 for i, q in enumerate(st.session_state["questions"]) if set(st.session_state["selected_answers"].get(i, [])) == set(q["correct"]))
    total_count = len(st.session_state["questions"])
    st.success(f"🎉 Вы ответили правильно на {correct_count} из {total_count} вопросов.")
    if st.button("🔄 Пройти еще раз"):
        st.session_state["test_started"] = False
        st.session_state["show_result"] = False
        st.rerun()

