from PyQt6.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel, QPushButton, QHBoxLayout, QSpacerItem, QSizePolicy, QCheckBox
import json
import os

class SettingsView(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.startup_tab_label = QLabel("Выберите начальный раздел")
        self.startup_tab_select = QComboBox()
        self.startup_tab_select.addItems(["Главная", "Команды", "Очередь", "Настройки"])

        self.hide_main_checkbox = QCheckBox("Скрыть Главная")
        self.hide_commands_checkbox = QCheckBox("Скрыть Команды")
        self.hide_queue_checkbox = QCheckBox("Скрыть Очередь")

        self.save_button = QPushButton("Сохранить настройки")

        # Layout for startup tab selection
        tab_selection_layout = QHBoxLayout()
        tab_selection_layout.addWidget(self.startup_tab_label)
        tab_selection_layout.addWidget(self.startup_tab_select)
        tab_selection_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.layout.addLayout(tab_selection_layout)
        self.layout.addWidget(self.hide_main_checkbox)
        self.layout.addWidget(self.hide_commands_checkbox)
        self.layout.addWidget(self.hide_queue_checkbox)
        self.layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self.layout.addWidget(self.save_button)

        self.save_button.clicked.connect(self.save_settings)

        self.load_settings()

    def load_settings(self):
        if os.path.exists("settings.json"):
            with open("settings.json", "r") as file:
                settings = json.load(file)
                self.startup_tab_select.setCurrentText(settings.get("startup_tab", "Главная"))
                self.hide_main_checkbox.setChecked(settings.get("hide_main", False))
                self.hide_commands_checkbox.setChecked(settings.get("hide_commands", False))
                self.hide_queue_checkbox.setChecked(settings.get("hide_queue", False))

    def save_settings(self):
        settings = {
            "startup_tab": self.startup_tab_select.currentText(),
            "hide_main": self.hide_main_checkbox.isChecked(),
            "hide_commands": self.hide_commands_checkbox.isChecked(),
            "hide_queue": self.hide_queue_checkbox.isChecked(),
        }
        with open("settings.json", "w") as file:
            json.dump(settings, file)
