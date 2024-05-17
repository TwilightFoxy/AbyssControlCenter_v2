import subprocess
import sys
#
#
# def upgrade_pip():
#     subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
#
#
# def install(package):
#     subprocess.check_call([sys.executable, "-m", "pip", "install", package])
#
#
# required_packages = [
#     "PyQt5",
#     "webbrowser",
#     "gspread",
#     "oauth2client",
#     "gspread-formatting",
#     "python-dotenv",
#     "twitchio",
# ]
#
# for package in required_packages:
#     try:
#         __import__(package)
#     except ImportError:
#         install(package)

from PyQt5.QtWidgets import QApplication
from twitch_bot_ui import TwitchBotApp


def main():
    app = QApplication(sys.argv)
    window = TwitchBotApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
