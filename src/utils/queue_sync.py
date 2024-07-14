import json
from PyQt6.QtCore import QTimer

class QueueSync:
    def __init__(self, queue_view, google_sheets_sync):
        self.queue_view = queue_view
        self.google_sheets_sync = google_sheets_sync

        self.timer = QTimer()
        self.timer.timeout.connect(self.sync_with_google_sheets)
        self.timer.start(60000)  # Синхронизация каждые 60 секунд

    def sync_with_google_sheets(self):
        try:
            data = self.load_local_data()
            self.google_sheets_sync.update_google_sheet(data)
            google_data = self.google_sheets_sync.read_google_sheet()
            self.update_local_data(google_data)
        except Exception as e:
            print(f"Ошибка при синхронизации с Google Sheets: {e}")

    def load_local_data(self):
        with open("data/queue_data.json", "r") as file:
            return json.load(file)

    def update_local_data(self, data):
        with open("data/queue_data.json", "w") as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        self.queue_view.update_from_json(data)
