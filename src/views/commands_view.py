import os
import json
import asyncio
import threading  # Добавляем импорт threading
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QGridLayout
from PyQt6.QtCore import QThread, pyqtSignal
from twitchio.ext import commands
from src.utils.rewards_tracker import RewardsTracker  # Импортируем RewardsTracker

SETTINGS_PATH = "data/settings.json"

class CommandsView(QWidget):
    connection_status_signal = pyqtSignal(str)

    def __init__(self, queue_view):
        super().__init__()
        self.queue_view = queue_view
        self.init_ui()
        self.connect_signals()
        self.load_commands()

    def init_ui(self):
        layout = QVBoxLayout()

        self.connection_info_label = QLabel("Информация о подключении")
        self.connection_status = QLabel("Статус: не подключен")

        self.start_bot_button = QPushButton("Подключиться")
        self.stop_bot_button = QPushButton("Отключиться")

        button_layout = QGridLayout()
        button_layout.addWidget(self.start_bot_button, 0, 0)
        button_layout.addWidget(self.stop_bot_button, 0, 1)

        self.commands_label = QLabel("Команды")
        self.commands_description = QLabel("!очередь - показать текущую очередь")

        layout.addWidget(self.connection_info_label)
        layout.addWidget(self.connection_status)
        layout.addLayout(button_layout)
        layout.addWidget(self.commands_label)
        layout.addWidget(self.commands_description)

        self.setLayout(layout)

    def connect_signals(self):
        self.start_bot_button.clicked.connect(self.start_twitch_bot)
        self.stop_bot_button.clicked.connect(self.stop_twitch_bot)

    def load_commands(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
                self.channel = settings.get("channel", "")
                self.auth_token = settings.get("auth_token", "")
                self.client_id = settings.get("client_id", "")
                self.user_id = settings.get("user_id", "")
                self.use_bot = settings.get("use_bot", True)
                self.enable_rewards = settings.get("enable_rewards", False)
                self.reward_selectors = settings.get("reward_selectors", {})
                self.rewards_checked = settings.get("rewards_checked", False)

    def start_twitch_bot(self):
        self.load_commands()  # Загружаем настройки при запуске бота
        if self.use_bot:
            token = self.auth_token
        else:
            token = self.bot_auth_token

        self.thread = BotThread(self.queue_view, self.channel, token, self.enable_rewards, self.reward_selectors)
        self.thread.connection_status_signal.connect(self.update_connection_status)
        self.thread.start()

        if self.enable_rewards:
            self.rewards_tracker = RewardsTracker(self.user_id, self.client_id, self.auth_token, self.queue_view, self.reward_selectors)
            self.rewards_tracker_thread = threading.Thread(target=self.rewards_tracker.start)
            self.rewards_tracker_thread.start()

    def stop_twitch_bot(self):
        if hasattr(self, 'thread') and self.thread.isRunning():
            self.thread.terminate()
            self.update_connection_status("Статус: не подключен")

        if hasattr(self, 'rewards_tracker'):
            self.rewards_tracker.stop()

    def update_connection_status(self, status):
        self.connection_status.setText(status)

class BotThread(QThread):
    connection_status_signal = pyqtSignal(str)

    def __init__(self, queue_view, channel, token, enable_rewards, reward_selectors):
        super().__init__()
        self.queue_view = queue_view
        self.channel = channel
        self.token = token
        self.enable_rewards = enable_rewards
        self.reward_selectors = reward_selectors

    def run(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.bot = TwitchBot(self.queue_view, self.channel, self.token, self.connection_status_signal, self.enable_rewards, self.reward_selectors)
        loop.run_until_complete(self.bot.start())

class TwitchBot(commands.Bot):
    def __init__(self, queue_view, channel, token, connection_status_signal, enable_rewards, reward_selectors):
        super().__init__(token=token, prefix='!', initial_channels=[channel])
        self.queue_view = queue_view
        self.channel = channel
        self.connection_status_signal = connection_status_signal
        self.enable_rewards = enable_rewards
        self.reward_selectors = reward_selectors

    async def event_ready(self):
        status = f'Подключен к каналу {self.channel} как {self.nick}'
        self.connection_status_signal.emit(status)

    @commands.command(name='очередь')
    async def my_command(self, ctx):
        current_vip_queue = self.get_queue_text(self.queue_view.current_vip_table, "Вип очередь")
        current_regular_queue = self.get_queue_text(self.queue_view.current_regular_table, "Обычная очередь")
        next_vip_queue = self.get_queue_text(self.queue_view.next_vip_table, "Следующая Вип очередь")
        next_regular_queue = self.get_queue_text(self.queue_view.next_regular_table, "Следующая Обычная очередь")

        message_parts = []
        if current_vip_queue:
            message_parts.append(current_vip_queue)
        if current_regular_queue:
            message_parts.append(current_regular_queue)
        if next_vip_queue:
            message_parts.append(next_vip_queue)
        if next_regular_queue:
            message_parts.append(next_regular_queue)

        message = " | ".join(message_parts) if message_parts else "Очередь пуста."

        settings = self.queue_view.load_settings()
        table_link = settings.get("table_link", "")

        if table_link:
            message += f" | Ссылка на полную таблицу: {table_link}"

        print(f"Длина сообщения: {len(message)}")
        print(f"Сообщение: {message}")

        if len(message) > 250:
            message = f"Ссылка на полную таблицу: {table_link}"

        await ctx.reply(message)

    def get_queue_text(self, table, title):
        queue_text = []
        for row in range(table.rowCount()):
            name_item = table.item(row, 0)
            status_item = table.item(row, 1)
            if name_item and status_item and status_item.text() != "Выполнено":
                queue_text.append(f"{name_item.text()}")

        if queue_text:
            return f"{title}: " + ", ".join(queue_text)
        return ""

    async def event_message(self, message):
        if message.author is None:
            return
        await self.handle_commands(message)
        if self.enable_rewards and message.tags.get('custom-reward-id'):
            await self.handle_reward(message)

    async def handle_reward(self, message):
        reward_id = message.tags['custom-reward-id']
        user_input = message.content
        reward_title = next((title for title, id in self.reward_selectors.items() if id == reward_id), None)
        if reward_title:
            reward_action = self.reward_selectors[reward_title]
            if reward_action == "Бездна себе –":
                self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, message.author.name, "Бездна")
            elif reward_action == "Бездна другу –":
                self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_input, "Бездна",
                                             f'заказал {message.author.name}')
            elif reward_action == "Обзор себе –":
                self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, message.author.name, "Обзор")
            elif reward_action == "Обзор другу –":
                self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_input, "Обзор",
                                             f'заказал {message.author.name}')
            elif reward_action == "Театр себе –":
                self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, message.author.name, "Театр")
            elif reward_action == "Театр другу –":
                self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_input, "Театр",
                                             f'заказал {message.author.name}')
            self.queue_view.update_counts()
            self.queue_view.save_data()
            print(f"Reward '{reward_action}' purchased by {message.author.name}: {user_input}")
        else:
            print(f"Reward ID '{reward_id}' не найден в reward_selectors")

