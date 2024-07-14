import gspread
from oauth2client.service_account import ServiceAccountCredentials


class GoogleSheetsSync:
    def __init__(self, sheet_id):
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name('data/access.json', scope)
        self.client = gspread.authorize(creds)
        self.sheet = self.client.open_by_key(sheet_id)

    def update_sheet(self, sheet_name, headers, data):
        try:
            worksheet = self.sheet.worksheet(sheet_name)
        except gspread.WorksheetNotFound:
            worksheet = self.sheet.add_worksheet(title=sheet_name, rows="100", cols="20")

        worksheet.clear()

        # Вставка объединенных ячеек для каждой секции
        sections = ["Текущая Вип", "Текущая Обычная", "Следующая Вип", "Следующая Обычная"]
        row_offset = 1

        for section, section_data in zip(sections, data):
            worksheet.merge_cells(row_offset, 1, row_offset, len(headers))
            worksheet.update_cell(row_offset, 1, section)
            row_offset += 1
            worksheet.append_row(headers)
            row_offset += 1
            if section_data:
                worksheet.append_rows(section_data)
                row_offset += len(section_data) + 1

        # Окраска строк в зависимости от статуса
        cell_list = worksheet.range(f'B2:B{worksheet.row_count}')
        for cell in cell_list:
            if cell.value == "Ожидание":
                cell.color = (1, 1, 0)  # Yellow
            elif cell.value == "Выполнено":
                cell.color = (0, 1, 0)  # Green
            elif cell.value == "Отложено":
                cell.color = (1, 0, 0)  # Red
        worksheet.update_cells(cell_list)
