import storage
import re # встроенная библиотека Python для работы с регулярными выражениями
from datetime import date

# Валидация (Возвращает словарь ошибок или пустой словарь, если всё ок)
def validate(data, is_update=False):
    """Валидация"""
    errors = {}

    if not is_update:
        required = ['name', 'group', 'isu', 'dorm', 'room', 'expDate', 'foreigner']
        for field in required:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                errors[field] = 'Обязательное поле'

    if 'name' in data:
        name = data['name']
        if not isinstance(name, str) or not name.strip():
            errors['name'] = 'Обязательное поле'
        elif len(name.strip().split()) < 2:
            errors['name'] = 'ФИО должно содержать минимум 2 слова'
        elif not re.fullmatch(r'[a-zA-Zа-яА-ЯёЁ\s]+', name):
            errors['name'] = 'ФИО должно содержать только буквы'

    if 'group' in data:
        group = data['group']
        if not isinstance(group, str) or not re.fullmatch(r'[A-Za-z][1-9][0-9]{3}', group):
            errors['group'] = 'Группа: 1 буква и 4 цифры (например, P1234)'

    if 'isu' in data:
        isu = data['isu']
        if isinstance(isu, bool) or not re.fullmatch(r'\d+', str(isu)):
            errors['isu'] = 'ИСУ должен быть целым числом'
        elif not 100000 <= int(isu) <= 999999:
            errors['isu'] = 'ИСУ должен быть от 100000 до 999999'

    if 'dorm' in data:
        dorm = data['dorm']
        if isinstance(dorm, bool) or not re.fullmatch(r'\d+', str(dorm)):
            errors['dorm'] = 'Номер общежития должен быть целым числом'
        elif not 1 <= int(dorm) <= 100:
            errors['dorm'] = 'Номер общежития: от 1 до 100'

    if 'room' in data:
        room = data['room']
        if not isinstance(room, str) or not re.fullmatch(r'[0-9]{2,4}[A-Za-zА-Яа-яЁё]?', room):
            errors['room'] = 'Комната: 2-4 цифры и необязательная буква'

    if 'expDate' in data:
        try:
            if not isinstance(data['expDate'], str):
                raise ValueError
            date.fromisoformat(data['expDate'])
        except ValueError:
            errors['expDate'] = 'Укажите дату в формате ГГГГ-ММ-ДД'

    if 'foreigner' in data and not isinstance(data['foreigner'], bool):
        errors['foreigner'] = 'Укажите статус студента'

    if 'notes' in data and not isinstance(data['notes'], str):
        errors['notes'] = 'Заметки должны быть текстом'

    return errors


FILTER_FIELDS = {'name', 'group', 'isu', 'dorm', 'room', 'expDate', 'foreigner', 'notes'}


def normalize_filters(raw_filters):
    """Проверяет фильтры GET/QUERY и приводит их к типам модели студента."""
    filters = {}
    errors = {}
    for original_key, value in raw_filters.items():
        key = 'dorm' if original_key == 'dormitory' else original_key
        if key not in FILTER_FIELDS:
            errors[original_key] = 'Неизвестное свойство студента'
            continue

        if key in ('isu', 'dorm'):
            if isinstance(value, bool) or not re.fullmatch(r'\d+', str(value)):
                errors[original_key] = 'Ожидалось целое число'
                continue
            value = int(value)
        elif key == 'foreigner':
            if isinstance(value, str) and value.lower() in ('true', 'false'):
                value = value.lower() == 'true'
            elif not isinstance(value, bool):
                errors[original_key] = 'Ожидалось true или false'
                continue
        elif not isinstance(value, str) or not value.strip():
            errors[original_key] = 'Ожидалась непустая строка'
            continue
        else:
            value = value.strip()

        if key in filters and filters[key] != value:
            errors[original_key] = 'Противоречивые значения одного фильтра'
        else:
            filters[key] = value

    return filters, errors

# Создает нового студента
def create_student(data):
    """Создает cтудента"""
    errors = validate(data) # Валидация
    if errors:
        return None, errors, 422  # 422 Unprocessable Entity (ошибка валидации)

    data = dict(data)
    data['isu'] = int(data['isu'])
    data['dorm'] = int(data['dorm'])

    if storage.get_by_isu(data['isu']): # Проверка на дубликат ИСУ
        return None, {'isu': 'Студент с таким ИСУ уже существует'}, 409  # 409 Conflict

    student = storage.add(data) # Сохранение
    return student, None, 201  # 201 Created

# Обновляет данные студента (частично или полностью)
def update_student(isu, data):
    """Обновляет данные студента"""
    existing = storage.get_by_isu(isu)
    if not existing:
        return None, {'error': 'Студент не найден'}, 404  # 404 Not Found

    errors = validate(data, is_update=True) # Валидация (is_update=True, чтобы не требовать все поля)
    if errors:
        return None, errors, 422

    data = dict(data)
    for field in ('isu', 'dorm'):
        if field in data:
            data[field] = int(data[field])

    # Если меняем ИСУ, проверяем, не занят ли новый ИСУ
    if 'isu' in data and data['isu'] != isu:
        if storage.get_by_isu(data['isu']):
            return None, {'isu': 'Студент с таким ИСУ уже существует'}, 409

    student = storage.update(isu, data) # Сохранение
    return student, None, 200  # 200 OK

def delete_student(isu):
    """Удаляет студента"""
    existing = storage.get_by_isu(isu)
    if not existing:
        return None, 404  # 404 Not Found

    storage.delete(isu)
    return None, 204  # 204 No Content (успешно, но тело ответа пустое)
