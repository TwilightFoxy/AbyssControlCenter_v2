from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton


class CommandsView(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.command_label = QLabel("Команды")
        self.command_text_edit = QTextEdit()
        self.save_button = QPushButton("Сохранить")

        layout.addWidget(self.command_label)
        layout.addWidget(self.command_text_edit)
        layout.addWidget(self.save_button)

        self.setLayout(layout)
