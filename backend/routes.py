"""HTTP-маршруты API: читают запросы и возвращают JSON с нужным статусом."""

from flask import Blueprint, request, jsonify
import validate
import storage

# Blueprint регистрируется в app.py и объединяет все маршруты /api/requests.
api = Blueprint('api', __name__)


def error_response(message, status, details=None):
    """Единый формат ошибок: сообщение и ошибки отдельных полей."""
    return jsonify({"error": {"message": message, "details": details or {}}}), status


def json_object(allow_empty=False):
    """Читает JSON-тело и убеждается, что клиент прислал объект, а не список."""
    if not request.is_json:
        return None, error_response('Ожидался JSON-объект', 400)
    # silent=True даёт None при повреждённом JSON вместо исключения Flask.
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or (not allow_empty and not data):
        return None, error_response('Ожидался непустой JSON-объект' if not allow_empty else 'Некорректный JSON-объект', 400)
    return data, None


def checked_filters(raw_filters):
    """Проверяет имена и значения фильтров до обращения к хранилищу."""
    filters, errors = validate.normalize_filters(raw_filters)
    if errors:
        return None, error_response('Некорректные фильтры', 422, errors)
    return filters, None


def student_error(errors, status):
    """Преобразует результат проверки студента в понятный HTTP-ответ."""
    if status == 404:
        return error_response('Студент не найден', status)
    if status == 409:
        return error_response('Студент с таким ИСУ уже существует', status, errors)
    return error_response('Некорректные данные студента', status, errors)


@api.route('/api/requests', methods=['GET'])
def get_students():
    """Возвращает весь список либо список с фильтрами из URL после ?."""
    filters, error = checked_filters(request.args.to_dict())
    if error:
        return error
    students = storage.filter_students(filters) if filters else storage.get_all()
    return jsonify(students), 200

@api.route('/api/requests', methods=['QUERY'])
def query_studens():
    """Получает фильтры из JSON-тела, когда передавать их в URL неудобно."""
    data, error = json_object(allow_empty=True)
    if error:
        return error
    filters, error = checked_filters(data)
    if error:
        return error
    return jsonify(storage.filter_students(filters)), 200

@api.route('/api/requests/<int:isu>', methods=['GET'])
def get_student(isu):
    """Ищет одного студента по ИСУ из адреса запроса."""
    student = storage.get_by_isu(isu)
    if student is None:
        return error_response('Студент не найден', 404)
    return jsonify(student), 200

@api.route('/api/requests', methods=['POST'])
def create_student():
    """Принимает нового студента, проверяет его и возвращает код 201."""
    data, error = json_object()
    if error:
        return error
    student, errors, status = validate.create_student(data)
    if errors:
        return student_error(errors, status)
    return jsonify(student), status

@api.route('/api/requests/<int:isu>', methods=['PATCH'])
def update_student(isu):
    """Обновляет только переданные поля студента с указанным ИСУ."""
    data, error = json_object()
    if error:
        return error
    student, errors, status = validate.update_student(isu, data)
    if errors:
        return student_error(errors, status)
    return jsonify(student), status

@api.route('/api/requests/<int:isu>', methods=['DELETE'])
def delete_student(isu):
    """Удаляет студента; код 204 означает успешный ответ без тела."""
    # Первое значение результата здесь не нужно: достаточно HTTP-статуса.
    _, status = validate.delete_student(isu)
    if status == 404:
        return error_response('Студент не найден', 404)
    return '', 204
