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
            
            if first_cell_text and not question_text:
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
        subthemes = list(set(q["subtheme"] for q in themes[selected_theme] if q["subtheme"])) if themes[selected_theme] else []

        selected_subtheme = None
        if subthemes:
            selected_subtheme = st.selectbox("Выберите подтему", subthemes, key="subtheme_select")
        
        if st.button("▶️ Начать тест"):
            st.session_state["selected_theme"] = selected_theme
            st.session_state["selected_subtheme"] = selected_subtheme if selected_subtheme else None
            st.session_state["questions"] = [q for q in themes[selected_theme] if q.get("subtheme") == selected_subtheme or not selected_subtheme]
            st.session_state["test_started"] = True
            st.session_state["current_question"] = 0
            st.session_state["selected_answers"] = {}
            st.rerun()
