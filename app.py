import os
import subprocess
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def download():
    if request.method == "POST":
        url = request.form.get("url")
        if url:
            filename = "video.mp4"  # Название скачиваемого файла
            command = ["yt-dlp", "-o", filename, url]

            try:
                subprocess.run(command, check=True)
                return send_file(filename, as_attachment=True)
            except subprocess.CalledProcessError:
                return "Ошибка скачивания!", 500

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
