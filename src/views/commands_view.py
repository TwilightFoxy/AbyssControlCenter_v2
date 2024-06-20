import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QGridLayout, QHBoxLayout, QSpacerItem, QSizePolicy
from PyQt6.QtCore import QThread, pyqtSignal
from twitchio.ext import commands
import asyncio
import json
from cryptography.fernet import Fernet
SETTINGS_PATH = "data/settings.json"
DATA_DIR = "data"

class CommandsView(QWidget):
    connection_status_signal = pyqtSignal(str)

    def __init__(self, queue_view):
        super().__init__()
        self.queue_view = queue_view

        self.init_ui()
        self.connect_signals()
        self.load_commands()

    # Инициализация пользовательского интерфейса
    def init_ui(self):
        layout = QVBoxLayout()

        # Информация о подключении
        self.connection_info_label = QLabel("Информация о подключении")
        self.connection_status = QLabel("Статус: не подключен")

        connection_layout = QVBoxLayout()
        connection_layout.addWidget(self.connection_info_label)
        connection_layout.addWidget(self.connection_status)
        connection_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Название канала
        self.channel_label = QLabel("Название канала")
        self.channel_input = QLineEdit()

        # Кнопки управления
        self.save_button = QPushButton("Сохранить")
        self.start_bot_button = QPushButton("Запустить бота")
        self.stop_bot_button = QPushButton("Остановить бота")

        # Сетка для организации кнопок и ввода
        button_layout = QGridLayout()
        button_layout.addWidget(self.channel_label, 0, 0)
        button_layout.addWidget(self.channel_input, 0, 1)
        button_layout.addWidget(self.save_button, 1, 0)
        button_layout.addWidget(self.start_bot_button, 1, 1)
        button_layout.addWidget(self.stop_bot_button, 2, 0, 1, 2)

        # Команды и описание
        self.commands_label = QLabel("Команды")
        self.commands_description = QLabel("!очередь - показать текущую очередь")

        layout.addLayout(connection_layout)
        layout.addWidget(self.commands_label)
        layout.addWidget(self.commands_description)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    # Подключение сигналалов к слотам
    def connect_signals(self):
        self.save_button.clicked.connect(self.save_commands)
        self.start_bot_button.clicked.connect(self.start_twitch_bot)
        self.stop_bot_button.clicked.connect(self.stop_twitch_bot)

    # Шифрование данных
    def encrypt(self, data):
        f = self.get_fernet()
        return f.encrypt(data.encode()).decode()

    # Дешифрование данных
    def decrypt(self, data):
        f = self.get_fernet()
        return f.decrypt(data.encode()).decode()

    # Загрузка ключа шифрования
    def load_key(self):
        key_path = os.path.join(DATA_DIR, "secret.key")
        if os.path.exists(key_path):
            with open(key_path, "rb") as key_file:
                return key_file.read()
        key = self.generate_key()
        with open(key_path, "wb") as key_file:
            key_file.write(key)
        return key

    # Генерация ключа шифрования
    def generate_key(self):
        return Fernet.generate_key()

    # Получение объекта Fernet для шифрования и дешифрования
    def get_fernet(self):
        if not hasattr(self, '_fernet'):
            self._fernet = Fernet(self.load_key())
        return self._fernet

    # Сохранение настроек команд в файл
    def save_commands(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
        else:
            settings = {}
        settings["channel"] = self.channel_input.text()
        with open(SETTINGS_PATH, "w") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)

    # Загрузка настроек команд из файла
    def load_commands(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
                self.channel_input.setText(settings.get("channel", ""))
                encrypted_token = settings.get("auth_token", "")
                if encrypted_token:
                    self.auth_token = self.decrypt(encrypted_token)
                else:
                    self.auth_token = ""

    # Запуск Twitch бота в отдельном потоке
    def start_twitch_bot(self):
        channel = self.channel_input.text()
        self.thread = BotThread(self.queue_view, channel, self.auth_token)
        self.thread.connection_status_signal.connect(self.update_connection_status)
        self.thread.start()

    # Остановка Twitch бота
    def stop_twitch_bot(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.terminate()
            self.update_connection_status("Статус: не подключен")

    # Обновление статуса подключения
    def update_connection_status(self, status):
        self.connection_status.setText(status)

class BotThread(QThread):
    connection_status_signal = pyqtSignal(str)

    def __init__(self, queue_view, channel, auth_token):
        super().__init__()
        self.queue_view = queue_view
        self.channel = channel
        self.auth_token = auth_token

    # Запуск Twitch бота в новом событии loop
    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.bot = TwitchBot(self.queue_view, self.channel, self.auth_token, self.connection_status_signal)
        loop.run_until_complete(self.bot.start())

class TwitchBot(commands.Bot):
    def __init__(self, queue_view, channel, auth_token, connection_status_signal):
        super().__init__(token=auth_token, prefix='!', initial_channels=[channel])
        self.queue_view = queue_view
        self.channel = channel
        self.connection_status_signal = connection_status_signal

    # Событие, срабатывающее при подключении бота
    async def event_ready(self):
        status = f'Подключен к каналу {self.channel} как {self.nick}'
        self.connection_status_signal.emit(status)

    # Команда для отображения очереди
    @commands.command(name='очередь')
    async def my_command(self, ctx):
        current_vip_queue = self.get_queue_text(self.queue_view.current_vip_table, "Вип очередь")
        current_regular_queue = self.get_queue_text(self.queue_view.current_regular_table, "Обычная очередь")
        next_vip_queue = self.get_queue_text(self.queue_view.next_vip_table, "Следующая Вип очередь")
        next_regular_queue = self.get_queue_text(self.queue_view.next_regular_table, "Следующая Обычная очередь")

        message_parts = [current_vip_queue, current_regular_queue, next_vip_queue, next_regular_queue]
        message_parts = [part for part in message_parts if part]

        message = "\n\n".join(message_parts) if message_parts else "Очередь пуста."

        await ctx.reply(message)

    # Получение текста очереди из таблицы
    def get_queue_text(self, table, title):
        queue_text = []
        for row in range(table.rowCount()):
            name_item = table.item(row, 0)
            status_item = table.item(row, 1)
            if name_item and status_item and status_item.text() != "Выполнено":
                queue_text.append(f" {name_item.text()}")

        if queue_text:
            return f"{title}:\n" + ",\n".join(queue_text)
        return ""
