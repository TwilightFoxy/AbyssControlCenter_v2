import os
import sys

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QCheckBox, QLineEdit
import json
from cryptography.fernet import Fernet

SETTINGS_PATH = "data/settings.json"
DATA_DIR = "data"

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.load_settings()

    # Инициализация пользовательского интерфейса
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Выбор начального раздела
        self.startup_tab_label = QLabel("Выберите начальный раздел")
        self.startup_tab_select = QComboBox()
        self.startup_tab_select.addItems(["Главная", "Команды", "Очередь", "Настройки"])

        # Чекбоксы для скрытия разделов
        self.hide_main_checkbox = QCheckBox("Скрыть Главная")
        self.hide_commands_checkbox = QCheckBox("Скрыть Команды")
        self.hide_queue_checkbox = QCheckBox("Скрыть Очередь")

        # Поля ввода для ширины и высоты окна
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Ширина окна (например, 1100)")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Высота окна (например, 800)")

        # Поле ввода для токена авторизации
        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Введите токен авторизации")
        self.token_input.setEchoMode(QLineEdit.EchoMode.Password)  # Скрытие ввода

        # Кнопка для сохранения настроек
        self.save_button = QPushButton("Сохранить настройки")

        # Layout для выбора начального раздела
        tab_selection_layout = QHBoxLayout()
        tab_selection_layout.addWidget(self.startup_tab_label)
        tab_selection_layout.addWidget(self.startup_tab_select)
        tab_selection_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # Добавление виджетов в основной layout
        self.layout.addLayout(tab_selection_layout)
        self.layout.addWidget(self.hide_main_checkbox)
        self.layout.addWidget(self.hide_commands_checkbox)
        self.layout.addWidget(self.hide_queue_checkbox)
        self.layout.addWidget(QLabel("Настройки размера окна"))
        self.layout.addWidget(self.width_input)
        self.layout.addWidget(self.height_input)
        self.layout.addWidget(QLabel("Токен авторизации"))
        self.layout.addWidget(self.token_input)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.save_button)

        # Подключение сигнала нажатия кнопки к слоту сохранения настроек
        self.save_button.clicked.connect(self.save_settings)

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

    # Шифрование данных
    def encrypt(self, data):
        f = self.get_fernet()
        return f.encrypt(data.encode()).decode()

    # Дешифрование данных
    def decrypt(self, data):
        f = self.get_fernet()
        return f.decrypt(data.encode()).decode()

    # Загрузка настроек из файла
    def load_settings(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
                self.startup_tab_select.setCurrentText(settings.get("startup_tab", "Главная"))
                self.hide_main_checkbox.setChecked(settings.get("hide_main", False))
                self.hide_commands_checkbox.setChecked(settings.get("hide_commands", False))
                self.hide_queue_checkbox.setChecked(settings.get("hide_queue", False))
                self.width_input.setText(str(settings.get("window_width", 1100)))
                self.height_input.setText(str(settings.get("window_height", 800)))
                encrypted_token = settings.get("auth_token", "")
                if encrypted_token:
                    self.token_input.setText(self.decrypt(encrypted_token))

    # Сохранение настроек в файл
    def save_settings(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
        else:
            settings = {}
        settings.update({
            "startup_tab": self.startup_tab_select.currentText(),
            "hide_main": self.hide_main_checkbox.isChecked(),
            "hide_commands": self.hide_commands_checkbox.isChecked(),
            "hide_queue": self.hide_queue_checkbox.isChecked(),
            "window_width": int(self.width_input.text()) if self.width_input.text().isdigit() else 1100,
            "window_height": int(self.height_input.text()) if self.height_input.text().isdigit() else 800,
            "auth_token": self.encrypt(self.token_input.text()) if self.token_input.text() else ""
        })
        with open(SETTINGS_PATH, "w") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)
        self.restart_app()

    # Перезапуск приложения для применения настроек
    def restart_app(self):
        self.parent().close()  # Закрываем текущее приложение
        os.execl(sys.executable, sys.executable, *sys.argv)  # Запускаем новое приложение с сохраненными настройками
