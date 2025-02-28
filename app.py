import pandas as pd
import streamlit as st
import openpyxl  # Убедимся, что библиотека установлена и импортирована

def load_questions_from_excel(file):
    """Загружает вопросы из Excel, начиная с первой ячейки в столбце A, равной 1."""
    df = pd.read_excel(file, sheet_name=None, engine="openpyxl")  # Загружаем все листы
    questions = []

    for sheet_name, data in df.items():
        st.write(f"🔍 Обрабатываем лист: {sheet_name}")  # Для отладки выводим имя листа

        # Ищем строку, в которой в первой колонке (A) есть число 1
        start_row = None
        for i, value in enumerate(data.iloc[:, 0]):  # Перебираем первый столбец (A)
            if pd.notna(value) and str(value).strip() == "1":
                start_row = i
                break  # Нашли начало теста

        if start_row is None:
            st.warning(f"⚠️ На листе '{sheet_name}' не найдено начало теста (значение '1' в первом столбце). Пропускаем.")
            continue  # Если не нашли начало теста, пропускаем лист

        # Загружаем вопросы, начиная с найденной строки
        data = data.iloc[start_row:]  # Обрезаем все строки до начала теста
        data.columns = data.iloc[0]  # Устанавливаем первую строку в качестве заголовков
        data = data[1:].reset_index(drop=True)  # Удаляем строку-заголовок из данных

        # Проверяем, содержатся ли нужные столбцы
        required_columns = ["№ п/п", "Тема", "Текст вопроса", "Варианты ответа", "Эталон"]
        if not all(col in data.columns for col in required_columns):
            st.error(f"❌ Ошибка: На листе '{sheet_name}' не хватает нужных столбцов! Пропускаем.")
            continue

        # Читаем данные и формируем список вопросов
        for _, row in data.iterrows():
            number = str(row["№ п/п"]).strip()
            if not number.endswith("."):
                number += "."  # Добавляем точку, если её нет

            questions.append({
                "block": sheet_name,  # Название б
