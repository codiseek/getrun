import os
import json
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
import datetime
from visitor import track_visitor


app = Flask(__name__)
app.secret_key = os.urandom(24)
UPLOAD_FOLDER = 'uploads'
PREVIEW_FOLDER = 'static/previews'
CONFIG_FILE = 'config.json'
PASSWORD = '5Q88xLoo1'


track_visitor(app)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PREVIEW_FOLDER, exist_ok=True)

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return []
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = f.read().strip()
            return json.loads(data) if data else []
    except json.JSONDecodeError:
        return []

def save_config(data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Главная страница
@app.route("/")
def index():
    # Загружаем все файлы для главной страницы
    files = load_config()
    # Сортируем по ID, чтобы новые файлы были в начале
    files = sorted(files, key=lambda x: x['id'], reverse=True)

     # Получаем последний ID и суммарное количество скачиваний
    last_id = files[0]['id'] if files else 0
    total_downloads = sum(file.get('downloads', 0) for file in files)
    return render_template("index.html", files=files, last_id=last_id, total_downloads=total_downloads)



@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.args.get("password") != PASSWORD:
        return "Доступ запрещён", 403
    
    # Обработка POST запроса для загрузки файлов
    if request.method == "POST":
        file = request.files.get("file")
        preview = request.files.get("preview")
        svg = request.files.get("svg")
        description = request.form.get("description", "")
        formats = request.form.get("formats", "")
        downloads = int(request.form.get("downloads", 0))  # Преобразуем в целое число
        
        if file and file.filename.endswith(".zip"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            preview_filename = ""
            if preview and preview.filename:
                preview_filename = secure_filename(preview.filename)
                preview.save(os.path.join(PREVIEW_FOLDER, preview_filename))

            svg_filename = ""
            if svg and svg.filename:
                svg_filename = secure_filename(svg.filename)
                svg.save(os.path.join(PREVIEW_FOLDER, svg_filename))
            
            # Загружаем текущие файлы
            files = load_config()
            
            # Новый ID будет основан на длине списка файлов
            new_id = len(files) + 1  
            
            # Добавляем новый файл в список
            files.append({
                "id": new_id,  # ID нового файла
                "name": filename,
                "description": description,
                "preview": preview_filename,
                "svg": svg_filename,
                "formats": formats,
                "downloads": downloads
            })
            
            # Сохраняем обновленный список файлов
            save_config(files)
            
            # Перенаправляем обратно на страницу админки
            return redirect(url_for("admin", password=PASSWORD))

    # Загружаем все файлы для админки
    files = load_config()

    # Сортируем по ID, чтобы новые файлы были в начале
    files = sorted(files, key=lambda x: x['id'], reverse=True)

    # Получаем последний ID и суммарное количество скачиваний
    last_id = files[0]['id'] if files else 0
    total_downloads = sum(file.get('downloads', 0) for file in files)

    # Загружаем информацию о посетителях
    try:
        with open('visitors.json', 'r') as file:
            visitors = json.load(file)
        unique_visitors = len(visitors)  # Просто считаем количество всех посетителей
    except (FileNotFoundError, json.JSONDecodeError):
        unique_visitors = 0

    # Передаем файлы, последний ID, общее количество скачиваний и количество посетителей в шаблон
    return render_template("admin.html", files=files, last_id=last_id, total_downloads=total_downloads, unique_visitors=unique_visitors)

    
    files = load_config()
    files = sorted(files, key=lambda x: x['id'], reverse=True)  # Сортируем по ID, новые файлы сверху
    return render_template("admin.html", files=files, password=PASSWORD)



@app.route("/delete/<filename>", methods=["POST"])
def delete(filename):
    if request.form.get("password") != PASSWORD:
        return "Доступ запрещён", 403

    files = load_config()
    file_to_delete = next((f for f in files if f["name"] == filename), None)

    if file_to_delete:
        preview_filename = file_to_delete.get("preview")
        if preview_filename:
            preview_path = os.path.join(PREVIEW_FOLDER, preview_filename)
            if os.path.exists(preview_path):
                os.remove(preview_path)  # Удаляем превью, если оно есть

    files = [f for f in files if f["name"] != filename]
    save_config(files)

    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    return redirect(url_for("admin", password=PASSWORD))

@app.route("/uploads/<filename>")
def download_by_filename(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route("/download/<int:file_id>")
def download(file_id):
    # Загружаем список файлов
    files = load_config()

    # Находим файл по ID
    file_to_download = next((f for f in files if f["id"] == file_id), None)
    if file_to_download:
        # Увеличиваем счетчик скачиваний
        file_to_download["downloads"] += 1

        # Сохраняем обновленный список файлов
        save_config(files)

        # Переходим к загрузке файла
        return send_from_directory(UPLOAD_FOLDER, file_to_download["name"])
    else:
        return "Файл не найден", 404

SVG_FOLDER = 'static/svg'  # Добавляем папку для SVG
os.makedirs(SVG_FOLDER, exist_ok=True)  # Создаем, если её нет

@app.route('/edit_file', methods=['POST'])
def edit_file():
    original_name = request.form['original_name']
    new_description = request.form['description']
    new_formats = request.form['formats']
    new_file = request.files.get("new_file")  # Новый ZIP файл
    new_preview = request.files.get("new_preview")  # Новое превью
    new_svg = request.files.get("new_svg")  # Новое SVG

    files = load_config()

    for file in files:
        if file["name"] == original_name:
            file["description"] = new_description
            file["formats"] = new_formats

            # Обновление ZIP-файла
            if new_file and new_file.filename.endswith(".zip"):
                new_filename = secure_filename(new_file.filename)
                new_path = os.path.join(UPLOAD_FOLDER, new_filename)

                # Удаляем старый файл
                old_path = os.path.join(UPLOAD_FOLDER, file["name"])
                if os.path.exists(old_path):
                    os.remove(old_path)

                new_file.save(new_path)
                file["name"] = new_filename  # Обновляем имя файла в JSON

            # Обновление превью
            if new_preview and new_preview.filename:
                new_preview_filename = secure_filename(new_preview.filename)
                new_preview_path = os.path.join(PREVIEW_FOLDER, new_preview_filename)

                # Удаляем старое превью
                old_preview_path = os.path.join(PREVIEW_FOLDER, file["preview"])
                if os.path.exists(old_preview_path):
                    os.remove(old_preview_path)

                new_preview.save(new_preview_path)
                file["preview"] = new_preview_filename  # Обновляем имя превью в JSON

            # Обновление SVG (сохранение в static/previews)
            if new_svg and new_svg.filename.endswith(".svg"):
                new_svg_filename = secure_filename(new_svg.filename)
                new_svg_path = os.path.join(PREVIEW_FOLDER, new_svg_filename)  # Теперь в previews

                # Удаляем старый SVG, если он был
                old_svg_path = os.path.join(PREVIEW_FOLDER, file.get("svg", ""))
                if os.path.exists(old_svg_path):
                    os.remove(old_svg_path)

                new_svg.save(new_svg_path)
                file["svg"] = new_svg_filename  # Обновляем путь к SVG в JSON

            break  # Завершаем цикл после обновления

    
    save_config(files)
    flash('Файл успешно обновлен!', 'success')
    return redirect(url_for('admin', password=PASSWORD))


if __name__ == "__main__":
    app.run(debug=True)
