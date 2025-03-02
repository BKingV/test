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
        correct_answer = None

        for row in rows[1:]:  # Пропускаем заголовки
            question_text = row.cells[question_idx].text.strip()
            answer_text = row.cells[answers_idx].text.strip()
            correct_text = row.cells[correct_idx].text.strip() if correct_idx else ""

            if question_text:  # Если новая строка с вопросом
                if current_question and answers:
                    questions.append({
                        "question": current_question,
                        "answers": answers,
                        "correct": correct_answer
                    })
                current_question = question_text
                answers = []
                correct_answer = None

            if answer_text:
                answer_options = answer_text.split("\n")  # Разбиваем варианты ответов по строкам
                answers.extend([a.strip() for a in answer_options if a.strip()])

            if correct_text:  # Если есть правильный ответ
                correct_answer = correct_text.strip()

        if current_question and answers:
            questions.append({
                "question": current_question,
                "answers": answers,
                "correct": correct_answer
            })

    return questions

if uploaded_file:
    doc = Document(uploaded_file)
    questions = extract_questions_from_tables(doc)

    if not questions:
        st.warning("Не удалось извлечь вопросы. Проверьте формат документа.")
    else:
        st.session_state["questions"] = questions
        st.success(f"Найдено {len(questions)} вопросов. Можно начинать тест!")
        if st.button("Начать тест"):
            st.session_state["current_question"] = 0
            st.session_state["score"] = 0
            st.rerun()

# Отображение теста
if "questions" in st.session_state and "current_question" in st.session_state:
    q_idx = st.session_state["current_question"]
    question_data = st.session_state["questions"][q_idx]

    st.subheader(question_data["question"])
    selected_answer = st.radio("Выберите ответ:", question_data["answers"])

    if st.button("Ответить"):
        if selected_answer == question_data["correct"]:
            st.session_state["score"] += 1

        if q_idx + 1 < len(st.session_state["questions"]):
            st.session_state["current_question"] += 1
            st.rerun()
        else:
            st.success("Тест завершен!")
            st.write(f"Вы ответили правильно на {st.session_state['score']} из {len(st.session_state['questions'])} вопросов.")
