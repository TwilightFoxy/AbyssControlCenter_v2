import sys
from PyQt5.QtWidgets import QApplication
from twitch_bot_ui import TwitchBotApp

def main():
    app = QApplication(sys.argv)
    window = TwitchBotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
