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

                    # Если это новый вопрос
                    if current_question is None or current_question["question"] != question_text:
                        current_question = {
                            "question": question_text,
                            "answers": [],
                            "correct": []
                        }
                        themes[current_theme].append(current_question)

                    # Добавляем вариант ответа к текущему вопросу
                    current_question["answers"].append(answer_text)
                    if correct_text:
                        current_question["correct"].append(answer_text)

                processing_started = True  

            except StopIteration:
                # Нет таблицы после темы — пропускаем
                pass  

    return themes

# --- Основная логика приложения ---

if uploaded_file:
    doc = Document(uploaded_file)
    themes = extract_themes_and_questions(doc)

    if not themes:
        st.warning("Не удалось извлечь темы и вопросы. Проверьте формат документа.")
    else:
        # Инициализируем состояние при первой загрузке
        if "themes" not in st.session_state:
            st.session_state["themes"] = themes
            st.session_state["selected_theme"] = None
            st.session_state["questions"] = []
            st.session_state["current_question"] = 0
            st.session_state["test_started"] = False
            st.session_state["show_result"] = False
            st.session_state["selected_answers"] = {}
            st.session_state["show_confirm_exit"] = False

        # 1. Если тест НЕ запущен, показываем выбор темы и кнопку "Начать тест"
        if not st.session_state["test_started"]:
            st.header("Выберите тему")
            theme_list = list(themes.keys())
            if not theme_list:
                st.warning("Нет доступных тем.")
            else:
                # Выбираем тему
                selected = st.selectbox("Тема:", theme_list, index=0)
                st.session_state["selected_theme"] = selected

                # Кнопка начать тест
                if st.button("Начать тест"):
                    st.session_state["test_started"] = True
                    st.session_state["current_question"] = 0
                    st.session_state["show_result"] = False
                    # Загружаем вопросы выбранной темы
                    st.session_state["questions"] = st.session_state["themes"][selected]
                    # Сбрасываем ответы
                    st.session_state["selected_answers"] = {i: [] for i in range(len(st.session_state["questions"]))}
                    st.rerun()

        # 2. Если тест запущен, показываем вопросы
        else:
            # --- Кнопка "Вернуться к выбору темы" (с подтверждением) ---
            col1, col2 = st.columns([5,1])
            with col2:
                if st.button("🔙 Вернуться к выбору темы"):
                    st.session_state["show_confirm_exit"] = True

            # Окно подтверждения выхода
            if st.session_state["show_confirm_exit"]:
                st.warning("❓ Вы уверены, что хотите выйти? Ваши ответы не сохранятся.")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("✅ Да, выйти"):
                        # Сброс теста
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

            # --- Показываем текущий вопрос ---
            if st.session_state["questions"] and not st.session_state["show_result"]:
                q_idx = st.session_state["current_question"]
                if q_idx >= len(st.session_state["questions"]):
                    # Защита от выхода за предел массива
                    q_idx = len(st.session_state["questions"]) - 1

                question_data = st.session_state["questions"][q_idx]

                st.subheader(f"{st.session_state['selected_theme']} - Вопрос {q_idx + 1} из {len(st.session_state['questions'])}")
                st.write(question_data["question"])

                # Отмеченные ответы
                selected_answers = st.session_state["selected_answers"].get(q_idx, [])

                # Чекбоксы с вариантами
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

                # Кнопки навигации
                c_left, c_right = st.columns([1,1])
                with c_left:
                    # Предыдущий вопрос (убираем на первом)
                    if q_idx > 0:
                        if st.button("⬅️ Предыдущий вопрос"):
                            st.session_state["current_question"] -= 1
                            st.rerun()

                with c_right:
                    # Следующий вопрос или Завершить
                    if q_idx + 1 < len(st.session_state["questions"]):
                        if st.button("➡️ Следующий вопрос"):
                            st.session_state["current_question"] += 1
                            st.rerun()
                    else:
                        if st.button("✅ Завершить тест"):
                            st.session_state["show_result"] = True
                            st.rerun()

            # 3. Отображение результата
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
                    st.session_state["show_confirm_exit"] = False
                    st.rerun()
