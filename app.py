import requests
from flask import Flask, render_template, request, Response
from flask_cors import CORS  # Импортируем CORS

app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех источников (можно настроить более детально)

API_KEY = "ceb849cff8msh123f466bfb728a8p16578ajsn40f5d50ec450"
API_URL = "https://save-insta1.p.rapidapi.com/media"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "save-insta1.p.rapidapi.com",
    "Content-Type": "application/json"
}

# Функция для получения ссылки на видео
def get_video_url(instagram_url):
    payload = { "url": instagram_url }
    try:

        print(f"Sending request to API with URL: {instagram_url}")

        response = requests.post(API_URL, json=payload, headers=headers)
        response.raise_for_status()  # выбрасывает исключение при ошибке запроса

        response_json = response.json()
        print(f"API Response: {response_json}")  # Логируем полный ответ API для диагностики

        if response_json.get('success') and 'result' in response_json:
            video_url = response_json['result'][0]['urls'][0]['url']
            return video_url
        else:
            print("Ошибка: Не удалось получить ссылку на видео.")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
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
        return "Please provide a valid URL", 400

    print(f"Received URL: {url}")
    
    # Форматируем URL, чтобы он всегда был в правильной форме
    url = url.replace("https://www.instagram.com/reels/", "https://www.instagram.com/reel/")  # Приводим к единому формату
    url = url.replace("https://www.instagram.com/p/", "https://www.instagram.com/reel/")
    url = url.replace("https://www.instagram.com/share/reel/", "https://www.instagram.com/reel/")

    # Проверяем, что URL правильный
    if not url.startswith("https://www.instagram.com/reel/"):
        return "Invalid Instagram Reels URL format", 400

    video_url = get_video_url(url)
    if not video_url:
        return "Failed to retrieve video URL", 500

    try:
        # Загружаем видео, но теперь не в память, а непосредственно в поток
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()

        # Используем Response для потоковой передачи данных в реальном времени
        return Response(video_response.iter_content(chunk_size=1024),
                        content_type='video/mp4',
                        status=200,
                        headers={'Content-Disposition': 'attachment; filename="video.mp4"'})

    except requests.exceptions.RequestException as e:
        print(f"Ошибка загрузки видео: {e}")
        return f"Failed to download video: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
