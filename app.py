import requests
from flask import Flask, render_template, request, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех источников

API_KEY = "ceb849cff8msh123f466bfb728a8p16578ajsn40f5d50ec450"
API_URL = "https://save-insta1.p.rapidapi.com/media"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "save-insta1.p.rapidapi.com",
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# Функция для получения ссылки на видео
def get_video_url(instagram_url):
    payload = {"url": instagram_url}
    try:
        print(f"🔍 Отправка запроса на API с URL: {instagram_url}")
        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()

        response_json = response.json()
        print(f"📜 API Response (JSON): {response_json}")  # Логируем полный JSON-ответ

        if response_json.get('success') and 'result' in response_json:
            video_url = response_json['result'][0]['urls'][0]['url']
            print(f"🎯 Найдено видео: {video_url}")
            return video_url
        else:
            print("⚠ Ошибка: Не удалось получить ссылку на видео.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка запроса: {e}")
        return None

# Главная страница
@app.route('/')
def index():
    return render_template('index.html')

# Страница скачивания
@app.route('/download', methods=['GET'])
def download_video():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "Please provide a valid URL"}), 400

    print(f"📥 Полученный URL: {url}")

    # Приведение URL к единому формату
    url = url.replace("https://www.instagram.com/reels/", "https://www.instagram.com/reel/")
    url = url.replace("https://www.instagram.com/p/", "https://www.instagram.com/reel/")
    url = url.replace("https://www.instagram.com/share/reel/", "https://www.instagram.com/reel/")

    # Проверяем корректность URL
    if not url.startswith("https://www.instagram.com/reel/"):
        return jsonify({"error": "Invalid Instagram Reels URL format"}), 400

    video_url = get_video_url(url)
    if not video_url:
        return jsonify({"error": "Failed to retrieve video URL"}), 500

    try:
        # Загружаем видео в потоковом режиме
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()

        print("📤 Отправка видео пользователю...")
        return Response(
            video_response.iter_content(chunk_size=1024),
            content_type="video/mp4",
            status=200,
            headers={"Content-Disposition": "attachment; filename=video.mp4"}
        )
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка загрузки видео: {e}")
        return jsonify({"error": f"Failed to download video: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
