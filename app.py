import streamlit as st
from docx import Document

st.title("📄 Онлайн-тестирование по блокам и темам")

uploaded_file = st.file_uploader("Загрузите Word-файл с тестами", type=["docx"])

def extract_blocks_and_questions(doc):
    """Извлекает блоки, темы и вопросы из документа"""
    blocks = {}
    current_block = None
    current_theme = None
    last_valid_theme = None  # Запоминаем последнюю найденную тему

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
                last_valid_theme = current_theme  # Запоминаем последнюю корректную тему

    # Выводим найденные блоки и темы (отладка)
    st.subheader("📋 Найденные блоки и темы:")
    for block, themes in blocks.items():
        st.write(f"🔹 **{block}**")
        for theme in themes:
            st.write(f"  - {theme}")

    # Обрабатываем таблицы, чтобы привязать вопросы к последней найденной теме
    for table in doc.tables:
        if not current_block:
            st.warning("⚠️ Таблица найдена без привязанного блока! Проверьте структуру документа.")
            continue  # Пропускаем таблицу, если не найден блок

        # Если перед таблицей не было новой темы, используем последнюю корректную тему
        if not current_theme:
            current_theme = last_valid_theme

        st.write("🔹 **Обрабатываем таблицу**")  # Отладочный вывод
        st.write(f"📌 Текущий блок: {current_block}")
        st.write(f"📌 Текущая тема: {current_theme}")

        if not current_theme:
            st.warning("⚠️ Таблица найдена без привязанной темы! Проверьте структуру документа.")
            continue  # Пропускаем таблицу, если не найдена тема

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
                    st.warning("⚠️ В этой теме пока нет вопросов. Проверьте, правильно ли заголовки идут перед таблицами.")
