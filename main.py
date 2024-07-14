import os
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.views.main_view import MainView
import json
import requests

# Путь к файлу настроек и директории данных
SETTINGS_PATH = "data/settings.json"
DATA_DIR = "data"

def authorize(client_id, client_secret):
    try:
        response = requests.post('https://id.twitch.tv/oauth2/token', data={
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        })
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.RequestException as e:
        print(f"Authorization failed: {e}")
        return None

# Применение стилей к приложению из файла QSS
def apply_styles(app):
    with open("src/assets/styles.qss", "r") as file:
        app.setStyleSheet(file.read())

# Загрузка настроек размеров окна из файла
def load_window_settings():
    if os.path.exists(SETTINGS_PATH):
        with open(SETTINGS_PATH, "r") as file:
            settings = json.load(file)
            return settings.get("window_width", 1100), settings.get("window_height", 800)
    return 1100, 800

# Основная функция запуска приложения
def main():
    app = QApplication(sys.argv)
    apply_styles(app)

    # Установка иконки приложения
    app.setWindowIcon(QIcon('src/assets/icons/main.png'))  # Укажите путь к иконке

    # Загрузка настроек окна
    window_width, window_height = load_window_settings()

    # Создание и настройка основного окна
    main_view = MainView()
    main_view.setWindowTitle("БезднаБотер 2.0")  # Установка заголовка приложения
    main_view.resize(window_width, window_height)
    main_view.show()

    # Запуск приложения
    sys.exit(app.exec())

if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    main()