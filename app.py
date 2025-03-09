import os
import json
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PREVIEW_FOLDER = 'static/previews'
CONFIG_FILE = 'config.json'
PASSWORD = 'x0000'

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
    
    if request.method == "POST":
        file = request.files.get("file")
        preview = request.files.get("preview")
        description = request.form.get("description", "")
        formats = request.form.get("formats", "")
        downloads = request.form.get("downloads", 0)
        
        if file and file.filename.endswith(".zip"):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            preview_filename = ""
            if preview and preview.filename:
                preview_filename = secure_filename(preview.filename)
                preview.save(os.path.join(PREVIEW_FOLDER, preview_filename))
            
            files = load_config()
            new_id = len(files) + 1  # ID для нового файла
            files.append({
                "id": new_id,  # Добавляем id
                "name": filename,
                "description": description,
                "preview": preview_filename,
                "formats": formats,  # Добавляем поле форматов
                "downloads": downloads
            })
            save_config(files)
            
            return redirect(url_for("admin", password=PASSWORD))
    
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


if __name__ == "__main__":
    app.run(debug=True)
