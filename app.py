import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование из Word-файла")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_questions_from_tables(doc):
    """Извлекает вопросы и ответы из таблиц Word-документа"""
    questions = []

    for table in doc.tables:
        rows = table.rows
        if len(rows) < 2:
            continue  # Пропускаем пустые таблицы

        headers = [cell.text.strip().lower() for cell in rows[0].cells]
        if "текст вопроса" not in headers or "варианты ответов" not in headers:
            continue  # Пропускаем таблицы без заголовков

        question_idx = headers.index("текст вопроса")
        answers_idx = headers.index("варианты ответов")
        correct_idx = headers.index("эталон") if "эталон" in headers else None

        current_question = None
        answers = []
        correct_answers = []

        for row in rows[1:]:  # Пропускаем заголовки
            question_text = row.cells[question_idx].text.strip()
            answer_text = row.cells[answers_idx].text.strip()
            correct_text = row.cells[correct_idx].text.strip() if correct_idx else ""

            if question_text and question_text != current_question:
                # Если это новый вопрос, сохраняем предыдущий и начинаем новый
                if current_question and answers:
                    questions.append({
                        "question": current_question,
                        "answers": answers,
                        "correct": correct_answers
                    })
                current_question = question_text
                answers = []
                correct_answers = []

            if answer_text:
                answers.append(answer_text)  # Добавляем новый вариант ответа

            if correct_text:  # Если есть правильный ответ
                correct_answers.append(answer_text)  # Запоминаем ВСЕ правильные ответы

        # Добавляем последний вопрос после прохода по всем строкам
        if current_question and answers:
            questions.append({
                "question": current_question,
                "answers": answers,
                "correct": correct_answers
            })

    return questions

if uploaded_file:
    doc = Document(uploaded_file)
    questions = extract_questions_from_tables(doc)

    if not questions:
        st.warning("Не удалось извлечь вопросы. Проверьте формат документа.")
    else:
        if "questions" not in st.session_state:
            st.session_state["questions"] = questions
            st.session_state["current_question"] = 0
            st.session_state["score"] = 0
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {i: [] for i in range(len(questions))}  # Сохраняем выбранные ответы

        st.success(f"Найдено {len(questions)} вопросов. Можно начинать тест!")

        if st.button("Начать тест"):
            st.session_state["current_question"] = 0
            st.session_state["score"] = 0
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {i: [] for i in range(len(questions))}
            st.rerun()

# Отображение теста с кнопками "Предыдущий вопрос" и "Следующий вопрос"
if "questions" in st.session_state and "current_question" in st.session_state and not st.session_state.get("show_result", False):
    q_idx = st.session_state["current_question"]
    question_data = st.session_state["questions"][q_idx]

    st.subheader(question_data["question"])
    
    selected_answers = st.session_state["selected_answers"].get(q_idx, [])

    for i, answer in enumerate(question_data["answers"]):
        key = f"q{q_idx}_a{i}"  # Уникальный ключ для каждого чекбокса
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
        if st.button("➡️ Следующий вопрос"):
            correct_set = set(question_data["correct"])
            selected_set = set(selected_answers)

            # Начисляем балл только если выбраны ТОЛЬКО правильные ответы
            if selected_set == correct_set:
                st.session_state["score"] += 1

            # Переходим к следующему вопросу
            if q_idx + 1 < len(st.session_state["questions"]):
                st.session_state["current_question"] += 1
                st.rerun()
            else:
                st.session_state["show_result"] = True
                st.rerun()

# Отображение результата теста
if st.session_state.get("show_result", False):
    st.success("✅ Тест завершен!")
    total_questions = len(st.session_state["questions"])
    score = st.session_state["score"]
    st.write(f"📊 Ваш результат: **{score} из {total_questions}** правильных ответов.")

    if st.button("Пройти снова"):
        st.session_state["current_question"] = 0
        st.session_state["score"] = 0
        st.session_state["show_result"] = False
        st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}
        st.rerun()
