from flask import request
import json
from datetime import datetime

# Функция для записи посещений
def log_visitor():
    # Получаем IP-адрес пользователя
    ip_address = request.remote_addr
    
    # Получаем информацию о User-Agent
    user_agent = request.headers.get('User-Agent')
    
    # Записываем время посещения
    visit_time = datetime.now().isoformat()
    
    visitor_info = {
        "ip_address": ip_address,
        "user_agent": user_agent,
        "visit_time": visit_time
    }

    # Загружаем существующих посетителей из файла
    try:
        with open('visitors.json', 'r') as file:
            visitors = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        visitors = []

    # Проверяем, есть ли уже такой IP в списке
    existing_visitor = next((visitor for visitor in visitors if visitor['ip_address'] == ip_address), None)

    if not existing_visitor:
        # Если посетителя с таким IP нет, добавляем нового
        visitors.append(visitor_info)

        # Сохраняем обновленный список посетителей
        with open('visitors.json', 'w') as file:
            json.dump(visitors, file, indent=4)

# Функция для отслеживания посетителей
def track_visitor(app):
    @app.before_request
    def track():
        log_visitor()
