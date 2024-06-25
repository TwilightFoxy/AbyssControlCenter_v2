from PyQt6.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel
import json
import os

from .commands_view import CommandsView
from .queue_view import QueueView
from .settings_view import SettingsView

SETTINGS_PATH = "data/settings.json"

class MainView(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AbyssControlCenter_v0.3")

        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.queue_view = QueueView()
        self.add_tabs()
        self.adjustSize()

        self.load_settings()

    # Добавление вкладок в интерфейс
    def add_tabs(self):
        self.main_tab = self.create_main_tab()
        self.commands_view = CommandsView(self.queue_view)
        self.settings_view = SettingsView()

        self.tabs = [
            ("Главная", self.main_tab),
            ("Команды", self.commands_view),
            ("Очередь", self.queue_view),
            ("Настройки", self.settings_view)
        ]

        for tab_name, tab_widget in self.tabs:
            self.tab_widget.addTab(tab_widget, tab_name)

    # Создание главной вкладки
    def create_main_tab(self):
        main_tab = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Состояние модулей"))
        layout.addWidget(QLabel("Здесь будет отображаться состояние каждого модуля"))
        main_tab.setLayout(layout)
        return main_tab

    # Загрузка настроек из файла
    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
                startup_tab = settings.get("startup_tab", "Главная")
                self.set_startup_tab(startup_tab)
                self.hide_tabs(settings)
                window_width = settings.get("window_width", 1100)
                window_height = settings.get("window_height", 800)
                self.resize(window_width, window_height)

    # Установка начальной вкладки
    def set_startup_tab(self, tab_name):
        tab_index = {
            "Главная": 0,
            "Команды": 1,
            "Очередь": 2,
            "Настройки": 3
        }.get(tab_name, 0)
        self.tab_widget.setCurrentIndex(tab_index)

    # Скрытие вкладок в соответствии с настройками
    def hide_tabs(self, settings):
        hide_main = settings.get("hide_main", False)
        hide_commands = settings.get("hide_commands", False)
        hide_queue = settings.get("hide_queue", False)

        if hide_main:
            self.tab_widget.removeTab(self.tab_widget.indexOf(self.main_tab))
        if hide_commands:
            self.tab_widget.removeTab(self.tab_widget.indexOf(self.commands_view))
        if hide_queue:
            self.tab_widget.removeTab(self.tab_widget.indexOf(self.queue_view))
