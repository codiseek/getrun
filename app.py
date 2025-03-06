import logging
import requests
from flask import Flask, render_template, request, Response
from flask_cors import CORS  

app = Flask(__name__)
CORS(app)  

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

API_KEY = "ceb849cff8msh123f466bfb728a8p16578ajsn40f5d50ec450"
API_URL = "https://instagram-post-reels-stories-downloader-api.p.rapidapi.com/instagram/"

headers = {
    "x-rapidapi-key": API_KEY,
    "x-rapidapi-host": "instagram-post-reels-stories-downloader-api.p.rapidapi.com"
}

# Функция для получения ссылки на видео
def get_video_url(instagram_url):
    try:
        logger.info(f"🔍 Отправка запроса на API с URL: {instagram_url}")
        
        params = {"url": instagram_url}
        response = requests.get(API_URL, headers=headers, params=params)
        response.raise_for_status()  
        
        response_json = response.json()
        logger.info(f"📜 API Response: {response_json}")
        
        if response_json.get("success") and "data" in response_json:
            medias = response_json["data"].get("medias", [])
            if medias and isinstance(medias, list):
                video_url = medias[0]["url"]
                logger.info(f"✅ Найдена ссылка на видео: {video_url}")
                return video_url
        
        logger.warning("⚠ Ошибка: Не удалось получить ссылку на видео.")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка запроса: {e}")
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
        logger.warning("⚠ Не передан URL в запросе")
        return "Please provide a valid URL", 400

    logger.info(f"📥 Полученный URL: {url}")
    
    # Приведение URL к единому формату
    url = url.replace("https://www.instagram.com/reels/", "https://www.instagram.com/reel/")  
    url = url.replace("https://www.instagram.com/p/", "https://www.instagram.com/reel/")
    url = url.replace("https://www.instagram.com/share/reel/", "https://www.instagram.com/reel/")

    if not url.startswith("https://www.instagram.com/reel/"):
        logger.warning("⚠ Некорректный формат URL")
        return "Invalid Instagram Reels URL format", 400

    video_url = get_video_url(url)
    if not video_url:
        return "Failed to retrieve video URL", 500

    try:
        logger.info(f"📡 Скачивание видео с URL: {video_url}")
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()
        
        logger.info("✅ Видео успешно загружено")
        return Response(video_response.iter_content(chunk_size=1024),
                        content_type='video/mp4',
                        status=200,
                        headers={'Content-Disposition': 'attachment; filename="video.mp4"'})
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Ошибка загрузки видео: {e}")
        return f"Failed to download video: {e}", 500

if __name__ == "__main__":
    app.run(debug=True)
