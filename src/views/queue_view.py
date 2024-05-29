from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QPushButton, \
    QLineEdit, QComboBox, QAbstractItemView, QGridLayout, QMessageBox, QCheckBox, QPlainTextEdit, QTextEdit
from PyQt6.QtCore import Qt
import json
import os

class QueueView(QWidget):
    def __init__(self):
        super().__init__()

        main_layout = QHBoxLayout()

        # Создаем контейнер для управления
        control_widget = QWidget()
        control_layout = QVBoxLayout(control_widget)
        control_widget.setMinimumWidth(300)  # Устанавливаем минимальную ширину
        control_widget.setMaximumWidth(350)  # Устанавливаем максимальную ширину

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введите имя")
        self.column_select = QComboBox()
        self.column_select.addItems(["Текущая Вип", "Текущая Обычная", "Следующая Вип", "Следующая Обычная"])
        self.add_button = QPushButton("Добавить")
        self.up_button = QPushButton("Вверх")
        self.down_button = QPushButton("Вниз")
        self.hide_completed_checkbox = QCheckBox("Скрыть выполненные")
        self.delete_button = QPushButton("Удалить выбранную строку")
        self.transfer_button = QPushButton("Перенести следующую в текущую")
        self.delete_completed_button = QPushButton("Удалить выполненные")

        # Изменение цвета кнопок удаления
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
        control_layout.addWidget(self.add_button)

        # Добавление кнопок Вверх и Вниз в одну строку
        move_buttons_layout = QHBoxLayout()
        move_buttons_layout.addWidget(self.up_button)
        move_buttons_layout.addWidget(self.down_button)
        control_layout.addLayout(move_buttons_layout)

        control_layout.addWidget(self.hide_completed_checkbox)
        control_layout.addWidget(self.delete_button)
        control_layout.addWidget(self.delete_completed_button)
        control_layout.addWidget(self.transfer_button)

        # Создание горизонтального макета для надписи и кнопки помощи
        template_label_layout = QHBoxLayout()
        template_label = QLabel("Шаблон")
        self.help_button = QPushButton("?")
        self.help_button.setFixedSize(30, 30)  # Устанавливаем фиксированный размер для кнопки
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
        control_layout.addStretch()  # Добавляем растягивающий элемент для выравнивания
        control_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Метки для подсчета
        self.current_vip_label = QLabel("Текущая Вип: 0")
        self.current_regular_label = QLabel("Текущая Обычная: 0")
        self.next_vip_label = QLabel("Следующая Вип: 0")
        self.next_regular_label = QLabel("Следующая Обычная: 0")

        # Сетка для таблиц
        grid_layout = QGridLayout()

        # Таблицы текущей ротации
        self.current_vip_table = self.create_table(["Вип", "Статус"])
        self.current_regular_table = self.create_table(["Обычная", "Статус"])

        grid_layout.addWidget(self.current_vip_label, 0, 0)
        grid_layout.addWidget(self.current_vip_table, 1, 0)
        grid_layout.addWidget(self.current_regular_label, 0, 1)
        grid_layout.addWidget(self.current_regular_table, 1, 1)

        # Таблицы следующей ротации
        self.next_vip_table = self.create_table(["Вип", "Статус"])
        self.next_regular_table = self.create_table(["Обычная", "Статус"])

        grid_layout.addWidget(self.next_vip_label, 2, 0)
        grid_layout.addWidget(self.next_vip_table, 3, 0)
        grid_layout.addWidget(self.next_regular_label, 2, 1)
        grid_layout.addWidget(self.next_regular_table, 3, 1)

        grid_layout.setRowStretch(1, 2)  # Увеличиваем высоту первой строки таблиц в два раза
        grid_layout.setRowStretch(3, 1)  # Оставляем высоту второй строки такой же

        main_layout.addWidget(control_widget)  # Добавляем контейнер управления в основной layout
        main_layout.addLayout(grid_layout)

        self.setLayout(main_layout)

        # Подключаем кнопки к функциям
        self.add_button.clicked.connect(self.add_to_queue)
        self.up_button.clicked.connect(self.move_up)
        self.down_button.clicked.connect(self.move_down)
        self.delete_button.clicked.connect(self.delete_selected_row)
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

        # Загрузка данных и шаблона при инициализации
        self.load_data()
        self.load_template()

    def create_table(self, headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.setRowCount(0)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        table.setDragEnabled(True)
        table.setAcceptDrops(True)
        table.setDropIndicatorShown(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setDefaultSectionSize(150)  # Устанавливаем стандартный размер заголовков столбцов
        table.verticalHeader().setDefaultSectionSize(20)  # Устанавливаем стандартный размер заголовков строк
        return table

    def add_to_queue(self):
        name = self.name_input.text()
        column = self.column_select.currentIndex()

        if not name:
            return

        if column == 0:
            self.add_to_table(self.current_vip_table, 0, name)
        elif column == 1:
            self.add_to_table(self.current_regular_table, 0, name)
        elif column == 2:
            self.add_to_table(self.next_vip_table, 0, name)
        elif column == 3:
            self.add_to_table(self.next_regular_table, 0, name)
        self.update_counts()
        self.save_data()

    def add_to_table(self, table, column, name):
        row_count = table.rowCount()
        table.insertRow(row_count)
        table.setItem(row_count, column, QTableWidgetItem(name))
        table.setItem(row_count, column + 1, QTableWidgetItem("Ожидание"))

    def change_status(self, row, column):
        table = self.sender()
        if column == 1:  # Проверяем, что это колонка статуса
            current_status = table.item(row, column).text()
            new_status = self.get_next_status(current_status)
            table.setItem(row, column, QTableWidgetItem(new_status))
        self.update_counts()
        self.save_data()

    def get_next_status(self, current_status):
        if current_status == "Ожидание":
            return "Выполнено"
        elif current_status == "Выполнено":
            return "Отложено"
        elif current_status == "Отложено":
            return "Ожидание"
        return current_status

    def delete_selected_row(self):
        current_table = self.current_vip_table
        if self.current_regular_table.hasFocus():
            current_table = self.current_regular_table
        elif self.next_vip_table.hasFocus():
            current_table = self.next_vip_table
        elif self.next_regular_table.hasFocus():
            current_table = self.next_regular_table

        selected_rows = current_table.selectionModel().selectedRows()
        if selected_rows:
            reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить выбранную строку?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                for index in sorted(selected_rows):
                    current_table.removeRow(index.row())
                self.update_counts()
                self.save_data()

    def hide_completed(self):
        hide = self.hide_completed_checkbox.isChecked()
        for table in [self.current_vip_table, self.current_regular_table, self.next_vip_table, self.next_regular_table]:
            for row in range(table.rowCount()):
                if table.item(row, 1).text() == "Выполнено":
                    table.setRowHidden(row, hide)

    def transfer_to_current(self):
        for next_table, current_table in [(self.next_vip_table, self.current_vip_table),
                                          (self.next_regular_table, self.current_regular_table)]:
            for row in range(next_table.rowCount()):
                name_item = next_table.item(row, 0)
                status_item = next_table.item(row, 1)
                if name_item and status_item:
                    name = name_item.text()
                    status = status_item.text()
                    current_table.insertRow(current_table.rowCount())
                    current_table.setItem(current_table.rowCount() - 1, 0, QTableWidgetItem(name))
                    current_table.setItem(current_table.rowCount() - 1, 1, QTableWidgetItem(status))
            next_table.setRowCount(0)
        self.update_counts()
        self.save_data()

    def delete_completed(self):
        reply = QMessageBox.question(self, "Подтверждение", "Вы уверены, что хотите удалить все выполненные строки?",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            for table in [self.current_vip_table, self.current_regular_table, self.next_vip_table,
                          self.next_regular_table]:
                for row in reversed(range(table.rowCount())):
                    if table.item(row, 1).text() == "Выполнено":
                        table.removeRow(row)
            self.update_counts()
            self.save_data()

    def update_counts(self):
        self.current_vip_label.setText(f"Текущая Вип: {self.count_non_completed(self.current_vip_table)}")
        self.current_regular_label.setText(f"Текущая Обычная: {self.count_non_completed(self.current_regular_table)}")
        self.next_vip_label.setText(f"Следующая Вип: {self.count_non_completed(self.next_vip_table)}")
        self.next_regular_label.setText(f"Следующая Обычная: {self.count_non_completed(self.next_regular_table)}")

    def count_non_completed(self, table):
        count = 0
        for row in range(table.rowCount()):
            if table.item(row, 1).text() != "Выполнено":
                count += 1
        return count

    def move_up(self):
        current_table = self.current_vip_table
        if self.current_regular_table.hasFocus():
            current_table = self.current_regular_table
        elif self.next_vip_table.hasFocus():
            current_table = self.next_vip_table
        elif self.next_regular_table.hasFocus():
            current_table = self.next_regular_table

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

    def move_down(self):
        current_table = self.current_vip_table
        if self.current_regular_table.hasFocus():
            current_table = self.current_regular_table
        elif self.next_vip_table.hasFocus():
            current_table = self.next_vip_table
        elif self.next_regular_table.hasFocus():
            current_table = self.next_regular_table

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

    def save_template(self):
        template_text = self.template_input.toPlainText()
        with open("template.txt", "w") as file:
            file.write(template_text)

    def load_template(self):
        if not os.path.exists("template.txt"):
            with open("template.txt", "w") as file:
                file.write("Здесь вы выводите текст и используете переменные:\n{vip}, {norm}, {vip_next}, {norm_next}\n"
                           "Для чего? Весь этот текст переводится в файл output.txt, и его можно подключить к obs для вывода количества на экран в прямом эфире!")
        with open("template.txt", "r") as file:
            template_text = file.read()
            self.template_input.setPlainText(template_text)

    def show_help_template(self):
        help_text = ("Здесь вы выводите текст и используете переменные:\n"
                     "{vip}, {norm}, {vip_next}, {norm_next}\n"
                     "Для чего? Весь этот текст переводится в файл output.txt, и его можно подключить к obs для вывода количества на экран в прямом эфире!")
        self.template_input.setPlainText(help_text)
        with open("template.txt", "w") as file:
            file.write(help_text)

    def update_output_file(self):
        vip_count = self.count_non_completed(self.current_vip_table)
        norm_count = self.count_non_completed(self.current_regular_table)
        vip_next_count = self.count_non_completed(self.next_vip_table)
        norm_next_count = self.count_non_completed(self.next_regular_table)

        template_text = self.template_input.toPlainText()
        output_text = template_text.format(vip=vip_count, norm=norm_count, vip_next=vip_next_count,
                                           norm_next=norm_next_count)

        with open("output.txt", "w") as file:
            file.write(output_text)

    def save_data(self):
        data = {
            "current_vip": self.get_table_data(self.current_vip_table),
            "current_regular": self.get_table_data(self.current_regular_table),
            "next_vip": self.get_table_data(self.next_vip_table),
            "next_regular": self.get_table_data(self.next_regular_table)
        }
        with open("queue_data.json", "w") as file:
            json.dump(data, file)
        self.update_template_file()
        self.update_output_file()

    def load_data(self):
        if os.path.exists("queue_data.json"):
            with open("queue_data.json", "r") as file:
                data = json.load(file)
                self.set_table_data(self.current_vip_table, data.get("current_vip", []))
                self.set_table_data(self.current_regular_table, data.get("current_regular", []))
                self.set_table_data(self.next_vip_table, data.get("next_vip", []))
                self.set_table_data(self.next_regular_table, data.get("next_regular", []))
            self.update_counts()

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

    def set_table_data(self, table, data):
        table.setRowCount(0)
        for row_data in data:
            row = table.rowCount()
            table.insertRow(row)
            for column, text in enumerate(row_data):
                table.setItem(row, column, QTableWidgetItem(text))

    def update_template_file(self):
        template_text = self.template_input.toPlainText()
        vip_count = self.count_non_completed(self.current_vip_table)
        norm_count = self.count_non_completed(self.current_regular_table)
        vip_next_count = self.count_non_completed(self.next_vip_table)
        norm_next_count = self.count_non_completed(self.next_regular_table)

        # Заменяем переменные в шаблоне на их значения
        template_text = template_text.replace("{vip}", str(vip_count))
        template_text = template_text.replace("{norm}", str(norm_count))
        template_text = template_text.replace("{vip_next}", str(vip_next_count))
        template_text = template_text.replace("{norm_next}", str(norm_next_count))

        with open("output.txt", "w") as file:
            file.write(template_text)
