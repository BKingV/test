import random
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
                options = [opt.strip() for opt in cells[2].text.split("\n") if opt.strip()]
                correct_answers = [ans.strip() for ans in cells[3].text.split("\n") if ans.strip()]
                
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
        random.shuffle(topic_questions)
        
        score = 0
        for q in topic_questions:
            st.subheader(f"{q['number']}. {q['question']}")
            selected_option = st.radio("Выберите ответ:", q['options'], key=q['question'])
            if st.button("Проверить", key="check_" + q['question']):
                if selected_option in q['correct_answers']:
                    st.success("✅ Правильно!")
                    score += 1
                else:
                    st.error(f"❌ Неправильно. Правильный ответ: {', '.join(q['correct_answers'])}")
        
        st.write(f"🏆 Тест завершен! Ваш результат: {score}/{len(topic_questions)}")

if __name__ == "__main__":
    main()
