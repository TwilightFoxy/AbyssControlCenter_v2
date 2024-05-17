import os
import json

CONFIG_FILE = 'config.env'
COMMANDS_FILE = 'commands.json'


def save_config(oauth_token, client_id, client_secret, channel, spreadsheet_name, worksheet_name):
    config = {
        'TWITCH_OAUTH_TOKEN': oauth_token,
        'TWITCH_CLIENT_ID': client_id,
        'TWITCH_CLIENT_SECRET': client_secret,
        'TWITCH_CHANNEL': channel,
        'SPREADSHEET_NAME': spreadsheet_name,
        'WORKSHEET_NAME': worksheet_name
    }
    try:
        with open(CONFIG_FILE, 'w') as file:
            for key, value in config.items():
                file.write(f"{key}={value}\n")
    except Exception as e:
        pass


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return None

    config = {}
    try:
        with open(CONFIG_FILE, 'r') as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split('=', 1)
                config[key] = value
    except Exception as e:
        pass
    return config


def load_commands():
    if not os.path.exists(COMMANDS_FILE):
        default_commands = [{'command': 'привет', 'response': 'Привет!'}]
        try:
            with open(COMMANDS_FILE, 'w') as file:
                json.dump(default_commands, file)
        except Exception as e:
            pass
        return default_commands

    try:
        with open(COMMANDS_FILE, 'r') as file:
            commands = json.load(file)
    except json.JSONDecodeError:
        default_commands = [{'command': 'привет', 'response': 'Привет!'}]
        try:
            with open(COMMANDS_FILE, 'w') as file:
                json.dump(default_commands, file)
        except Exception as e:
            pass
        return default_commands
    except Exception as e:
        return []
    return commands


def save_command(command, response):
    if not command or not response:
        return False, "Команда и ответ не могут быть пустыми."

    try:
        commands = load_commands()

        for cmd in commands:
            if cmd['command'] == command:
                return False, "Команда уже существует."

        commands.append({'command': command, 'response': response})

        with open(COMMANDS_FILE, 'w') as file:
            json.dump(commands, file)

        return True, "Команда успешно сохранена."
    except Exception as e:
        return False, str(e)


def delete_command(command):
    try:
        commands = load_commands()
        commands = [cmd for cmd in commands if cmd['command'] != command]

        with open(COMMANDS_FILE, 'w') as file:
            json.dump(commands, file)

        return True, "Команда успешно удалена."
    except Exception as e:
        return False, str(e)