"""Точка входа: собирает Flask-приложение и отдаёт файлы клиенту."""

from pathlib import Path
from flask import Flask, request, send_from_directory
from werkzeug.exceptions import HTTPException, InternalServerError
from routes import api, error_response

# Python-файлы лежат в backend, а HTML, CSS, JS и students.json — на уровень выше.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, static_folder=None)

# Blueprint добавляет к приложению все API-маршруты из routes.py.
app.register_blueprint(api)


@app.errorhandler(HTTPException)
def handle_http_error(error):
    """Для ошибочного API-адреса возвращает JSON, для страниц — обычный ответ Flask."""
    if request.path.startswith('/api/'):
        return error_response(error.description, error.code)
    return error


@app.errorhandler(InternalServerError)
def handle_server_error(error):
    """Скрывает детали неожиданной ошибки сервера в ответе API."""
    if request.path.startswith('/api/'):
        return error_response('Внутренняя ошибка сервера', 500)
    return error

# Страницы открываются через Flask, чтобы браузер мог обращаться к API того же сервера.
@app.route('/')
@app.route('/index.html')
def index():
    """Главная страница со списком студентов."""
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/form.html')
def form_page():
    """Страница создания и редактирования студента."""
    return send_from_directory(PROJECT_ROOT, 'form.html')

@app.route('/student.html')
def student_page():
    """Страница с подробными данными одного студента."""
    return send_from_directory(PROJECT_ROOT, 'student.html')

# Эти маршруты отдают браузеру файлы оформления, скрипты и ресурсы страниц.
@app.route('/css/<path:filename>')
def css_files(filename):
    return send_from_directory(PROJECT_ROOT / 'css', filename)

@app.route('/js/<path:filename>')
def js_files(filename):
    return send_from_directory(PROJECT_ROOT / 'js', filename)

@app.route('/assets/<path:filename>')
def assets_files(filename):
    return send_from_directory(PROJECT_ROOT / 'assets', filename)

if __name__ == '__main__':
    # Запуск только при прямом выполнении: python backend/app.py.
    app.run(port=5000)
