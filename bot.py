import asyncio
import os
from twitchio.ext import commands, pubsub
from twitchio import Client
from dotenv import load_dotenv
from connect_to_sheets import connect_to_google_sheets, add_to_queue, get_position, get_queues

load_dotenv(dotenv_path='config.env')

class Bot(commands.Bot):

    def __init__(self, oauth_token, client_id, client_secret, channel):
        self.oauth_token = oauth_token
        self.client_id = client_id
        self.client_secret = client_secret
        self.channel = channel
        super().__init__(token=self.oauth_token, prefix='!', initial_channels=[f'#{self.channel}'])

        self.worksheet = connect_to_google_sheets()  # Инициализация подключения к Google Sheets

        self.loop.create_task(self.connect_pubsub())
        self.loop.create_task(self.periodic_queue_update())  # Запуск периодического обновления очереди

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'Connected to channel: {self.channel}')
        self.main_window.update_login_info(f"Logged in as | {self.nick}", f"Connected to channel: {self.channel}")

    async def event_message(self, message):
        if message.echo:
            return
        await self.handle_commands(message)

    async def connect_pubsub(self):
        client = Client(token=self.oauth_token, client_secret=self.client_secret)
        user = await client.fetch_users(names=[self.channel])
        user_id = user[0].id

        self.pubsub = pubsub.PubSubPool(client)
        topic = pubsub.channel_points(user_id)
        await self.pubsub.subscribe_topics([topic])

    async def event_channel_points(self, event):
        print(f"Награда: {event.reward.title}, Пользователь: {event.user.name}")

    # @commands.command(name='добавить')
    # async def add(self, ctx):
    #     username = ctx.author.name
    #     add_to_queue(self.worksheet, username, "normal")
    #     await ctx.send(f"{username}, ты добавлен в обычную очередь.")
    #
    # @commands.command(name='добавитьвип')
    # async def add_vip(self, ctx):
    #     username = ctx.author.name
    #     add_to_queue(self.worksheet, username, "vip")
    #     await ctx.send(f"{username}, ты добавлен в VIP очередь.")

    @commands.command(name='позиция')
    async def position(self, ctx):
        username = ctx.author.name
        position = get_position(self.worksheet, username)
        print(f"{username}, {position}")
        await ctx.send(f"{username}, {position}")

    async def periodic_queue_update(self):
        while True:
            print("Обновление очереди...")
            self.worksheet = connect_to_google_sheets()
            await asyncio.sleep(600)  # Ожидание 10 минут (600 секунд)
