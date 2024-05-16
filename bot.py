import os
from twitchio.ext import commands, pubsub
from twitchio import Client
from dotenv import load_dotenv

# Загружаем переменные окружения из файла config.env
load_dotenv(dotenv_path='config.env')

TWITCH_OAUTH_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TWITCH_CHANNEL = os.getenv('TWITCH_CHANNEL')

# Отладочная информация для проверки загрузки переменных
# print(f'TWITCH_OAUTH_TOKEN: {TWITCH_OAUTH_TOKEN}')
# print(f'TWITCH_CLIENT_ID: {TWITCH_CLIENT_ID}')
# print(f'TWITCH_CLIENT_SECRET: {TWITCH_CLIENT_SECRET}')
# print(f'TWITCH_CHANNEL: {TWITCH_CHANNEL}')

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TWITCH_OAUTH_TOKEN, prefix='!', initial_channels=[f'#{TWITCH_CHANNEL}'])
        self.loop.create_task(self.connect_pubsub())

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')
        print(f'Connected to channel: {TWITCH_CHANNEL}')

    async def event_message(self, message):
        if message.echo:
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

    # @commands.command(name='тг')
    # async def tg_command(self, ctx):
    #     await ctx.send('Чтобы не пропустить анонсы, подписывайтесь на мой телеграм канал: https://t.me/unsella')

bot = Bot()
bot.run()
