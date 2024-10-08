import discord
from discord.ext import commands

import os

from dotenv import load_dotenv

#Load env variables
load_dotenv()

class StatusBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='ccb ', intents=discord.Intents().all())

    async def setup_hook(self):
        for filename in os.listdir("cogs"):
            if filename.endswith('.py'):
                await self.load_extension(f'cogs.{filename[:-3]}')

    async def on_ready(self):
        print("Bot is ready")

StatusBot().run(os.getenv("DISCORD_BOT_TOKEN"))