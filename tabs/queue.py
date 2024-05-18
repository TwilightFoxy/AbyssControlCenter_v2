from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QComboBox, QListWidget, \
    QScrollArea, QWidget, QMessageBox, QApplication
from connect_to_sheets import connect_to_google_sheets, add_to_queue, mark_as_completed, get_queues, get_first_waiting_user

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
