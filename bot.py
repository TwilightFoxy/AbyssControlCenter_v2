import os
import json
from twitchio.ext import commands, pubsub
from twitchio import Client
from dotenv import load_dotenv
from connect_to_sheets import add_to_queue, get_position

load_dotenv(dotenv_path='config.env')

TWITCH_OAUTH_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TWITCH_CHANNEL = os.getenv('TWITCH_CHANNEL')


class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TWITCH_OAUTH_TOKEN, prefix='!', initial_channels=[f'#{TWITCH_CHANNEL}'])
        self.loop.create_task(self.connect_pubsub())
        self.load_custom_commands()

    def load_custom_commands(self):
        with open('commands.json', 'r', encoding='utf-8') as file:
            self.custom_commands = json.load(file)

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'Connected to channel: {TWITCH_CHANNEL}')
        self.main_window.update_login_info(f'Logged in: {self.nick}', f'Connected to channel: {TWITCH_CHANNEL}')

    async def event_message(self, message):
        if message.echo:
            return

        # Проверка на пользовательские команды
        for command in self.custom_commands:
            if message.content.lower() == f"!{command['command']}":
                await message.channel.send(command['response'])
                return

        await self.handle_commands(message)

    async def connect_pubsub(self):
        client = Client(token=TWITCH_OAUTH_TOKEN, client_secret=TWITCH_CLIENT_SECRET)
        user = await client.fetch_users(names=[TWITCH_CHANNEL])
        user_id = user[0].id

        self.pubsub = pubsub.PubSubPool(client)
        topic = pubsub.channel_points(user_id)
        await self.pubsub.subscribe_topics([topic])

    async def event_channel_points(self, event):
        print(f"Награда: {event.reward.title}, Пользователь: {event.user.name}")

    @commands.command(name='привет')
    async def hello_command(self, ctx):
        await ctx.send(f'Привет, {ctx.author.name}!')

    @commands.command(name='тг')
    async def tg_command(self, ctx):
        await ctx.send('Чтобы не пропустить анонсы, подписывайтесь на мой телеграм канал: https://t.me/unsella')

    @commands.command(name='добавить')
    async def add(self, ctx):
        username = ctx.author.name
        add_to_queue(username, "normal")
        await ctx.send(f"{username}, ты добавлен в обычную очередь.")

    @commands.command(name='добавитьвип')
    async def add_vip(self, ctx):
        username = ctx.author.name
        add_to_queue(username, "vip")
        await ctx.send(f"{username}, ты добавлен в VIP очередь.")

    @commands.command(name='позиция')
    async def position(self, ctx):
        username = ctx.author.name
        position = get_position(username)
        await ctx.send(f"{username}, {position}")


bot = Bot()
