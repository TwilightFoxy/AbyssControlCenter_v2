import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка необходимых модулей
required_packages = [
    "PyQt5",
    # Добавьте сюда другие необходимые пакеты
]

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install(package)

from PyQt5.QtWidgets import QApplication
from twitch_bot_ui import TwitchBotApp

def main():
    app = QApplication(sys.argv)
    window = TwitchBotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
