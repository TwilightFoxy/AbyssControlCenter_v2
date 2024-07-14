import webbrowser
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QCheckBox, QMessageBox, QSpacerItem,
                             QSizePolicy, QHBoxLayout, QFrame, QComboBox, QGridLayout)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
import requests
import json
import os

SETTINGS_PATH = "data/settings.json"

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.layout = QHBoxLayout()  # Используем горизонтальный layout для двух колонок
        self.setLayout(self.layout)

        self.left_column = QVBoxLayout()
        self.right_column = QVBoxLayout()

        # Колонка с основными настройками
        self.init_left_column()

        # Колонка с настройками наград за баллы
        self.init_right_column()

        self.layout.addLayout(self.left_column)
        self.layout.addLayout(self.right_column)

    def init_left_column(self):
        # Название канала
        self.channel_label = QLabel("Название канала")
        self.channel_input = QLineEdit()

        # Поля для токенов авторизации
        self.token_label = QLabel("Token")
        self.token_input = QLineEdit()

        # Поля для client_id и refresh_token
        self.client_id_label = QLabel("Client ID")
        self.client_id_input = QLineEdit()

        self.refresh_token_label = QLabel("Refresh Token")
        self.refresh_token_input = QLineEdit()

        # Поля для bot_token, client_id и refresh_token для бота
        self.bot_token_label = QLabel("Bot Token")
        self.bot_token_input = QLineEdit()

        self.bot_client_id_label = QLabel("Bot Client ID")
        self.bot_client_id_input = QLineEdit()

        self.bot_refresh_token_label = QLabel("Bot Refresh Token")
        self.bot_refresh_token_input = QLineEdit()

        # Поля для настроек приложения
        self.startup_tab_label = QLabel("Выберите начальный раздел")
        self.startup_tab_select = QComboBox()
        self.startup_tab_select.addItems(["Главная", "Команды", "Очередь", "Настройки"])
        self.hide_main_checkbox = QCheckBox("Скрыть Главная")
        self.hide_commands_checkbox = QCheckBox("Скрыть Команды")
        self.hide_queue_checkbox = QCheckBox("Скрыть Очередь")
        self.width_input = QLineEdit()
        self.width_input.setPlaceholderText("Ширина окна (например, 1100)")
        self.height_input = QLineEdit()
        self.height_input.setPlaceholderText("Высота окна (например, 800)")

        # Чекбокс для выбора режима работы (от имени канала или от имени бота)
        self.use_bot_checkbox = QCheckBox("Писать от имени канала")
        self.use_bot_checkbox.setChecked(True)

        # Поля для Google Sheets
        self.sheet_id_label = QLabel("Sheet ID")
        self.sheet_id_input = QLineEdit()

        self.sheet_name_label = QLabel("Sheet Name")
        self.sheet_name_input = QLineEdit()

        self.table_link_label = QLabel("Ссылка на таблицу")
        self.table_link_input = QLineEdit()

        # Кнопка для сохранения настроек
        self.save_button = QPushButton("Сохранить настройки")
        self.save_button.clicked.connect(self.save_settings)

        # Кнопка для перехода к инструкции
        self.instruction_button = QPushButton("Инструкция")
        self.instruction_button.clicked.connect(self.open_instruction)

        # Layout для полей ввода и кнопок
        grid_layout = QGridLayout()
        grid_layout.addWidget(self.channel_label, 0, 0)
        grid_layout.addWidget(self.channel_input, 0, 1)
        grid_layout.addWidget(self.token_label, 1, 0)
        grid_layout.addWidget(self.token_input, 1, 1)
        grid_layout.addWidget(self.client_id_label, 2, 0)
        grid_layout.addWidget(self.client_id_input, 2, 1)
        grid_layout.addWidget(self.refresh_token_label, 3, 0)
        grid_layout.addWidget(self.refresh_token_input, 3, 1)
        grid_layout.addWidget(self.bot_token_label, 4, 0)
        grid_layout.addWidget(self.bot_token_input, 4, 1)
        grid_layout.addWidget(self.bot_client_id_label, 5, 0)
        grid_layout.addWidget(self.bot_client_id_input, 5, 1)
        grid_layout.addWidget(self.bot_refresh_token_label, 6, 0)
        grid_layout.addWidget(self.bot_refresh_token_input, 6, 1)
        grid_layout.addWidget(self.sheet_id_label, 7, 0)
        grid_layout.addWidget(self.sheet_id_input, 7, 1)
        grid_layout.addWidget(self.sheet_name_label, 8, 0)
        grid_layout.addWidget(self.sheet_name_input, 8, 1)
        grid_layout.addWidget(self.table_link_label, 9, 0)
        grid_layout.addWidget(self.table_link_input, 9, 1)
        grid_layout.addWidget(self.instruction_button, 10, 1)

        self.left_column.addWidget(self.startup_tab_label)
        self.left_column.addWidget(self.startup_tab_select)
        self.left_column.addWidget(self.hide_main_checkbox)
        self.left_column.addWidget(self.hide_commands_checkbox)
        self.left_column.addWidget(self.hide_queue_checkbox)
        self.left_column.addWidget(QLabel("Настройки размера окна"))
        self.left_column.addWidget(self.width_input)
        self.left_column.addWidget(self.height_input)
        self.left_column.addLayout(grid_layout)
        self.left_column.addWidget(self.use_bot_checkbox)
        self.left_column.addSpacerItem(QSpacerItem(20, 150, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.left_column.addWidget(self.save_button)

    def init_right_column(self):
        # Чекбокс для включения функционала баллов
        self.enable_rewards_checkbox = QCheckBox("Включить функционал баллов")
        self.enable_rewards_checkbox.setChecked(False)
        self.enable_rewards_checkbox.stateChanged.connect(self.toggle_rewards_settings)
        self.right_column.addWidget(self.enable_rewards_checkbox)

        # Скрытая секция для настройки наград за баллы
        self.rewards_section = QVBoxLayout()
        self.check_rewards_button = QPushButton("Проверить доступность баллов")
        self.check_rewards_button.clicked.connect(self.check_rewards_availability)
        self.rewards_status = QLabel()
        self.rewards_status.setStyleSheet("background-color: yellow;")
        self.rewards_status.setFixedSize(20, 20)

        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(112, 112)

        rewards_status_layout = QHBoxLayout()
        rewards_status_layout.addWidget(self.rewards_status)
        rewards_status_layout.addWidget(self.avatar_label)
        self.right_column.addLayout(rewards_status_layout)

        self.rewards_list = QVBoxLayout()
        self.rewards = []

        self.rewards_section.addWidget(self.check_rewards_button)
        self.rewards_section.addLayout(self.rewards_list)

        # Поля для настройки наград
        self.add_reward_settings_fields()

        self.right_column.addLayout(self.rewards_section)

    def add_reward_settings_fields(self):
        reward_types = [
            "Бездна себе –", "Бездна другу –",
            "Обзор себе –", "Обзор другу –",
            "Театр себе –", "Театр другу –"
        ]
        self.reward_selectors = {}
        for reward_type in reward_types:
            label = QLabel(reward_type)
            combo_box = QComboBox()
            self.reward_selectors[reward_type] = combo_box
            self.rewards_section.addWidget(label)
            self.rewards_section.addWidget(combo_box)

    def toggle_rewards_settings(self):
        enable_rewards = self.enable_rewards_checkbox.isChecked()
        self.check_rewards_button.setVisible(enable_rewards)
        self.rewards_status.setVisible(enable_rewards)
        self.avatar_label.setVisible(enable_rewards)
        for i in range(self.rewards_list.count()):
            self.rewards_list.itemAt(i).widget().setVisible(enable_rewards)

    def refresh_access_token(self, client_id, refresh_token):
        try:
            response = requests.post('https://id.twitch.tv/oauth2/token', data={
                'grant_type': 'refresh_token',
                'refresh_token': refresh_token,
                'client_id': client_id
            })
            response.raise_for_status()
            tokens = response.json()
            return tokens['access_token'], tokens['refresh_token']
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при обновлении токена доступа: {e}")
            return None, None

    def check_rewards_availability(self):
        try:
            channel_name = self.channel_input.text()
            auth_token = self.token_input.text()
            client_id = self.client_id_input.text()
            refresh_token = self.refresh_token_input.text()

            if not auth_token or not channel_name:
                QMessageBox.warning(self, "Ошибка", "Введите токен и название канала.")
                return

            user_id = self.get_user_id(channel_name, client_id, auth_token)
            if not user_id:
                raise Exception("Не удалось получить ID пользователя")

            response = requests.get(f'https://api.twitch.tv/helix/channel_points/custom_rewards', headers={
                'Client-ID': client_id,
                'Authorization': f'Bearer {auth_token}'
            }, params={
                'broadcaster_id': user_id
            })
            response.raise_for_status()
            rewards_data = response.json()

            self.rewards_status.setStyleSheet("background-color: green;")
            self.rewards = rewards_data['data']
            self.update_rewards_list()

            avatar_url = self.get_channel_avatar(channel_name, client_id, auth_token)
            if (avatar_url):
                pixmap = QPixmap()
                pixmap.loadFromData(requests.get(avatar_url).content)
                self.avatar_label.setPixmap(pixmap.scaled(112, 112, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                self.avatar_label.clear()

            # Сохраняем user_id в настройки
            self.user_id = user_id
            self.save_settings()

        except requests.exceptions.RequestException as e:
            if e.response.status_code == 401:
                # Попытка обновить токен доступа
                new_access_token, new_refresh_token = self.refresh_access_token(client_id, refresh_token)
                if new_access_token:
                    self.token_input.setText(new_access_token)
                    self.refresh_token_input.setText(new_refresh_token)
                    self.save_settings()
                    self.check_rewards_availability()  # Повторный вызов функции с обновленным токеном
                else:
                    print(f"Ошибка при обновлении токена доступа: {e}")
                    self.rewards_status.setStyleSheet("background-color: red;")
            else:
                print(f"Ошибка при проверке доступности баллов: {e}")
                self.rewards_status.setStyleSheet("background-color: red;")

    def get_user_id(self, username, client_id, access_token):
        try:
            response = requests.get('https://api.twitch.tv/helix/users', headers={
                'Client-ID': client_id,
                'Authorization': f'Bearer {access_token}'
            }, params={
                'login': username
            })
            response.raise_for_status()
            data = response.json()
            print(f"Ответ от API: {data}")
            return data['data'][0]['id']
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении ID пользователя: {e}")
            return None

    def get_channel_avatar(self, username, client_id, access_token):
        try:
            response = requests.get('https://api.twitch.tv/helix/users', headers={
                'Client-ID': client_id,
                'Authorization': f'Bearer {access_token}'
            }, params={
                'login': username
            })
            response.raise_for_status()
            data = response.json()
            if 'data' in data and len(data['data']) > 0:
                return data['data'][0].get('profile_image_url', None)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении аватара канала: {e}")
            return None

    def update_rewards_list(self):
        # Получаем список доступных наград
        reward_titles = ['-'] + [reward['title'] for reward in self.rewards]

        # Обновляем каждый comboBox для выбора наград
        for reward_type, combo_box in self.reward_selectors.items():
            combo_box.clear()
            combo_box.addItems(reward_titles)
            # Восстанавливаем сохраненный выбор
            if reward_type in self.saved_reward_selectors:
                combo_box.setCurrentText(self.saved_reward_selectors[reward_type])

    @staticmethod
    def open_instruction():
        webbrowser.open("https://github.com/TwilightFoxy/AbyssControlCenter_v2")

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
                self.channel_input.setText(settings.get("channel", ""))
                self.token_input.setText(settings.get("auth_token", ""))
                self.client_id_input.setText(settings.get("client_id", ""))
                self.refresh_token_input.setText(settings.get("refresh_token", ""))
                self.bot_token_input.setText(settings.get("bot_auth_token", ""))
                self.bot_client_id_input.setText(settings.get("bot_client_id", ""))
                self.bot_refresh_token_input.setText(settings.get("bot_refresh_token", ""))
                self.use_bot_checkbox.setChecked(settings.get("use_bot", True))
                self.enable_rewards_checkbox.setChecked(settings.get("enable_rewards", False))
                self.rewards_checked = settings.get("rewards_checked", False)
                self.saved_reward_selectors = settings.get("reward_selectors", {})
                self.user_id = settings.get("user_id", "")
                self.sheet_id_input.setText(settings.get("sheet_id", ""))
                self.sheet_name_input.setText(settings.get("sheet_name", ""))
                self.table_link_input.setText(settings.get("table_link", ""))

                if self.rewards_checked:
                    self.rewards_status.setStyleSheet("background-color: green;")
                    self.update_rewards_list()

                if self.user_id:
                    avatar_url = self.get_channel_avatar(self.channel_input.text(), self.client_id_input.text(),
                                                         self.token_input.text())
                    if avatar_url:
                        pixmap = QPixmap()
                        pixmap.loadFromData(requests.get(avatar_url).content)
                        self.avatar_label.setPixmap(pixmap.scaled(112, 112, Qt.AspectRatioMode.KeepAspectRatio))

    def save_settings(self):
        settings = {
            "startup_tab": self.startup_tab_select.currentText(),
            "hide_main": self.hide_main_checkbox.isChecked(),
            "hide_commands": self.hide_commands_checkbox.isChecked(),
            "hide_queue": self.hide_queue_checkbox.isChecked(),
            "window_width": int(self.width_input.text()) if self.width_input.text().isdigit() else 1100,
            "window_height": int(self.height_input.text()) if self.height_input.text().isdigit() else 800,
            "channel": self.channel_input.text(),
            "auth_token": self.token_input.text(),
            "client_id": self.client_id_input.text(),
            "refresh_token": self.refresh_token_input.text(),
            "bot_auth_token": self.bot_token_input.text(),
            "bot_client_id": self.bot_client_id_input.text(),
            "bot_refresh_token": self.bot_refresh_token_input.text(),
            "use_bot": self.use_bot_checkbox.isChecked(),
            "enable_rewards": self.enable_rewards_checkbox.isChecked(),
            "rewards_checked": self.rewards_status.styleSheet() == "background-color: green;",
            "reward_selectors": {key: combo_box.currentText() for key, combo_box in self.reward_selectors.items()},
            "user_id": self.user_id,
            "sheet_id": self.sheet_id_input.text(),
            "sheet_name": self.sheet_name_input.text(),
            "table_link": self.table_link_input.text()
        }
        with open(SETTINGS_PATH, "w") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)

    def restart_app(self):
        self.parent().close()
        os.execl(sys.executable, sys.executable, *sys.argv)
