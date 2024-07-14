import websocket
import json
import threading

class RewardsTracker:
    def __init__(self, user_id, client_id, auth_token, queue_view, reward_selectors):
        self.user_id = user_id
        self.client_id = client_id
        self.auth_token = auth_token
        self.queue_view = queue_view
        self.reward_selectors = reward_selectors
        self.ws = None

    def start(self):
        websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            "wss://pubsub-edge.twitch.tv",
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
            on_open=self.on_open
        )
        self.ws.run_forever()

    def stop(self):
        if self.ws:
            self.ws.close()

    def on_open(self, ws):
        print("Подключение к WebSocket...")
        topic = f'channel-points-channel-v1.{self.user_id}'
        print(f"Listening to topic: {topic}")
        ws.send(json.dumps({
            'type': 'LISTEN',
            'nonce': 'random_nonce_string',
            'data': {
                'topics': [topic],
                'auth_token': self.auth_token
            }
        }))
        print("Соединение с WebSocket установлено, слушаем награды...")

    def on_message(self, ws, message):
        print(f"Получено сообщение: {message}")
        data = json.loads(message)
        if data.get('type') == 'MESSAGE':
            msg_data = json.loads(data['data']['message'])
            if msg_data['type'] == 'reward-redeemed':
                redemption = msg_data['data']['redemption']
                reward_title = redemption['reward']['title']
                user_name = redemption['user']['login']
                user_input = redemption.get('user_input', '')
                print(f"Reward redeemed: {reward_title} by {user_name}")
                self.handle_reward(reward_title, user_name, user_input)

    def on_error(self, ws, error):
        print(f"WebSocket error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("WebSocket closed")

    def handle_reward(self, reward_title, user_name, user_input):
        # Поиск соответствия по значению
        for key, value in self.reward_selectors.items():
            if value == reward_title:
                print(f"Reward '{reward_title}' matched with key '{key}'")
                if key == "Бездна себе –":
                    self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_name, "Бездна")
                elif key == "Бездна другу –":
                    self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_input, "Бездна")
                    self.queue_view.add_comment_to_last_row(self.queue_view.current_regular_table, f'заказал {user_name}')
                elif key == "Обзор себе –":
                    self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_name, "Обзор")
                elif key == "Обзор другу –":
                    self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_input, "Обзор")
                    self.queue_view.add_comment_to_last_row(self.queue_view.current_regular_table, f'заказал {user_name}')
                elif key == "Театр себе –":
                    self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_name, "Театр")
                elif key == "Театр другу –":
                    self.queue_view.add_to_table(self.queue_view.current_regular_table, 0, user_input, "Театр")
                    self.queue_view.add_comment_to_last_row(self.queue_view.current_regular_table, f'заказал {user_name}')
                self.queue_view.update_counts()
                self.queue_view.save_data()
                print(f"Reward '{reward_title}' processed for user {user_name}")
