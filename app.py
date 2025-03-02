import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование из Word-файла")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_questions_from_docx(doc):
    """Извлекает блоки, темы и вопросы из Word-файла"""
    structure = {}
    current_block = None
    current_theme = None

    for para in doc.paragraphs:
        text = para.text.strip()

        if not text:
            continue  # Пропускаем пустые строки

        if text.startswith("Блок"):  # Если это новый блок
            current_block = text
            structure[current_block] = {}
        elif text.startswith("Тема"):  # Если это новая тема в блоке
            if current_block:
                current_theme = text
                structure[current_block][current_theme] = []
        elif current_theme:  # Если это вопрос в текущей теме
            structure[current_block][current_theme].append(text)

    return structure

if uploaded_file:
    doc = Document(uploaded_file)
    structure = extract_questions_from_docx(doc)

    if not structure:
        st.warning("Не удалось извлечь вопросы. Проверьте формат документа.")
    else:
        if "structure" not in st.session_state:
            st.session_state["structure"] = structure
            st.session_state["selected_block"] = None
            st.session_state["selected_theme"] = None
            st.session_state["questions"] = []
            st.session_state["current_question"] = 0
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {}

        # Выбор блока
        st.header("Выберите блок")
        block = st.selectbox("Блок:", list(structure.keys()), index=0 if not st.session_state["selected_block"] else list(structure.keys()).index(st.session_state["selected_block"]))

        if block:
            st.session_state["selected_block"] = block

            # Выбор темы
            st.header("Выберите тему")
            theme = st.selectbox("Тема:", list(structure[block].keys()), index=0 if not st.session_state["selected_theme"] else list(structure[block].keys()).index(st.session_state["selected_theme"]))

            if theme:
                st.session_state["selected_theme"] = theme
                st.session_state["questions"] = structure[block][theme]
                st.session_state["current_question"] = 0
                st.session_state["show_result"] = False
                st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}

                if st.button("Начать тест"):
                    st.session_state["current_question"] = 0
                    st.session_state["show_result"] = False
                    st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}
                    st.rerun()

# Отображение теста по выбранной теме
if "questions" in st.session_state and len(st.session_state["questions"]) > 0 and not st.session_state.get("show_result", False):
    q_idx = st.session_state["current_question"]
    question_text = st.session_state["questions"][q_idx]

    st.subheader(f"{st.session_state['selected_theme']} - Вопрос {q_idx + 1} из {len(st.session_state['questions'])}")
    st.write(question_text)

    selected_answers = st.session_state["selected_answers"].get(q_idx, [])

    for i, answer in enumerate(["Ответ 1", "Ответ 2", "Ответ 3", "Ответ 4"]):  # Пока заглушка для вариантов
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
        if st.button("⬅️ Предыдущий вопрос") and q_idx > 0:
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

# Отображение результата теста после завершения
if st.session_state.get("show_result", False):
    st.success("✅ Тест завершен!")
    total_questions = len(st.session_state["questions"])
    
    # Пока просто заглушка для результата
    st.write(f"📊 Ваш результат: **X из {total_questions}** правильных ответов.")  

    if st.button("Пройти снова"):
        st.session_state["selected_block"] = None
        st.session_state["selected_theme"] = None
        st.session_state["questions"] = []
        st.session_state["current_question"] = 0
        st.session_state["show_result"] = False
        st.session_state["selected_answers"] = {}
        st.rerun()
