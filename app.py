from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)  # Создаем папку для видео, если её нет

def download_instagram_reel(url):
    output_path = os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_path,
        'merge_output_format': 'mp4',
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        return filename  # Возвращаем путь к скачанному видео

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        video_url = request.form.get("video_url")
        if video_url:
            try:
                file_path = download_instagram_reel(video_url)
                return send_file(file_path, as_attachment=True)  # Отправляем файл пользователю
            except Exception as e:
                return f"Ошибка при загрузке: {e}"
    
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)

