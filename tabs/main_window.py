import asyncio
import os
import threading
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QPushButton, QFrame, QLabel, QMessageBox
from twitch_bot_functions import load_config
from bot import Bot, run_bot

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
    self.bot = Bot(config['TWITCH_OAUTH_TOKEN'], config['TWITCH_CLIENT_ID'], config['TWITCH_CLIENT_SECRET'],
                   config['TWITCH_CHANNEL'])
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