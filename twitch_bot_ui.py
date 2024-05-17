import webbrowser
import os
import threading
import asyncio

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QTabWidget, QLineEdit,
                             QPushButton, QFormLayout, QMessageBox, QScrollArea, QHBoxLayout, QFrame, QListWidget,
                             QApplication, QCheckBox, QComboBox, QProgressDialog)
from PyQt5.QtGui import QPixmap, QPalette, QBrush

from twitch_bot_functions import save_config, load_config, load_commands, save_command, delete_command
from bot import Bot
from connect_to_sheets import connect_to_google_sheets, add_to_queue, mark_as_completed, get_queues, get_first_waiting_user


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

        self.init_main_tab()
        self.init_connect_tab()
        self.init_commands_tab()
        self.init_queue_tab()
        self.init_additional_tab()


        # self.queue_update_timer = QTimer(self)
        # self.queue_update_timer.timeout.connect(self.update_queues)
        # self.queue_update_timer.start(60000)

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

    def init_main_tab(self):
        layout = QVBoxLayout()
        self.main_tab.setLayout(layout)

        # Кнопка запуска/остановки бота
        self.start_button = QPushButton("Start Bot")
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: green;
                color: white;
                font-size: 16px;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #005500;
            }
        """)
        self.start_button.clicked.connect(self.toggle_bot)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)

        # Статусы
        status_group_box = QFrame()
        status_group_box.setFrameShape(QFrame.StyledPanel)
        status_group_box.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        status_layout = QVBoxLayout()
        status_group_box.setLayout(status_layout)

        self.chatbot_status_label = QLabel("Chat Bot: OFF", self.main_tab)
        self.chatbot_status_label.setStyleSheet("font-size: 14px; color: red;")
        status_layout.addWidget(self.chatbot_status_label, alignment=Qt.AlignCenter)

        self.login_info_label = QLabel("", self.main_tab)
        self.login_info_label.setStyleSheet("font-size: 14px; color: red;")
        status_layout.addWidget(self.login_info_label, alignment=Qt.AlignCenter)

        self.connection_status_label = QLabel("Connection: OFF", self.main_tab)
        self.connection_status_label.setStyleSheet("font-size: 14px; color: red;")
        status_layout.addWidget(self.connection_status_label, alignment=Qt.AlignCenter)

        self.channel_info_label = QLabel("", self.main_tab)
        self.channel_info_label.setStyleSheet("font-size: 14px; color: red;")
        status_layout.addWidget(self.channel_info_label, alignment=Qt.AlignCenter)

        layout.addWidget(status_group_box)

        # Документ и лист
        document_group_box = QFrame()
        document_group_box.setFrameShape(QFrame.StyledPanel)
        document_group_box.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        document_layout = QVBoxLayout()
        document_group_box.setLayout(document_layout)

        self.document_status_label = QLabel(f"Document: {os.getenv('SPREADSHEET_NAME')}", self.main_tab)
        self.document_status_label.setStyleSheet("font-size: 14px; color: blue;")
        document_layout.addWidget(self.document_status_label, alignment=Qt.AlignCenter)

        self.sheet_status_label = QLabel(f"Sheet: {os.getenv('WORKSHEET_NAME')}", self.main_tab)
        self.sheet_status_label.setStyleSheet("font-size: 14px; color: blue;")
        document_layout.addWidget(self.sheet_status_label, alignment=Qt.AlignCenter)

        layout.addWidget(document_group_box)

        # Дополнительное пространство для эстетики
        layout.addStretch()

    def toggle_bot(self):
        if self.start_button.text() == "Start Bot":
            self.start_bot()
        else:
            self.stop_bot()

    def start_bot(self):
        try:
            self.load_config()
            self.stop_bot()
            self.show_loading("Запуск бота...")
            self.bot_thread = threading.Thread(target=self.run_bot)
            self.bot_thread.start()
            self.update_status("ON", "green")
            self.start_button.setText("Stop Bot")
            self.start_button.setStyleSheet("background-color: red; color: white;")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            self.hide_loading()

    def stop_bot(self):
        self.show_loading("Остановка бота...")
        try:
            if hasattr(self, 'bot'):
                self.bot.loop.call_soon_threadsafe(self.bot.loop.stop)
                self.bot_thread.join()
                del self.bot
            self.update_status("OFF", "red")
            self.start_button.setText("Start Bot")
            self.start_button.setStyleSheet("background-color: green; color: white;")
            self.login_info_label.setText("")
            self.channel_info_label.setText("")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            self.hide_loading()

    def run_bot(self):
        config = load_config()
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        self.bot = Bot(config['TWITCH_OAUTH_TOKEN'], config['TWITCH_CLIENT_ID'], config['TWITCH_CLIENT_SECRET'], config['TWITCH_CHANNEL'])
        self.bot.main_window = self  # Добавим ссылку на главное окно в экземпляр бота
        self.bot.run()

    def update_status(self, status, color):
        self.chatbot_status_label.setText(f"Chat Bot: {status}")
        self.chatbot_status_label.setStyleSheet(f"color: {color}")

        self.connection_status_label.setText(f"Connection: {status}")
        self.connection_status_label.setStyleSheet(f"color: {color}")

        self.document_status_label.setText(f"Document: {os.getenv('SPREADSHEET_NAME')}")
        self.document_status_label.setStyleSheet(f"color: {color}")

        self.sheet_status_label.setText(f"Sheet: {os.getenv('WORKSHEET_NAME')}")
        self.sheet_status_label.setStyleSheet(f"color: {color}")

    def update_login_info(self, login_info, channel_info):
        self.login_info_label.setText(login_info)
        self.channel_info_label.setText(channel_info)

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

    def init_commands_tab(self):
        layout = QVBoxLayout()
        self.commands_tab.setLayout(layout)

        form_layout = QFormLayout()
        self.command_input = QLineEdit()
        self.command_response_input = QLineEdit()

        form_layout.addRow("Команда:", self.command_input)
        form_layout.addRow("Ответ на команду:", self.command_response_input)

        add_button = QPushButton("Добавить команду")
        add_button.clicked.connect(self.add_command)

        form_layout.addWidget(add_button)
        layout.addLayout(form_layout)

        self.commands_list_widget = QWidget()
        self.commands_list_layout = QVBoxLayout()
        self.commands_list_widget.setLayout(self.commands_list_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.commands_list_widget)

        layout.addWidget(scroll_area)

        header_frame = QFrame()
        header_layout = QHBoxLayout()
        header_frame.setLayout(header_layout)

        header_layout.addWidget(QLabel("Команда"))
        header_layout.addWidget(QLabel("Ответ"))
        header_layout.addWidget(QLabel(""))

        self.commands_list_layout.addWidget(header_frame)
        self.load_commands()

    def load_commands(self):
        commands = load_commands()
        for command_dict in commands:
            self.add_command_to_ui(command_dict['command'], command_dict['response'])

    def add_command(self):
        command = self.command_input.text()
        response = self.command_response_input.text()

        if not command or not response:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения")
            return

        success, message = save_command(command, response)
        if not success:
            QMessageBox.warning(self, "Ошибка", message)
            return

        self.add_command_to_ui(command, response)
        self.command_input.clear()
        self.command_response_input.clear()

    def add_command_to_ui(self, command, response):
        command_frame = QFrame()
        command_layout = QHBoxLayout()
        command_frame.setLayout(command_layout)

        command_label = QLabel(command)
        response_label = QLabel(response)
        delete_button = QPushButton("Удалить")
        delete_button.setStyleSheet("""
            background-color: #FF7F7F;
            color: white;
            border-radius: 5px;
        """)
        delete_button.clicked.connect(lambda: self.delete_command(command, command_frame))

        command_layout.addWidget(command_label)
        command_layout.addWidget(response_label)
        command_layout.addWidget(delete_button)

        command_frame.setStyleSheet("""
            background: rgba(255, 255, 255, 150);
            border-radius: 10px;
            margin: 2px;
            padding: 5px;
        """)

        self.commands_list_layout.addWidget(command_frame)

    def delete_command(self, command, command_frame):
        success, message = delete_command(command)
        if success:
            command_frame.deleteLater()
        else:
            QMessageBox.warning(self, "Ошибка", message)

    def init_queue_tab(self):
        layout = QHBoxLayout()
        self.queue_tab.setLayout(layout)

        self.worksheet = connect_to_google_sheets()

        control_layout = QVBoxLayout()
        control_layout.setAlignment(Qt.AlignTop)

        label = QLabel("Очередь", self.queue_tab)
        control_layout.addWidget(label, alignment=Qt.AlignTop)

        auto_process_layout = QHBoxLayout()
        self.first_user_label = QLabel("[Имя первого пользователя] - [Статус]")
        self.mark_button = QPushButton("Отметить")
        self.mark_button.clicked.connect(lambda: self.mark_first_user_as_completed())
        auto_process_layout.addWidget(self.first_user_label)
        auto_process_layout.addWidget(self.mark_button)
        control_layout.addLayout(auto_process_layout)

        add_user_group = QVBoxLayout()
        self.add_user_label = QLabel("Добавить пользователя")
        add_user_form_layout = QHBoxLayout()
        self.add_user_name_input = QLineEdit()
        self.add_user_type_selector = QComboBox()
        self.add_user_type_selector.addItems(["VIP", "Обычная"])
        self.add_user_button = QPushButton("Добавить")
        self.add_user_button.clicked.connect(lambda: self.add_user())
        add_user_form_layout.addWidget(self.add_user_name_input)
        add_user_form_layout.addWidget(self.add_user_type_selector)
        add_user_form_layout.addWidget(self.add_user_button)
        add_user_group.addWidget(self.add_user_label)
        add_user_group.addLayout(add_user_form_layout)
        control_layout.addLayout(add_user_group)

        remove_user_group = QVBoxLayout()
        self.remove_user_label = QLabel("Отметить пользователя")
        remove_user_form_layout = QHBoxLayout()
        self.remove_user_name_input = QLineEdit()
        self.remove_user_type_selector = QComboBox()
        self.remove_user_type_selector.addItems(["VIP", "Обычная"])
        self.remove_user_button = QPushButton("Отметить")
        self.remove_user_button.clicked.connect(lambda: self.remove_user())
        remove_user_form_layout.addWidget(self.remove_user_name_input)
        remove_user_form_layout.addWidget(self.remove_user_type_selector)
        remove_user_form_layout.addWidget(self.remove_user_button)
        remove_user_group.addWidget(self.remove_user_label)
        remove_user_group.addLayout(remove_user_form_layout)
        control_layout.addLayout(remove_user_group)

        self.hide_completed_checkbox = QCheckBox("Скрыть пройденные")
        self.hide_completed_checkbox.stateChanged.connect(lambda: self.update_queues())
        control_layout.addWidget(self.hide_completed_checkbox)

        # Автоматическое добавление пользователей за баллы
        auto_add_group = QVBoxLayout()
        self.auto_add_label = QLabel("Автоматическое добавление пользователей за баллы")
        auto_add_form_layout = QHBoxLayout()
        self.auto_add_command_input = QLineEdit()
        self.auto_add_save_button = QPushButton("Сохранить")
        self.auto_add_save_button.clicked.connect(lambda: self.save_auto_add_command())
        auto_add_form_layout.addWidget(self.auto_add_command_input)
        auto_add_form_layout.addWidget(self.auto_add_save_button)
        auto_add_group.addWidget(self.auto_add_label)
        auto_add_group.addLayout(auto_add_form_layout)
        control_layout.addLayout(auto_add_group)

        # Дополнительные функции
        additional_functions_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Обновить очередь")
        self.refresh_button.clicked.connect(lambda: self.update_queues())
        self.export_button = QPushButton("Экспортировать в CSV")
        self.export_button.clicked.connect(lambda: self.export_to_csv())
        additional_functions_layout.addWidget(self.refresh_button)
        additional_functions_layout.addWidget(self.export_button)
        control_layout.addLayout(additional_functions_layout)

        self.auto_add_label1 = QLabel("Если нужно именно удалить ячейку, то")
        self.auto_add_label2 = QLabel("сделайте это в онлайн таблице, ")
        self.auto_add_label3 = QLabel("удалив ячейку и её состояние ")
        self.auto_add_label4 = QLabel("со сдвигом вверх")
        auto_add_group.addWidget(self.auto_add_label1)
        auto_add_group.addWidget(self.auto_add_label2)
        auto_add_group.addWidget(self.auto_add_label3)
        auto_add_group.addWidget(self.auto_add_label4)
        control_layout.addLayout(additional_functions_layout)

        # Разместим управление очередью слева
        control_widget = QWidget()
        control_widget.setLayout(control_layout)
        control_widget.setFixedWidth(self.width() // 3)  # Занимает треть экрана
        layout.addWidget(control_widget)

        # Обычная очередь
        normal_queue_layout = QVBoxLayout()
        normal_queue_layout.setAlignment(Qt.AlignTop)
        self.normal_queue_label = QLabel("Обычная очередь")
        self.normal_queue_list = QListWidget()
        self.normal_queue_list.itemClicked.connect(self.copy_item_to_clipboard)
        normal_queue_layout.addWidget(self.normal_queue_label, alignment=Qt.AlignTop)
        normal_queue_layout.addWidget(self.normal_queue_list)

        normal_queue_scroll_area = QScrollArea()
        normal_queue_scroll_area.setWidgetResizable(True)
        normal_queue_scroll_area.setWidget(QWidget())
        normal_queue_scroll_area.widget().setLayout(normal_queue_layout)
        layout.addWidget(normal_queue_scroll_area)

        vip_queue_layout = QVBoxLayout()
        vip_queue_layout.setAlignment(Qt.AlignTop)
        self.vip_queue_label = QLabel("VIP очередь")
        self.vip_queue_list = QListWidget()
        self.vip_queue_list.itemClicked.connect(self.copy_item_to_clipboard)
        vip_queue_layout.addWidget(self.vip_queue_label, alignment=Qt.AlignTop)
        vip_queue_layout.addWidget(self.vip_queue_list)

        vip_queue_scroll_area = QScrollArea()
        vip_queue_scroll_area.setWidgetResizable(True)
        vip_queue_scroll_area.setWidget(QWidget())
        vip_queue_scroll_area.widget().setLayout(vip_queue_layout)
        layout.addWidget(vip_queue_scroll_area)

        self.update_queues()

    def copy_item_to_clipboard(self, item):
        clipboard = QApplication.clipboard()
        text_to_copy = item.text().split(" - ")[0]
        clipboard.setText(text_to_copy)
        self.show_toast(f"Скопировано в буфер: {text_to_copy}")

    def mark_first_user_as_completed(self):
        self.show_loading("Отметка первого пользователя как выполненного...")
        try:
            first_user, queue_type = get_first_waiting_user(self.worksheet)
            if first_user:
                mark_as_completed(self.worksheet, first_user, queue_type)
                self.update_queues()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            self.hide_loading()

    def add_user(self):
        self.show_loading("Добавление пользователя...")
        try:
            username = self.add_user_name_input.text().strip()
            queue_type = self.add_user_type_selector.currentText().lower()
            if username:
                add_to_queue(self.worksheet, username, queue_type)
                self.update_queues()
        finally:
            self.hide_loading()

    def remove_user(self):
        self.show_loading("Отметка пользователя как выполненного...")
        try:
            username = self.remove_user_name_input.text().strip()
            queue_type = self.remove_user_type_selector.currentText().lower()
            if username:
                mark_as_completed(self.worksheet, username, queue_type)
                self.update_queues()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
        finally:
            self.hide_loading()

    def save_auto_add_command(self):
        command = self.auto_add_command_input.text().strip()
        self.show_toast("В разработке")
        # Логика сохранения команды для автоматического добавления пользователей
        print(f"Сохранена команда: {command}")

    def update_queues(self):
        self.show_loading("Обновление очереди...")
        try:
            self.worksheet = connect_to_google_sheets()
            vip_queue, normal_queue = get_queues(self.worksheet)
            self.normal_queue_list.clear()
            self.vip_queue_list.clear()

            hide_completed = self.hide_completed_checkbox.isChecked()

            for user, status in normal_queue:
                if hide_completed and status == "Пройдена":
                    continue
                item = f"{user} - {status}"
                self.normal_queue_list.addItem(item)

            for user, status in vip_queue:
                if hide_completed and status == "Пройдена":
                    continue
                item = f"{user} - {status}"
                self.vip_queue_list.addItem(item)

            first_user = get_first_waiting_user(self.worksheet)
            if first_user:
                self.first_user_label.setText(f"{first_user} - Ожидает")
            else:
                self.first_user_label.setText("[Нет ожидающих пользователей]")
        finally:
            self.hide_loading()

    def export_to_csv(self):
        self.show_toast("В разработке. Ну точнее мне пока лень, но если кому-то понадобится сделаю")
        print("Экспорт в CSV")

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