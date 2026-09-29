# импорты
from pathlib import Path
from flask import Flask, request, send_from_directory #фреймворк + функция для раздачи файлов из папки
from werkzeug.exceptions import HTTPException, InternalServerError
from routes import api, error_response # blueprint маршруты

PROJECT_ROOT = Path(__file__).resolve().parent.parent
app = Flask(__name__, static_folder=None) # созд приложение

app.register_blueprint(api) # Подключаем все эндпоинты из routes.py (GET, POST, PATCH, DELETE, QUERY)


@app.errorhandler(HTTPException)
def handle_http_error(error):
    if request.path.startswith('/api/'):
        return error_response(error.description, error.code)
    return error


@app.errorhandler(InternalServerError)
def handle_server_error(error):
    if request.path.startswith('/api/'):
        return error_response('Внутренняя ошибка сервера', 500)
    return error

# отдаем html при запуске
@app.route('/')
@app.route('/index.html')
def index():
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/form.html')
def form_page():
    return send_from_directory(PROJECT_ROOT, 'form.html')

@app.route('/student.html')
def student_page():
    return send_from_directory(PROJECT_ROOT, 'student.html')

# подгружаем стили, js и иконку
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
    app.run(port=5000)
