import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_formatting import *
from dotenv import load_dotenv


def connect_to_google_sheets():
    load_dotenv(dotenv_path='config.env')
    credentials_file = 'access.json'

    # Настройки для Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(credentials_file, scope)
    client = gspread.authorize(creds)

    # Имя таблицы и страницы
    SPREADSHEET_NAME = os.getenv('SPREADSHEET_NAME')
    WORKSHEET_NAME = os.getenv('WORKSHEET_NAME')

    # Откройте таблицу и лист
    spreadsheet = client.open(SPREADSHEET_NAME)
    worksheet = spreadsheet.worksheet(WORKSHEET_NAME)

    return worksheet


# Цвета
waiting_color = Color(1, 1, 0.8)  # светло-желтый
completed_color = Color(0.8, 1, 0.8)  # светло-зеленый


# Основные функции работы с очередями
def add_to_queue(worksheet, username, queue_type):
    if queue_type == "vip":
        vip_queue = worksheet.col_values(3)
        for i in range(3, len(vip_queue) + 3):
            if len(vip_queue) < i or vip_queue[i - 1] == "":
                worksheet.update_cell(i, 3, username)
                worksheet.update_cell(i, 4, "Ожидает")
                format_cell_range(worksheet, f'C{i}:D{i}', cellFormat(backgroundColor=waiting_color))
                return
        worksheet.append_row(["", "", username, "Ожидает"])
        last_row = worksheet.row_count
        format_cell_range(worksheet, f'C{last_row}:D{last_row}', cellFormat(backgroundColor=waiting_color))
    else:
        normal_queue = worksheet.col_values(1)
        for i in range(3, len(normal_queue) + 3):
            if len(normal_queue) < i or normal_queue[i - 1] == "":
                worksheet.update_cell(i, 1, username)
                worksheet.update_cell(i, 2, "Ожидает")
                format_cell_range(worksheet, f'A{i}:B{i}', cellFormat(backgroundColor=waiting_color))
                return
        worksheet.append_row([username, "Ожидает", "", ""])
        last_row = worksheet.row_count
        format_cell_range(worksheet, f'A{last_row}:B{last_row}', cellFormat(backgroundColor=waiting_color))


def get_position(worksheet, username):
    data = worksheet.get_all_values()
    vip_queue = [row[2] for row in data[2:] if row[2] != "" and row[3] == "Ожидает"]
    normal_queue = [row[0] for row in data[2:] if row[0] != "" and row[1] == "Ожидает"]

    if username in vip_queue:
        vip_position = vip_queue.index(username)
        if vip_position == 0:
            return f"Ты 1 в списке VIP очереди."
        return f"Перед тобой {vip_position} в VIP очереди. Ты {vip_position + 1} в списке VIP очереди."
    elif username in normal_queue:
        normal_position = normal_queue.index(username)
        vip_position = len(vip_queue)
        return f"Перед тобой {vip_position} в VIP очереди и {normal_position} в обычной очереди. Ты {vip_position + normal_position + 1} в списке."
    else:
        return "Ты не в очереди."



def mark_as_completed(worksheet, username):
    cell = worksheet.find(username)
    if cell:
        if cell.col == 1:
            worksheet.update_cell(cell.row, 2, "Пройдена")
            format_cell_range(worksheet, f'A{cell.row}:B{cell.row}', cellFormat(backgroundColor=completed_color))
        elif cell.col == 3:
            worksheet.update_cell(cell.row, 4, "Пройдена")
            format_cell_range(worksheet, f'C{cell.row}:D{cell.row}', cellFormat(backgroundColor=completed_color))


def get_first_waiting_user(worksheet):
    data = worksheet.get_all_values()
    vip_queue = [(row[2], row[3]) for row in data[2:] if row[2] != ""]
    normal_queue = [(row[0], row[1]) for row in data[2:] if row[0] != ""]

    # Найти первого пользователя в VIP очереди со статусом "Ожидает"
    for user, status in vip_queue:
        if status == "Ожидает":
            return user

    # Если в VIP очереди нет ожидающих, найти первого пользователя в обычной очереди со статусом "Ожидает"
    for user, status in normal_queue:
        if status == "Ожидает":
            return user
    return None


def get_queues(worksheet):
    data = worksheet.get_all_values()
    vip_queue = [(row[2], row[3]) for row in data[2:] if row[2] != ""]
    normal_queue = [(row[0], row[1]) for row in data[2:] if row[0] != ""]
    return vip_queue, normal_queue
