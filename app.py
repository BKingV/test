import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование по блокам и темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_blocks_and_questions(doc):
    """Извлекает блоки, темы и вопросы из документа"""
    blocks = {}
    current_block = None
    current_theme = None

    # Обрабатываем заголовки для блоков и тем
    for para in doc.paragraphs:
        text = para.text.strip()
        style = para.style.name

        if style == "Heading 1":  # Если заголовок 1-го уровня - это блок
            current_block = text
            blocks[current_block] = {}
            current_theme = None  # Сбрасываем текущую тему
        elif style == "Heading 2":  # Если заголовок 2-го уровня - это тема
            if current_block:
                current_theme = text.replace("ТЕМА:", "").strip()
                blocks[current_block][current_theme] = []

    # Обрабатываем таблицы, чтобы привязать вопросы к последней найденной теме
    for table in doc.tables:
        if not current_block or not current_theme:
            continue  # Пропускаем таблицу, если не найден блок или тема

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

            if current_block and current_theme:
                blocks[current_block][current_theme].append({
                    "question": question_text,
                    "answers": answer_text.split("\n"),  # Разделяем ответы по строкам
                    "correct": correct_text.split("\n")  # Разделяем правильные ответы
                })

    return blocks

if uploaded_file:
    doc = Document(uploaded_file)
    blocks = extract_blocks_and_questions(doc)

    if not blocks:
        st.warning("Не удалось извлечь блоки и вопросы. Проверьте формат документа.")
    else:
        if "blocks" not in st.session_state:
            st.session_state["blocks"] = blocks
            st.session_state["selected_block"] = None
            st.session_state["selected_theme"] = None
            st.session_state["questions"] = []
            st.session_state["current_question"] = 0
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {}

        # Выбор блока
        st.header("Выберите блок")
        block = st.selectbox("Блок:", list(blocks.keys()), index=0 if not st.session_state["selected_block"] else list(blocks.keys()).index(st.session_state["selected_block"]))

        if block:
            st.session_state["selected_block"] = block

            # Выбор темы
            st.header("Выберите тему")
            theme = st.selectbox("Тема:", list(blocks[block].keys()), index=0 if not st.session_state["selected_theme"] else list(blocks[block].keys()).index(st.session_state["selected_theme"]))

            if theme:
                st.session_state["selected_theme"] = theme

                # Проверяем, есть ли вопросы в теме
                if len(blocks[block][theme]) > 0:
                    st.session_state["questions"] = blocks[block][theme]
                    st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}

                    if st.button("Начать тест"):
                        st.session_state["current_question"] = 0
                        st.session_state["show_result"] = False
                        st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}
                        st.rerun()
                else:
                    st.warning("В этой теме пока нет вопросов.")

# Проверяем, какие вопросы загружены для выбранной темы
if "questions" in st.session_state and len(st.session_state["questions"]) > 0 and not st.session_state.get("show_result", False):
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
    correct_count = 0

    # Подсчет правильных ответов ТОЛЬКО после нажатия "Завершить тест"
    for idx, question in enumerate(st.session_state["questions"]):
        correct_set = set(question["correct"])
        selected_set = set(st.session_state["selected_answers"].get(idx, []))

        if selected_set == correct_set:
            correct_count += 1

    st.write(f"📊 Ваш результат: **{correct_count} из {total_questions}** правильных ответов.")  

    if st.button("Пройти снова"):
        st.session_state["selected_block"] = None
        st.session_state["selected_theme"] = None
        st.session_state["questions"] = []
        st.session_state["current_question"] = 0
        st.session_state["show_result"] = False
        st.session_state["selected_answers"] = {}
        st.rerun()
