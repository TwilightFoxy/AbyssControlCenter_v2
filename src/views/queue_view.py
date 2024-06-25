from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, \
    QLineEdit, QComboBox, QAbstractItemView, QGridLayout, QMessageBox, QCheckBox, QTextEdit, QHeaderView, QApplication, \
    QToolTip
from PyQt6.QtGui import QColor, QCursor, QKeySequence, QShortcut
from PyQt6.QtCore import Qt
import json
import os

QUEUE_DATA_PATH = "data/queue_data.json"
SETTINGS_PATH = "data/settings.json"
DATA_DIR = "data"

STATUS_COLOR = {
    "Ожидание": QColor(255, 255, 224),  # светло-желтый
    "Выполнено": QColor(144, 238, 144),  # светло-зеленый
    "Отложено": QColor(255, 182, 193)  # светло-розовый
}

TYPE_COLOR = {
    "Бездна": QColor(238, 130, 238),  # фиолетовый
    "Театр": QColor(135, 206, 250),  # светло-голубой
    "Обзор": QColor(255, 215, 0)  # золотой
}

class QueueView(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
        self.connect_signals()
        self.load_data()

    # Инициализация пользовательского интерфейса
    def init_ui(self):
        main_layout = QHBoxLayout()

        control_widget = self.create_control_widget()
        control_widget.setMinimumWidth(300)
        control_widget.setMaximumWidth(350)

        grid_layout = self.create_grid_layout()

        main_layout.addWidget(control_widget)
        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

    # Создание виджета управления
    def create_control_widget(self):
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя")
        self.column_select = QComboBox()
        self.column_select.addItems(["Текущая Вип", "Текущая Обычная", "Следующая Вип", "Следующая Обычная"])

        self.add_abyss_button = QPushButton("Бездну")
        self.add_theater_button = QPushButton("Театр")
        self.add_overview_button = QPushButton("Обзор")
        self.up_button = QPushButton("Вверх")
        self.down_button = QPushButton("Вниз")
        self.hide_completed_checkbox = QCheckBox("Скрыть выполненные")
        self.delete_button = QPushButton("Удалить выбранную строку")
        self.transfer_button = QPushButton("Перенести следующую в текущую")
        self.delete_completed_button = QPushButton("Удалить выполненные")

        delete_button_style = """
            QPushButton {
                background-color: #d9534f;
                color: white;
                border: 1px solid #d43f3a;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c9302c;
                border-color: #ac2925;
            }
            QPushButton:pressed {
                background-color: #ac2925;
                border-color: #761c19;
            }
        """
        self.delete_button.setStyleSheet(delete_button_style)
        self.delete_completed_button.setStyleSheet(delete_button_style)

        control_layout.addWidget(QLabel("Управление"))
        control_layout.addWidget(self.name_input)
        control_layout.addWidget(self.column_select)

        add_buttons_layout = QHBoxLayout()
        add_buttons_layout.addWidget(self.add_abyss_button)
        add_buttons_layout.addWidget(self.add_theater_button)
        add_buttons_layout.addWidget(self.add_overview_button)
        control_layout.addLayout(add_buttons_layout)

        move_buttons_layout = QHBoxLayout()
        move_buttons_layout.addWidget(self.up_button)
        move_buttons_layout.addWidget(self.down_button)
        control_layout.addLayout(move_buttons_layout)

        control_layout.addWidget(self.hide_completed_checkbox)
        control_layout.addWidget(self.delete_button)
        control_layout.addWidget(self.delete_completed_button)
        control_layout.addWidget(self.transfer_button)

        template_label_layout = QHBoxLayout()
        template_label = QLabel("Шаблон")
        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(30, 30)
        self.help_button.clicked.connect(self.show_help_template)
        template_label_layout.addWidget(template_label)
        template_label_layout.addWidget(self.help_button)
        template_label_layout.addStretch()

        control_layout.addLayout(template_label_layout)

        self.template_input = QTextEdit()
        self.template_input.setPlaceholderText("например: {vip}")
        control_layout.addWidget(self.template_input)

        self.save_template_button = QPushButton("Сохранить шаблон")
        self.save_data_button = QPushButton("Сохранить таблицы")
        self.load_data_button = QPushButton("Загрузить таблицы")

        save_load_buttons_layout = QHBoxLayout()
        save_load_buttons_layout.addWidget(self.save_data_button)
        save_load_buttons_layout.addWidget(self.load_data_button)

        control_layout.addWidget(self.save_template_button)
        control_layout.addLayout(save_load_buttons_layout)
        control_layout.addStretch()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        return control_widget

    # Создание сетки таблиц
    def create_grid_layout(self):
        grid_layout = QGridLayout()

        self.current_vip_label = QLabel("Текущая Вип: 0")
        self.current_regular_label = QLabel("Текущая Обычная: 0")
        self.next_vip_label = QLabel("Следующая Вип: 0")
        self.next_regular_label = QLabel("Следующая Обычная: 0")

        self.current_vip_table = self.create_table(["Вип", "Статус", "Тип"])
        self.current_regular_table = self.create_table(["Обычная", "Статус", "Тип"])

        grid_layout.addWidget(self.current_vip_label, 0, 0)
        grid_layout.addWidget(self.current_vip_table, 1, 0)
        grid_layout.addWidget(self.current_regular_label, 0, 1)
        grid_layout.addWidget(self.current_regular_table, 1, 1)

        self.next_vip_table = self.create_table(["Вип", "Статус", "Тип"])
        self.next_regular_table = self.create_table(["Обычная", "Статус", "Тип"])

        grid_layout.addWidget(self.next_vip_label, 2, 0)
        grid_layout.addWidget(self.next_vip_table, 3, 0)
        grid_layout.addWidget(self.next_regular_label, 2, 1)
        grid_layout.addWidget(self.next_regular_table, 3, 1)

        grid_layout.setRowStretch(1, 2)
        grid_layout.setRowStretch(3, 1)

        return grid_layout

    # Подключение сигналов к соответствующим слотам
    def connect_signals(self):
        self.add_abyss_button.clicked.connect(lambda: self.add_to_queue("Бездна"))
        self.add_theater_button.clicked.connect(lambda: self.add_to_queue("Театр"))
        self.add_overview_button.clicked.connect(lambda: self.add_to_queue("Обзор"))
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        self.delete_button.clicked.connect(lambda: self.delete_selected_row())
        self.hide_completed_checkbox.stateChanged.connect(self.hide_completed)
        self.transfer_button.clicked.connect(self.transfer_to_current)
        self.delete_completed_button.clicked.connect(self.delete_completed)
        self.save_template_button.clicked.connect(self.save_template)
        self.save_data_button.clicked.connect(self.save_data)
        self.load_data_button.clicked.connect(self.load_data)

        self.current_vip_table.cellClicked.connect(self.change_status)
        self.current_regular_table.cellClicked.connect(self.change_status)
        self.next_vip_table.cellClicked.connect(self.change_status)
        self.next_regular_table.cellClicked.connect(self.change_status)

        # Горячие клавиши
        self.delete_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Return), self)
        self.delete_shortcut.activated.connect(self.delete_selected_row)

        self.toggle_hide_completed_shortcut_equal = QShortcut(QKeySequence(Qt.Key.Key_Equal), self)
        self.toggle_hide_completed_shortcut_equal.activated.connect(self.toggle_hide_completed)

        self.toggle_hide_completed_shortcut_plus = QShortcut(QKeySequence(Qt.Key.Key_Plus), self)
        self.toggle_hide_completed_shortcut_plus.activated.connect(self.toggle_hide_completed)

    # Копирование текста в буфер обмена
    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        QToolTip.showText(QCursor.pos(), f'"{text}" скопировано в буфер обмена')

    # Обработка одиночного клика
    def cell_clicked(self, row, column):
        table = self.sender()
        if column == 0:  # Если кликнули на первую ячейку (ник)
            name_item = table.item(row, column)
            if name_item:
                self.copy_to_clipboard(name_item.text())

    # Обработка двойного клика
    def cell_double_clicked(self, row, column):
        table = self.sender()
        if column == 0 or column == 3:  # Разрешаем редактирование только первой и четвертой ячейки (ник и комментарий)
            table.setEditTriggers(QAbstractItemView.EditTrigger.AllEditTriggers)
            table.editItem(table.item(row, column))  # Начинаем редактирование выбранной ячейки
        else:
            table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

    # Переключение состояния чекбокса "Скрыть выполненные"
    def toggle_hide_completed(self):
        self.hide_completed_checkbox.setChecked(not self.hide_completed_checkbox.isChecked())

    # Создание таблицы
    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers) + 1)
        table.setHorizontalHeaderLabels(headers + ["Комментарий"])
        table.setRowCount(0)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)  # Отключаем редактирование для всех столбцов по умолчанию
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setDragEnabled(True)
        table.setAcceptDrops(True)
        table.setDropIndicatorShown(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        table.verticalHeader().setDefaultSectionSize(20)
        table.cellClicked.connect(self.cell_clicked)
        table.cellDoubleClicked.connect(self.cell_double_clicked)
        return table

    # Добавление элемента в очередь
    def add_to_queue(self, type_):
        name = self.name_input.text()
        column = self.column_select.currentIndex()

        if not name:
            return

        if column == 0:
            self.add_to_table(self.current_vip_table, 0, name, type_)
        elif column == 1:
            self.add_to_table(self.current_regular_table, 0, name, type_)
        elif column == 2:
            self.add_to_table(self.next_vip_table, 0, name, type_)
        elif column == 3:
            self.add_to_table(self.next_regular_table, 0, name, type_)
        self.update_counts()
        self.save_data()

    # Добавление элемента в таблицу
    def add_to_table(self, table, column, name, type_):
        row_count = table.rowCount()
        table.insertRow(row_count)
        table.setItem(row_count, column, QTableWidgetItem(name))
        table.setItem(row_count, column + 1, QTableWidgetItem("Ожидание"))
        table.setItem(row_count, column + 2, QTableWidgetItem(type_))
        table.setItem(row_count, column + 3, QTableWidgetItem(""))
        self.set_row_color(table, row_count)

    # Изменение статуса элемента в таблице
    def change_status(self, row, column):
        table = self.sender()
        if column == 1:
            current_status = table.item(row, column).text()
            new_status = self.get_next_status(current_status)
            table.setItem(row, column, QTableWidgetItem(new_status))
        elif column == 2:
            current_type = table.item(row, column).text()
            new_type = self.get_next_type(current_type)
            table.setItem(row, column, QTableWidgetItem(new_type))
        self.set_row_color(table, row)
        self.update_counts()
        self.save_data()

    # Получение следующего статуса
    def get_next_status(self, current_status):
        if current_status == "Ожидание":
            return "Выполнено"
        elif current_status == "Выполнено":
            return "Отложено"
        elif current_status == "Отложено":
            return "Ожидание"
        return current_status

    # Получение следующего типа
    def get_next_type(self, current_type):
        if current_type == "Бездна":
            return "Театр"
        elif current_type == "Театр":
            return "Обзор"
        elif current_type == "Обзор":
            return "Бездна"
        return current_type

    # Удаление выбранных строк с подтверждением
    def delete_selected_row(self):
        current_table = self.get_focused_table()
        selected_rows = current_table.selectionModel().selectedRows()
        if selected_rows:
            confirmation_box = QMessageBox(self)
            confirmation_box.setWindowTitle("Подтверждение удаления")
            confirmation_box.setText("Нажмите Enter для подтверждения удаления выбранной строки.")
            confirmation_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            confirmation_box.button(QMessageBox.StandardButton.Yes).setShortcut(Qt.Key.Key_Return)
            confirmation_box.button(QMessageBox.StandardButton.No).setShortcut(Qt.Key.Key_Escape)
            confirmation_box.button(QMessageBox.StandardButton.Yes).clicked.connect(lambda: self.remove_selected_rows(current_table, selected_rows))
            confirmation_box.show()

    # Удаление выбранных строк
    def remove_selected_rows(self, current_table, selected_rows):
        for index in sorted(selected_rows, reverse=True):
            current_table.removeRow(index.row())
        self.update_counts()
        self.save_data()

    # Скрытие выполненных элементов
    def hide_completed(self):
        hide = self.hide_completed_checkbox.isChecked()
        for table in [self.current_vip_table, self.current_regular_table, self.next_vip_table, self.next_regular_table]:
            for row in range(table.rowCount()):
                if table.item(row, 1).text() == "Выполнено":
                    table.setRowHidden(row, hide)

    # Перенос следующей очереди в текущую
    def transfer_to_current(self):
        for next_table, current_table in [(self.next_vip_table, self.current_vip_table), (self.next_regular_table, self.current_regular_table)]:
            for row in range(next_table.rowCount()):
                name_item = next_table.item(row, 0)
                status_item = next_table.item(row, 1)
                type_item = next_table.item(row, 2)
                comment_item = next_table.item(row, 3)
                if name_item and status_item and type_item:
                    name = name_item.text()
                    status = status_item.text()
                    type_ = type_item.text()
                    comment = comment_item.text() if comment_item else ""
                    current_table.insertRow(current_table.rowCount())
                    current_table.setItem(current_table.rowCount() - 1, 0, QTableWidgetItem(name))
                    current_table.setItem(current_table.rowCount() - 1, 1, QTableWidgetItem(status))
                    current_table.setItem(current_table.rowCount() - 1, 2, QTableWidgetItem(type_))
                    current_table.setItem(current_table.rowCount() - 1, 3, QTableWidgetItem(comment))
                    self.set_row_color(current_table, current_table.rowCount() - 1)
            next_table.setRowCount(0)
        self.update_counts()
        self.save_data()

    # Удаление выполненных элементов
    def delete_completed(self):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить все выполненные строки?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for table in [self.current_vip_table, self.current_regular_table, self.next_vip_table, self.next_regular_table]:
                for row in reversed(range(table.rowCount())):
                    if table.item(row, 1).text() == "Выполнено":
                        table.removeRow(row)
            self.update_counts()
            self.save_data()

    # Обновление счетчиков
    def update_counts(self):
        self.current_vip_label.setText(f"Текущая Вип: {self.count_non_completed(self.current_vip_table)}")
        self.current_regular_label.setText(f"Текущая Обычная: {self.count_non_completed(self.current_regular_table)}")
        self.next_vip_label.setText(f"Следующая Вип: {self.count_non_completed(self.next_vip_table)}")
        self.next_regular_label.setText(f"Следующая Обычная: {self.count_non_completed(self.next_regular_table)}")

    # Подсчет невыполненных элементов в таблице
    def count_non_completed(self, table):
        count = 0
        for row in range(table.rowCount()):
            if table.item(row, 1).text() != "Выполнено":
                count += 1
        return count

    # Перемещение элемента вверх по очереди
    def move_up(self):
        current_table = self.get_focused_table()
        selected_rows = current_table.selectionModel().selectedRows()
        if selected_rows:
            for index in sorted(selected_rows):
                row = index.row()
                if row > 0:
                    current_table.insertRow(row - 1)
                    for column in range(current_table.columnCount()):
                        current_table.setItem(row - 1, column, current_table.takeItem(row + 1, column))
                    current_table.removeRow(row + 1)
                    current_table.selectRow(row - 1)
        self.save_data()

    # Перемещение элемента вниз по очереди
    def move_down(self):
        current_table = self.get_focused_table()
        selected_rows = current_table.selectionModel().selectedRows()
        if selected_rows:
            for index in sorted(selected_rows, reverse=True):
                row = index.row()
                if row < current_table.rowCount() - 1:
                    current_table.insertRow(row + 2)
                    for column in range(current_table.columnCount()):
                        current_table.setItem(row + 2, column, current_table.takeItem(row, column))
                    current_table.removeRow(row)
                    current_table.selectRow(row + 1)
        self.save_data()

    # Сохранение шаблона в файл
    def save_template(self):
        template_text = self.template_input.toPlainText()
        with open(SETTINGS_PATH, "r") as file:
            settings = json.load(file)
        settings["template"] = template_text
        with open(SETTINGS_PATH, "w") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)

    # Загрузка шаблона из файла
    def load_template(self):
        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
                template_text = settings.get("template", "например: {vip}")
                self.template_input.setPlainText(template_text)

    # Показ помощи по шаблону
    def show_help_template(self):
        help_text = ("Здесь вы выводите текст и используете переменные:\n"
                     "{vip}, {norm}, {vip_next}, {norm_next}, {all_next} \n"
                     "Для чего? Весь этот текст переводится в файл output.txt, и его можно подключить к obs для вывода количества на экран в прямом эфире!")
        self.template_input.setPlainText(help_text)
        with open(SETTINGS_PATH, "r") as file:
            settings = json.load(file)
        settings["template"] = help_text
        with open(SETTINGS_PATH, "w") as file:
            json.dump(settings, file, ensure_ascii=False, indent=4)

    # Обновление выходного файла
    def update_output_file(self):
        vip_count = self.count_non_completed(self.current_vip_table)
        norm_count = self.count_non_completed(self.current_regular_table)
        vip_next_count = self.count_non_completed(self.next_vip_table)
        norm_next_count = self.count_non_completed(self.next_regular_table)
        all_next_count = vip_next_count + norm_next_count

        if os.path.exists(SETTINGS_PATH):
            with open(SETTINGS_PATH, "r") as file:
                settings = json.load(file)
                template_text = settings.get("template", "")
        else:
            template_text = ""

        output_text = template_text.format(vip=vip_count, norm=norm_count, vip_next=vip_next_count, norm_next=norm_next_count, all_next=all_next_count)

        lines = output_text.split('\n')
        filtered_lines = [line for line in lines if '{all_next}' not in line or all_next_count != 0]

        with open(os.path.join(DATA_DIR, "output.txt"), "w", encoding="utf-8") as file:
            file.write('\n'.join(filtered_lines))

    # Сохранение данных в файл
    def save_data(self):
        data = {
            "current_vip": self.get_table_data(self.current_vip_table),
            "current_regular": self.get_table_data(self.current_regular_table),
            "next_vip": self.get_table_data(self.next_vip_table),
            "next_regular": self.get_table_data(self.next_regular_table)
        }
        with open(QUEUE_DATA_PATH, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.update_output_file()

    def load_data(self):
        if os.path.exists(QUEUE_DATA_PATH):
            with open(QUEUE_DATA_PATH, "r", encoding="utf-8") as file:
                data = json.load(file)
                if data:
                    self.set_table_data(self.current_vip_table, self.ensure_four_columns(data.get("current_vip", [])))
                    self.set_table_data(self.current_regular_table,
                                        self.ensure_four_columns(data.get("current_regular", [])))
                    self.set_table_data(self.next_vip_table, self.ensure_four_columns(data.get("next_vip", [])))
                    self.set_table_data(self.next_regular_table, self.ensure_four_columns(data.get("next_regular", [])))
                self.update_counts()
    def ensure_four_columns(self, data):
        for row in data:
            while len(row) < 4:
                row.append("")
        return data

    # Получение данных из таблицы
    def get_table_data(self, table):
        data = []
        for row in range(table.rowCount()):
            row_data = []
            for column in range(table.columnCount()):
                item = table.item(row, column)
                if item:
                    row_data.append(item.text())
                else:
                    row_data.append("")
            data.append(row_data)
        return data

    # Установка данных в таблицу
    def set_table_data(self, table, data):
        table.setRowCount(0)
        for row_data in data:
            row = table.rowCount()
            table.insertRow(row)
            for column, text in enumerate(row_data):
                table.setItem(row, column, QTableWidgetItem(text))
            self.set_row_color(table, row)

    # Установка цвета строки в таблице
    def set_row_color(self, table, row):
        status_item = table.item(row, 1)
        type_item = table.item(row, 2)

        if status_item and status_item.text() in STATUS_COLOR:
            color = STATUS_COLOR[status_item.text()]
            for column in range(table.columnCount()):
                item = table.item(row, column)
                item.setBackground(color)
                item.setForeground(QColor(0, 0, 0))

        if type_item and type_item.text() in TYPE_COLOR:
            color = TYPE_COLOR[type_item.text()]
            type_item.setBackground(color)
            type_item.setForeground(QColor(0, 0, 0))

    # Получение текущей фокусной таблицы
    def get_focused_table(self):
        if self.current_regular_table.hasFocus():
            return self.current_regular_table
        elif self.next_vip_table.hasFocus():
            return self.next_vip_table
        elif self.next_regular_table.hasFocus():
            return self.next_regular_table
        else:
            return self.current_vip_table
