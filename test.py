import requests

url = "https://instagram-reels-downloader-api.p.rapidapi.com/download"

querystring = {"url":"https://www.instagram.com/reel/DCxTlFwSJ_Y/"}

headers = {
	"x-rapidapi-key": "ceb849cff8msh123f466bfb728a8p16578ajsn40f5d50ec450",
	"x-rapidapi-host": "instagram-reels-downloader-api.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())

input("\nНажмите Enter, чтобы закрыть...")