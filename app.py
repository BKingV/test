import random
import docx
import streamlit as st

def load_questions_from_docx(file):
    """Загружает вопросы из файла .docx"""
    doc = docx.Document(file)
    questions = []
    for table in doc.tables:
        for row in table.rows[1:]:  # Пропускаем заголовки
            cells = row.cells
            if len(cells) >= 4:
                question_text = cells[1].text.strip()
                options = [cells[i].text.strip() for i in range(2, 5)]
                answer = cells[2].text.strip()
                questions.append({"question": question_text, "options": options, "answer": answer})
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
        
        random.shuffle(questions)
        score = 0
        
        for q in questions:
            st.subheader(q['question'])
            selected_option = st.radio("Выберите ответ:", q['options'], key=q['question'])
            if st.button("Проверить", key="check_" + q['question']):
                if selected_option == q['answer']:
                    st.success("✅ Правильно!")
                    score += 1
                else:
                    st.error(f"❌ Неправильно. Правильный ответ: {q['answer']}")
        
        st.write(f"🏆 Тест завершен! Ваш результат: {score}/{len(questions)}")

if __name__ == "__main__":
    main()
