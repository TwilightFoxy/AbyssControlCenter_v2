import os

def save_config(oauth_token, client_id, client_secret, channel):
    config_data = (
        f"TWITCH_OAUTH_TOKEN={oauth_token}\n"
        f"TWITCH_CLIENT_ID={client_id}\n"
        f"TWITCH_CLIENT_SECRET={client_secret}\n"
        f"TWITCH_CHANNEL={channel}\n"
    )

    with open("config.env", "w") as config_file:
        config_file.write(config_data)

def load_config():
    if not os.path.exists("config.env"):
        return None

    config = {}
    with open("config.env", "r") as config_file:
        for line in config_file:
            key, value = line.strip().split('=', 1)
            config[key] = value
    return config
