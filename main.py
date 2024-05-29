import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from src.views.main_view import MainView

def apply_styles(app):
    with open("src/assets/styles.qss", "r") as file:
        app.setStyleSheet(file.read())

def main():
    app = QApplication(sys.argv)
    apply_styles(app)

    # Set the application icon
    app.setWindowIcon(QIcon('src/assets/icons/main.png'))  # Update the path to where your icon is saved

    main_view = MainView()
    main_view.setWindowTitle("БезднаБотер 2.0")  # Set the application title
    main_view.resize(900, 800)
    main_view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
