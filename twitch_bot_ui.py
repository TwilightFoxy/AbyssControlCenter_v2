from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QLabel, QTabWidget, QLineEdit,
                             QPushButton, QFormLayout, QMessageBox, QScrollArea, QHBoxLayout, QFrame, QListWidget,
                             QApplication)
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from twitch_bot_functions import save_config, load_config, load_commands, save_command, delete_command

class TwitchBotApp(QMainWindow):
    def __init__(self):
        super().__init__()

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
                background: rgba(255, 255, 255, 150);
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
                background: rgba(255, 255, 255, 25);
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
        self.tabs.addTab(self.queue_tab, "Настройки очереди")
        self.tabs.addTab(self.additional_tab, "Дополнительно")

        self.init_main_tab()
        self.init_connect_tab()
        self.init_commands_tab()
        self.init_queue_tab()
        self.init_additional_tab()

    def init_main_tab(self):
        layout = QVBoxLayout()
        self.main_tab.setLayout(layout)
        label = QLabel("Главная", self.main_tab)
        layout.addWidget(label)

    def init_connect_tab(self):
        layout = QVBoxLayout()
        self.connect_tab.setLayout(layout)

        form_layout = QFormLayout()
        self.twitch_oauth_token_input = QLineEdit()
        self.twitch_client_id_input = QLineEdit()
        self.twitch_client_secret_input = QLineEdit()
        self.twitch_channel_input = QLineEdit()

        form_layout.addRow("TWITCH_OAUTH_TOKEN:", self.twitch_oauth_token_input)
        form_layout.addRow("TWITCH_CLIENT_ID:", self.twitch_client_id_input)
        form_layout.addRow("TWITCH_CLIENT_SECRET:", self.twitch_client_secret_input)
        form_layout.addRow("TWITCH_CHANNEL:", self.twitch_channel_input)

        save_button = QPushButton("Сохранить")
        save_button.clicked.connect(self.save_config)

        form_layout.addWidget(save_button)
        layout.addLayout(form_layout)

        # Загрузка данных из config.env
        self.load_config()

        # Создаем горизонтальный макет для размещения изображения и ссылок в одной строке
        bottom_layout = QHBoxLayout()

        # Макет для ссылок
        links_layout = QVBoxLayout()
        oauth_token_label = QLabel("TWITCH_OAUTH_TOKEN:")
        twitchapps_link = QLabel('<a href="https://twitchapps.com">twitchapps.com</a>')
        twitchapps_link.setOpenExternalLinks(True)

        client_id_secret_label = QLabel("TWITCH_CLIENT_ID/SECRET:")
        devtwitch_link = QLabel(
            '<a href="https://dev.twitch.tv/console/apps/create">dev.twitch.tv/console/apps/create</a>')
        devtwitch_link.setOpenExternalLinks(True)

        links_layout.addWidget(oauth_token_label)
        links_layout.addWidget(twitchapps_link)
        links_layout.addWidget(client_id_secret_label)
        links_layout.addWidget(devtwitch_link)
        links_layout.addStretch()  # Добавляем растяжение после ссылок для правильного позиционирования

        # Настройка ширины макета с ссылками
        links_widget = QWidget()
        links_widget.setLayout(links_layout)
        links_widget.setFixedWidth(self.width() // 3)  # Устанавливаем ширину треть ширины окна

        # Макет для изображения
        image_label = QLabel()
        pixmap = QPixmap("Resources/Phantom.png")
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignTop)  # Выравниваем по верхнему краю

        # Добавляем макеты в горизонтальный макет
        bottom_layout.addWidget(links_widget)
        bottom_layout.addWidget(image_label)
        bottom_layout.addStretch()  # Добавляем растяжение после изображения для правильного позиционирования

        layout.addLayout(bottom_layout)
        self.connect_tab.setLayout(layout)

    def load_config(self):
        config = load_config()
        if config:
            self.twitch_oauth_token_input.setText(config.get('TWITCH_OAUTH_TOKEN', ''))
            self.twitch_client_id_input.setText(config.get('TWITCH_CLIENT_ID', ''))
            self.twitch_client_secret_input.setText(config.get('TWITCH_CLIENT_SECRET', ''))
            self.twitch_channel_input.setText(config.get('TWITCH_CHANNEL', ''))

    def save_config(self):
        oauth_token = self.twitch_oauth_token_input.text()
        client_id = self.twitch_client_id_input.text()
        client_secret = self.twitch_client_secret_input.text()
        channel = self.twitch_channel_input.text()

        if not oauth_token or not client_id or not client_secret or not channel:
            QMessageBox.warning(self, "Ошибка", "Все поля обязательны для заполнения")
            return

        save_config(oauth_token, client_id, client_secret, channel)
        QMessageBox.information(self, "Успех", "Данные успешно сохранены")

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

        # Прокручиваемая область для команд
        self.commands_list_widget = QWidget()
        self.commands_list_layout = QVBoxLayout()
        self.commands_list_widget.setLayout(self.commands_list_layout)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.commands_list_widget)

        layout.addWidget(scroll_area)

        # Добавление заголовков столбцов
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
        layout = QVBoxLayout()
        self.queue_tab.setLayout(layout)
        label = QLabel("Настройки очереди", self.queue_tab)
        layout.addWidget(label)

    from PyQt5.QtCore import QTimer, Qt
    from PyQt5.QtWidgets import QLabel

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
        toast.setAttribute(Qt.WA_DeleteOnClose)  # Удаляем виджет после закрытия
        toast.setGeometry(0, 0, 250, 50)
        toast.move(self.width() // 2 - toast.width() // 2, self.height() // 2 - toast.height() // 2)
        toast.show()

        QTimer.singleShot(2000, toast.close)  # Скрываем сообщение через 2 секунды
