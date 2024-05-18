from PyQt5.QtWidgets import QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QWidget, QScrollArea, QFrame, QHBoxLayout, QLabel, QMessageBox
from twitch_bot_functions import save_command, delete_command as delete_command_from_file, load_commands as load_commands_from_file


def init_commands_tab(self):
    layout = QVBoxLayout()
    self.commands_tab.setLayout(layout)

    form_layout = QFormLayout()
    self.command_input = QLineEdit()
    self.command_response_input = QLineEdit()

    form_layout.addRow("Команда:", self.command_input)
    form_layout.addRow("Ответ на команду:", self.command_response_input)

    add_button = QPushButton("Добавить команду")
    add_button.clicked.connect(lambda: self.add_command())
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
    commands = load_commands_from_file()
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
    try:
        success, message = delete_command_from_file(command)
        if success:
            print(f"Попытка удалить команду '{command}'...")
            command_frame.deleteLater()
            print(f"Команда '{command}' успешно удалена.")
        else:
            QMessageBox.warning(self, "Ошибка", message)
    except Exception as e:
        print(f"Ошибка при удалении команды: {e}")
        QMessageBox.critical(self, "Ошибка", f"Произошла ошибка при удалении команды: {e}")
