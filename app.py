import requests
from flask import Flask, request, render_template

app = Flask(__name__)

def download_instagram_reel(insta_url):
    snapinsta_api = "https://snapinsta.app/action"
    data = {"url": insta_url}
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.post(snapinsta_api, data=data, headers=headers)
    if response.ok:
        return response.text  # Здесь будет ссылка на скачивание видео
    return None

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        insta_url = request.form["url"]
        video_url = download_instagram_reel(insta_url)
        return f"<a href='{video_url}'>Скачать видео</a>" if video_url else "Ошибка!"

    return '''
        <form method="post">
            <input type="text" name="url" placeholder="Вставьте ссылку на Reels">
            <button type="submit">Скачать</button>
        </form>
    '''

if __name__ == "__main__":
    app.run(debug=True)
