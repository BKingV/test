import docx
import streamlit as st

def load_questions_from_docx(file):
    """Загружает вопросы из файла .docx и корректно извлекает данные"""
    doc = docx.Document(file)
    questions = []
    current_topic = ""
    
    for para in doc.paragraphs:
        if para.text.startswith("ТЕМА:"):
            current_topic = para.text.strip()
    
    for table in doc.tables:
        for row in table.rows[1:]:  # Пропускаем заголовки
            cells = row.cells
            if len(cells) >= 4:
                question_number = cells[0].text.strip()
                question_text = cells[1].text.strip()
                options = [opt.strip() for opt in cells[2].text.split("\n") if opt.strip()]  # Корректно разбираем варианты ответов
                correct_answers = [ans.strip() for ans in cells[3].text.split("\n") if ans.strip()]  # Корректно разбираем эталонные ответы
                
                if question_text and options:
                    questions.append({
                        "topic": current_topic,
                        "number": question_number,
                        "question": question_text,
                        "options": options,
                        "correct_answers": correct_answers
                    })
    return questions

def main():
    """Основная логика работы теста"""
    st.title("📝 Тренажер для подготовки к тесту")
    uploaded_file = st.file_uploader("📂 Загрузите файл .docx с вопросами", type=["docx"])
    
    if uploaded_file:
        questions = load_questions_from_docx(uploaded_file)
        if not questions:
            st.error("❌ Ошибка: вопросы не загружены.")
            return
        
        topics = list(set(q['topic'] for q in questions))
        selected_topic = st.selectbox("Выберите тему", topics)
        topic_questions = [q for q in questions if q['topic'] == selected_topic]
        
        score = 0
        for idx, q in enumerate(topic_questions):
            st.write(f"**{q['number']}. {q['question']}**")  # Исправлено форматирование вывода
            selected_option = st.radio("Выберите ответ:", q['options'], key=f"q_{idx}", index=None)
            
            if st.button(f"Проверить {q['number']}", key=f"check_{idx}"):
                if selected_option and selected_option in q['correct_answers']:
                    st.success("✅ Правильно!")
                    score += 1
                elif selected_option:
                    st.error(f"❌ Неправильно. Правильный ответ: {', '.join(q['correct_answers'])}")
                else:
                    st.warning("⚠️ Выберите вариант ответа перед проверкой.")
        
        st.write(f"🏆 Тест завершен! Ваш результат: {score}/{len(topic_questions)}")

if __name__ == "__main__":
    main()
