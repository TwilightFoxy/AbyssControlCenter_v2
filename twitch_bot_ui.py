import webbrowser
import os
import threading
import asyncio
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QTabWidget, QLineEdit, QPushButton, QFormLayout, QMessageBox, QScrollArea, QHBoxLayout, QFrame, QListWidget, QApplication, QCheckBox, QComboBox, QProgressDialog)
from PyQt5.QtGui import QPixmap, QPalette, QBrush

from twitch_bot_functions import save_config, load_config, load_commands, save_command, delete_command
from bot import Bot
from tabs.commands import init_commands_tab, add_command, delete_command as delete_command_from_ui, \
    load_commands as load_commands_from_ui, add_command_to_ui
from tabs.main_window import init_main_tab, toggle_bot, start_bot, stop_bot, run_bot, update_status, update_login_info
from tabs.queue import init_queue_tab, copy_item_to_clipboard, mark_first_user_as_completed, add_user, remove_user, save_auto_add_command, update_queues, export_to_csv


class TwitchBotApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.progress_dialog = None

        self.setWindowTitle("Twitch Bot Manager")
        self.setGeometry(100, 100, 1024, 768)

        # Установка фонового изображения
        self.setAutoFillBackground(True)
        palette = self.palette()
        background_pixmap = QPixmap("Resources/wallp.png")
        palette.setBrush(QPalette.Window, QBrush(background_pixmap))
        self.setPalette(palette)

        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #C4C4C3;
                background: rgba(255, 255, 255, 127);
            }
            QTabBar::tab {
                background: rgba(200, 200, 200, 180);
                border: 1px solid #C4C4C3;
                padding: 10px;
                border-top-left-radius: 10px;
                border-top-right-radius: 10px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background: rgba(150, 150, 150, 180);
                border: 2px solid #8A2BE2;
            }
            QWidget {
                background: rgba(255, 255, 255, 20);
            }
        """)
        self.setCentralWidget(self.tabs)

        # Создание пустых вкладок
        self.main_tab = QWidget()
        self.connect_tab = QWidget()
        self.commands_tab = QWidget()
        self.queue_tab = QWidget()
        self.additional_tab = QWidget()

        self.tabs.addTab(self.main_tab, "Главная")
        self.tabs.addTab(self.connect_tab, "Подключить аккаунт")
        self.tabs.addTab(self.commands_tab, "Команды")
        self.tabs.addTab(self.queue_tab, "Очередь")
        self.tabs.addTab(self.additional_tab, "Дополнительно")

        # Связываем методы из commands с экземпляром TwitchBotApp
        self.add_command = add_command.__get__(self)
        self.delete_command = delete_command_from_ui.__get__(self)
        self.load_commands = load_commands_from_ui.__get__(self)
        self.add_command_to_ui = add_command_to_ui.__get__(self)

        # Связываем методы из main_window с экземпляром TwitchBotApp
        self.toggle_bot = toggle_bot.__get__(self)
        self.start_bot = start_bot.__get__(self)
        self.stop_bot = stop_bot.__get__(self)
        self.run_bot = run_bot.__get__(self)
        self.update_status = update_status.__get__(self)
        self.update_login_info = update_login_info.__get__(self)

        # Связываем методы из queue с экземпляром TwitchBotApp
        self.copy_item_to_clipboard = copy_item_to_clipboard.__get__(self)
        self.mark_first_user_as_completed = mark_first_user_as_completed.__get__(self)
        self.add_user = add_user.__get__(self)
        self.remove_user = remove_user.__get__(self)
        self.save_auto_add_command = save_auto_add_command.__get__(self)
        self.update_queues = update_queues.__get__(self)
        self.export_to_csv = export_to_csv.__get__(self)

        init_main_tab(self)
        self.init_connect_tab()
        init_commands_tab(self)
        init_queue_tab(self)
        self.init_additional_tab()

    def show_loading(self, message="Загрузка..."):
        if self.progress_dialog is None:
            self.progress_dialog = QProgressDialog(message, "Отмена", 0, 0, self)
            self.progress_dialog.setWindowModality(Qt.WindowModal)
        else:
            self.progress_dialog.setLabelText(message)
        self.progress_dialog.show()

    def hide_loading(self):
        if self.progress_dialog:
            self.progress_dialog.hide()

    def init_connect_tab(self):
        layout = QVBoxLayout()
        self.connect_tab.setLayout(layout)

        form_layout = QFormLayout()
        self.twitch_oauth_token_input = QLineEdit()
        self.twitch_oauth_token_input.setEchoMode(QLineEdit.Password)

        self.twitch_client_id_input = QLineEdit()
        self.twitch_client_id_input.setEchoMode(QLineEdit.Password)

        self.twitch_client_secret_input = QLineEdit()
        self.twitch_client_secret_input.setEchoMode(QLineEdit.Password)

        self.twitch_channel_input = QLineEdit()
        self.spreadsheet_name_input = QLineEdit()
        self.worksheet_name_input = QLineEdit()

        form_layout.addRow("TWITCH_OAUTH_TOKEN:", self.twitch_oauth_token_input)
        form_layout.addRow("TWITCH_CLIENT_ID:", self.twitch_client_id_input)
        form_layout.addRow("TWITCH_CLIENT_SECRET:", self.twitch_client_secret_input)
        form_layout.addRow("TWITCH_CHANNEL:", self.twitch_channel_input)
        form_layout.addRow("Таблица:", self.spreadsheet_name_input)
        form_layout.addRow("Лист:", self.worksheet_name_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_config)

        form_layout.addWidget(save_button)
        layout.addLayout(form_layout)

        self.load_config()

        bottom_layout = QHBoxLayout()

        links_layout = QVBoxLayout()
        oauth_token_label = QLabel("TWITCH_OAUTH_TOKEN:")
        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?client_id={self.twitch_client_id_input.text().strip()}"
            f"&redirect_uri=http://localhost"
            f"&response_type=token"
            f"&scope=chat:read+chat:edit+channel:read:redemptions+channel:manage:redemptions"
        )
        twitchapps_link = QLabel(f'<a href="{auth_url}">Получить ключ авторизации</a>')
        twitchapps_link.setOpenExternalLinks(True)

        client_id_secret_label = QLabel("TWITCH_CLIENT_ID/SECRET:")
        devtwitch_link = QLabel(
            '<a href="https://dev.twitch.tv/console/apps/create">dev.twitch.tv/console/apps/create</a>')
        devtwitch_link.setOpenExternalLinks(True)

        important_label = QLabel(
            '<a href="https://github.com/TwilightFoxy/coffee_bot">(ВАЖНО) Подключение гугл таблицы</a>')
        important_label.setOpenExternalLinks(True)

        activate_sheets_label = QLabel(
            '<a href="https://console.cloud.google.com/apis/library/sheets.googleapis.com">(ВАЖНО) Подключение Google Sheets API</a>')
        activate_sheets_label.setOpenExternalLinks(True)

        activate_drive_label = QLabel(
            '<a href="https://console.cloud.google.com/apis/library/drive.googleapis.com">(ВАЖНО) Подключение Google Drive API</a>')
        activate_drive_label.setOpenExternalLinks(True)

        links_layout.addWidget(oauth_token_label)
        links_layout.addWidget(twitchapps_link)
        links_layout.addWidget(client_id_secret_label)
        links_layout.addWidget(devtwitch_link)
        links_layout.addWidget(important_label)
        links_layout.addWidget(activate_sheets_label)
        links_layout.addWidget(activate_drive_label)
        links_layout.addStretch()

        links_widget = QWidget()
        links_widget.setLayout(links_layout)
        links_widget.setFixedWidth(self.width() // 4)

        image_label = QLabel()
        pixmap = QPixmap("Resources/Phantom.png")
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignTop)

        bottom_layout.addWidget(links_widget)
        bottom_layout.addWidget(image_label)
        bottom_layout.addStretch()

        layout.addLayout(bottom_layout)
        self.connect_tab.setLayout(layout)

    def get_auth_token(self):
        client_id = self.twitch_client_id_input.text().strip()
        client_secret = self.twitch_client_secret_input.text().strip()

        if not client_id or not client_secret:
            QMessageBox.warning(self, "Ошибка", "Заполните поля CLIENT ID и CLIENT SECRET")
            return

        redirect_uri = "http://localhost"
        scope = "chat:read chat:edit channel:read:redemptions channel:manage:redemptions"

        auth_url = (
            f"https://id.twitch.tv/oauth2/authorize"
            f"?client_id={client_id}"
            f"&redirect_uri={redirect_uri}"
            f"&response_type=token"
            f"&scope={scope.replace(' ', '+')}"
        )

        webbrowser.open(auth_url)

    def load_config(self):
        config = load_config()
        if config:
            self.twitch_oauth_token_input.setText(config.get('TWITCH_OAUTH_TOKEN', ''))
            self.twitch_client_id_input.setText(config.get('TWITCH_CLIENT_ID', ''))
            self.twitch_client_secret_input.setText(config.get('TWITCH_CLIENT_SECRET', ''))
            self.twitch_channel_input.setText(config.get('TWITCH_CHANNEL', ''))
            self.spreadsheet_name_input.setText(config.get('SPREADSHEET_NAME', ''))
            self.worksheet_name_input.setText(config.get('WORKSHEET_NAME', ''))

    def save_config(self):
        oauth_token = self.twitch_oauth_token_input.text()
        client_id = self.twitch_client_id_input.text()
        client_secret = self.twitch_client_secret_input.text()
        channel = self.twitch_channel_input.text()
        spreadsheet_name = self.spreadsheet_name_input.text()
        worksheet_name = self.worksheet_name_input.text()

        if not oauth_token or not client_id or not client_secret or not channel or not spreadsheet_name or not worksheet_name:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения")
            return

        save_config(oauth_token, client_id, client_secret, channel, spreadsheet_name, worksheet_name)
        self.show_toast("Данные успешно сохранены")

    def init_additional_tab(self):
        layout = QVBoxLayout()
        self.additional_tab.setLayout(layout)
        label = QLabel("Полезные штуки, которые пока хз куда впихнуть:", self.additional_tab)
        layout.addWidget(label)

        list_widget = QListWidget()
        list_widget.addItem("{ctx.author.name} - Обращение к пользователю по имени в командах")
        list_widget.itemClicked.connect(self.copy_to_clipboard)
        layout.addWidget(list_widget)

    def copy_to_clipboard(self, item):
        clipboard = QApplication.clipboard()
        text_to_copy = "{ctx.author.name}"
        clipboard.setText(text_to_copy)

        self.show_toast("Скопировано в буфер: {ctx.author.name}")

    def show_toast(self, message):
        toast = QLabel(message, self)
        toast.setStyleSheet("background-color: #444444; color: white; padding: 10px; border-radius: 5px;")
        toast.setAlignment(Qt.AlignCenter)
        toast.setWindowFlags(Qt.ToolTip)
        toast.setAttribute(Qt.WA_DeleteOnClose)
        toast.setGeometry(0, 0, 250, 50)
        toast.move(self.width() // 2 - toast.width() // 2, self.height() // 2 - toast.height() // 2)
        toast.show()

        QTimer.singleShot(2000, toast.close)