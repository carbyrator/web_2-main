"""Правила проверки студента и фильтров, а также операции с проверкой ИСУ."""

import re
from datetime import date
import storage

def validate_student(data, is_update=False):
    """Возвращает словарь ошибок полей; пустой словарь означает успех."""
    errors = {}

    # При создании нужны все основные поля; при PATCH проверяем только присланные.
    if not is_update:
        required = ['name', 'group', 'isu', 'dorm', 'room', 'expDate', 'foreigner']
        for field in required:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                errors[field] = 'Обязательное поле'

    # fullmatch требует соответствия всей строки, а не только её части.
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
        # bool исключаем отдельно: в Python это подкласс int.
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
        # Неверную календарную дату date.fromisoformat сообщает через ValueError.
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


# Клиент может фильтровать только по свойствам модели студента.
FILTER_FIELDS = {'name', 'group', 'isu', 'dorm', 'room', 'expDate', 'foreigner', 'notes'}


def normalize_filters(raw_filters):
    """Проверяет фильтры GET/QUERY и приводит числа и флаги к нужным типам."""
    filters = {}
    errors = {}
    for original_key, value in raw_filters.items():
        # В примере ТЗ поле называется dormitory, в модели проекта — dorm.
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
            # В URL всё приходит строками; "false" должен стать Python False.
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
            # Например, dorm=8 и dormitory=9 задают разные значения одного поля.
            errors[original_key] = 'Противоречивые значения одного фильтра'
        else:
            filters[key] = value

    return filters, errors


def create_student(data):
    """Проверяет нового студента; возвращает (студент, ошибки, HTTP-код)."""
    errors = validate_student(data)
    if errors:
        return None, errors, 422

    # Копия не меняет исходный словарь запроса; числовые поля храним как int.
    student = dict(data)
    student['isu'] = int(student['isu'])
    student['dorm'] = int(student['dorm'])
    # ИСУ — уникальный идентификатор, поэтому дубликат не сохраняем.
    if storage.get_by_isu(student['isu']) is not None:
        return None, {'isu': 'Студент с таким ИСУ уже существует'}, 409
    return storage.add(student), None, 201


def update_student(isu, data):
    """Проверяет PATCH и возвращает (студент, ошибки, HTTP-код)."""
    if storage.get_by_isu(isu) is None:
        return None, {'error': 'Студент не найден'}, 404

    errors = validate_student(data, is_update=True)
    if errors:
        return None, errors, 422

    # В updates остаются только поля из запроса: остальные свойства сохранятся.
    updates = dict(data)
    for field in ('isu', 'dorm'):
        if field in updates:
            updates[field] = int(updates[field])

    if 'isu' in updates and updates['isu'] != isu:
        # Новый ИСУ допустим, только если он ещё не занят другим студентом.
        if storage.get_by_isu(updates['isu']) is not None:
            return None, {'isu': 'Студент с таким ИСУ уже существует'}, 409

    student = storage.update(isu, updates)
    if student is None:
        return None, {'error': 'Студент не найден'}, 404
    return student, None, 200


def delete_student(isu):
    """Удаляет найденного студента; возвращает (None, HTTP-код)."""
    if storage.get_by_isu(isu) is None or not storage.delete(isu):
        return None, 404
    return None, 204
