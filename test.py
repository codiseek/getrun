import requests

url = "https://save-insta1.p.rapidapi.com/media"

payload = { "url": "https://www.instagram.com/reel/DCz0WwWNJ9U/" }
headers = {
    "x-rapidapi-key": "ceb849cff8msh123f466bfb728a8p16578ajsn40f5d50ec450",
    "x-rapidapi-host": "save-insta1.p.rapidapi.com",
    "Content-Type": "application/json"
}

try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()  # Это выбросит исключение, если статус ответа не 200

    # Проверяем, если ответ в формате JSON
    if response.status_code == 200:
        print(response.json())  # Выводим JSON-ответ
    else:
        print(f"Ошибка: {response.status_code}")
        print(response.text)  # Печатаем текст ошибки от API

except requests.exceptions.RequestException as e:
    print(f"Ошибка запроса: {e}")


input("\nНажмите Enter, чтобы закрыть...")