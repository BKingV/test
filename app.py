import pandas as pd
import streamlit as st

def load_questions_from_excel(file):
    """Загружает вопросы из файла Excel и структурирует данные."""
    df = pd.read_excel(file, sheet_name=None)  # Загружаем все листы
    questions = []
    
    for sheet_name, data in df.items():
        for _, row in data.iterrows():
            if pd.notna(row["№ п/п"]):
                questions.append({
                    "block": sheet_name,  # Название блока
                    "topic": row["Тема"],  # Название темы
                    "number": row["№ п/п"],  # Номер вопроса
                    "question": row["Текст вопроса"],  # Текст вопроса
                    "options": str(row["Варианты ответа"]).split(";"),  # Разделяем варианты ответа
                    "correct_answers": str(row["Эталон"]).split(";")  # Разделяем правильные ответы
                })
    return questions

def main():
    """Основная логика работы теста."""
    st.title("📝 Тренажер для подготовки к тесту")
    uploaded_file = st.file_uploader("📂 Загрузите файл Excel с вопросами", type=["xlsx", "xls"])
    
    if uploaded_file:
        questions = load_questions_from_excel(uploaded_file)
        if not questions:
            st.error("❌ Ошибка: вопросы не загружены.")
            return
        
        blocks = list(set(q['block'] for q in questions))
        selected_block = st.selectbox("Выберите блок", blocks)
        block_questions = [q for q in questions if q['block'] == selected_block]
        
        topics = list(set(q['topic'] for q in block_questions))
        selected_topic = st.selectbox("Выберите тему", topics)
        topic_questions = [q for q in block_questions if q['topic'] == selected_topic]
        
        score = 0
        for idx, q in enumerate(topic_questions):
            st.write(f"**{q['number']}. {q['question']}**")
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
