from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QAbstractItemView
from PyQt6.QtCore import pyqtSignal


class DraggableTableWidget(QTableWidget):
    drop_completed = pyqtSignal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('application/x-qabstractitemmodeldatalist'):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        source = event.source()
        if isinstance(source, QTableWidget) and source != self:
            selected_items = source.selectedItems()
            if not selected_items:
                return

            row_positions = sorted(set(item.row() for item in selected_items))
            new_rows = []
            for row in row_positions:
                row_data = []
                for column in range(source.columnCount()):
                    item = source.item(row, column)
                    row_data.append(item.text() if item else '')

                new_row = self.rowCount()
                self.insertRow(new_row)
                new_rows.append(new_row)
                for column, text in enumerate(row_data):
                    self.setItem(new_row, column, QTableWidgetItem(text))

                source.removeRow(row)

            self.resizeColumnsToContents()
            self.drop_completed.emit((self, new_rows))
            event.accept()
        elif isinstance(source, QTableWidget) and source == self:
            # If dragging within the same table, cancel the event
            event.ignore()
        else:
            super().dropEvent(event)
