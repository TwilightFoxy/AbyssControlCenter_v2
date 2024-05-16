import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QTabWidget, QLineEdit, QPushButton, QFormLayout, QMessageBox
from PyQt5.QtGui import QPixmap, QPalette, QBrush
from PyQt5.QtCore import Qt
from twitch_bot_functions import save_config, load_config

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

        links_layout = QVBoxLayout()
        twitchapps_link = QLabel('<a href="https://twitchapps.com">twitchapps.com</a>')
        twitchapps_link.setOpenExternalLinks(True)
        links_layout.addWidget(twitchapps_link)

        devtwitch_link = QLabel('<a href="https://dev.twitch.tv/console/apps/create">dev.twitch.tv/console/apps/create</a>')
        devtwitch_link.setOpenExternalLinks(True)
        links_layout.addWidget(devtwitch_link)

        links_layout.addStretch()  # Добавляем растяжение перед ссылками для размещения их внизу
        layout.addLayout(links_layout)
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
        label = QLabel("Команды", self.commands_tab)
        layout.addWidget(label)

    def init_queue_tab(self):
        layout = QVBoxLayout()
        self.queue_tab.setLayout(layout)
        label = QLabel("Настройки очереди", self.queue_tab)
        layout.addWidget(label)

    def init_additional_tab(self):
        layout = QVBoxLayout()
        self.additional_tab.setLayout(layout)
        label = QLabel("Дополнительно", self.additional_tab)
        layout.addWidget(label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = TwitchBotApp()
    window.show()
    sys.exit(app.exec_())
