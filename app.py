import docx
import re

def load_questions(docx_path):
    doc = docx.Document(docx_path)
    questions = []
    current_question = {}
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        # Определение начала нового вопроса
        match = re.match(r'^(\d+)\s+(.*)', text)
        if match:
            if current_question:
                questions.append(current_question)
                current_question = {}
            current_question['number'] = match.group(1)
            current_question['question'] = match.group(2)
            current_question['options'] = []
        elif 'Эталон' in text:
            current_question['answer'] = text.split('Эталон')[0].strip()
        else:
            # Предполагается, что варианты ответов следуют после вопроса
            current_question['options'].append(text)
    if current_question:
        questions.append(current_question)
    return questions

def conduct_test(questions):
    score = 0
    for q in questions:
        print(f"\nВопрос {q['number']}: {q['question']}")
        options = q['options']
        for idx, option in enumerate(options, 1):
            print(f"{idx}. {option}")
        try:
            answer = int(input("Ваш ответ (укажите номер варианта): "))
            if options[answer - 1].lower() == q['answer'].lower():
                print("Правильно!")
                score += 1
            else:
                print(f"Неверно. Правильный ответ: {q['answer']}")
        except (IndexError, ValueError):
            print("Некорректный ввод. Перейдём к следующему вопросу.")
    print(f"\nТест завершён. Ваш результат: {score}/{len(questions)}")

if __name__ == "__main__":
    docx_file = "ЛЭИ ЦЭСТ (Алтухова) - 2025 (003).docx"
    questions = load_questions(docx_file)
    conduct_test(questions)
