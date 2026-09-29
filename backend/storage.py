"""Хранение студентов в JSON-файле и простые операции над списком."""

import json
from pathlib import Path

# Файл данных лежит в корне проекта, а не в папке backend.
d_b = Path(__file__).resolve().parent.parent / 'students.json'

def load_data():
    """Превращает JSON-файл в список словарей; отсутствие файла означает пустой список."""
    if not d_b.exists():
        return []
    with open(d_b, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_data(students):
    """Полностью перезаписывает JSON-файл текущим списком студентов."""
    with open(d_b, 'w', encoding='utf-8') as file:
        # ensure_ascii=False оставляет русские буквы читаемыми, indent добавляет отступы.
        json.dump(students, file, ensure_ascii=False, indent=2)

def get_all():
    """Возвращает все записи без фильтрации."""
    return load_data()

def get_by_isu(isu):
    """Ищет студента по уникальному ИСУ; None означает, что записи нет."""
    students = load_data()
    for s in students:
        if s['isu'] == isu:
            return s
    return None

def add(student):
    """Добавляет студента в список и сохраняет обновлённый файл."""
    students = load_data()
    students.append(student)
    save_data(students)
    return student

def update(isu, updates):
    """Находит студента и меняет только поля, переданные в updates."""
    students = load_data()
    for s in students:
        if s['isu'] == isu:
            # dict.update заменяет указанные поля, остальные остаются прежними.
            s.update(updates)
            save_data(students)
            return s
    return None

def delete(isu):
    """Удаляет запись по ИСУ; возвращает True, если студент был найден."""
    students = load_data()
    # Списковое включение оставляет все записи, кроме удаляемой.
    new_students = [s for s in students if s['isu'] != isu]
    if len(new_students) < len(students):
        save_data(new_students)
        return True
    return False

def filter_students(filters):
    """Ищет все записи по части значения каждого фильтра GET/QUERY."""
    students = load_data()
    result = students
    for key, value in filters.items():
        # Для флага нужен точный ответ, остальные поля ищем по части
        if key == 'foreigner':
            result = [s for s in result if s.get(key) is value]
        else:
            result = [s for s in result if value.casefold() in str(s.get(key, '')).casefold()]

    return result
