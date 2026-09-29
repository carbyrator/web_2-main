import json
from pathlib import Path

d_b = Path(__file__).resolve().parent.parent / 'students.json' # база данных в корне проекта

# Читает список студентов из JSON-файла
def load_data():
    if not d_b.exists(): # проверяем, есть ли файл на диске
        return []  # Если файла нет, возвращаем пустой список, чтобы проога не упала с ошибкой
    with open(d_b, 'r', encoding='utf-8') as file: # открываем файл на чтение. utf-8 для ру букв
        return json.load(file)

# Записывает список студентов в JSON-файл
def save_data(students): # открываем файл на запись. Если файла не было, он создастся. Если был — полностью перезапишется
    with open(d_b, 'w', encoding='utf-8') as file:
        json.dump(students, file, ensure_ascii=False, indent=2)

# Возвращает всех студентов (просто возвращает весь список из файла)
def get_all():
    return load_data()

# Ищет и возвращает одного студента по ису
def get_by_isu(isu):
    students = load_data() # загружаем список и перебираем его
    for s in students:
        if s['isu'] == isu:
            return s
    return None

# Добавляет нового студента в конец списка и сохраняет
def add(student):
    students = load_data()
    students.append(student)
    save_data(students) # перезаписываем файл обновленным списком
    return student # возвращаем добавленного студента (чтобы бэкенд мог отдать его в ответе с кодом 201)

# Частично (меняет только те поля, которые пришли с фронта, не трогая остальные) обновляет данные студента (для PATCH)
def update(isu, updates):
    students = load_data()
    for s in students:
        if s['isu'] == isu:
            s.update(updates)  # Встроенный метод словаря, меняющий одно поле
            save_data(students)
            return s
    return None

# Удаляет студента по ИСУ. Возвращает True, если удалил, и False, если не нашел
def delete(isu):
    students = load_data()
    new_students = [s for s in students if s['isu'] != isu] # Оставляем только тех, у кого ИСУ не совпадает с удаляемым
    if len(new_students) < len(students): # проверяем, стал ли список короче
        save_data(new_students)
        return True
    return False

# Фильтрует студентов по переданным параметрам (QUERY)
def filter_students(filters):
    students = load_data() # загружаем всех студентов
    result = students # и создаем переменную, с которой будем работать
    for key, value in filters.items(): # Проходим по каждому переданному фильтру (ключ: значение)
        result = [s for s in result if str(s.get(key)) == str(value)] # Оставляем только тех, у кого значение поля совпадает с фильтром

    return result
