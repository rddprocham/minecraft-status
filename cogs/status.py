import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer

from dotenv import load_dotenv
import os

import json

import datetime

THRESHOLD = 3

#Load env variables
load_dotenv()

with open("emojis.json","r") as f:
     emojis = json.load(f)

DISCORD_SERVER = int(os.getenv("DISCORD_SERVER"))
CHANNEL = int(os.getenv("STATUS-CHANNEL"))
ADMIN_CHANNEL = int(os.getenv("ADMIN_CHANNEL"))

import asyncio
class Status(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_message.start()
        # self.check_threshold.start()
        self.msg = None
        self.count_to_stop = 0
    
    # @commands.command()
    # async def no-notify(self, ctx, time_to_wait_num, time_to_wait_unit):
    #     options = {
    #          "s":1,
    #          "m":60,
    #          "h":3600,
    #          "d":86400
    #     }
    #     options_str = {
    #          "s":"secondes",
    #          "m":"minutes",
    #          "h":"heures",
    #          "d":"jours"
    #     }

    #     time_value = time_to_wait_num * options[time_to_wait_unit]

    #     time_now = datetime.datetime.now()

    #     time_future = time_now 

    #     timestamp = time_future.timestamp()
    #     with open("no_notify.json", "w") as f:
    #         json.dump({"time": timestamp}, f)

        

    #     # Send a confirmation message
    #     await ctx.send(f"Vous ne recevrez plus de notifications pendant {time_value}.")

    @commands.Cog.listener()
    async def on_ready(self):
        guild = self.bot.get_guild(DISCORD_SERVER)
        if guild is None:
            print(f"Guild with ID {DISCORD_SERVER} not found.")
            return
        
        channel = guild.get_channel(CHANNEL)
        if channel is None:
            print(f"Channel with ID {CHANNEL} not found in guild {DISCORD_SERVER}.")
            return
        
        embed = discord.Embed(title="Statut du serveur")
        embed.add_field(name="IP",
            value=os.getenv("MINECRAFT_SERVER"),
            inline=False)
                    
        embed.add_field(name="Statut",
            value=f"Chargement {emojis['loading']}",
            inline=False)
        try:
            # Fetch the first message in the channel
            async for message in channel.history(limit=1, oldest_first=True):
                self.msg = message
                break
            if self.msg is None:  # No messages in the channel
                raise discord.NotFound
        except:
            self.msg = await channel.send(embed=embed)
        
        print("Message stored successfully.")



    def cog_unload(self):
        self.send_message.cancel()

    @tasks.loop(seconds=20)
    async def send_message(self):
        await asyncio.sleep(3)
        try:
                    server = JavaServer.lookup(os.getenv("MINECRAFT_SERVER"))
                    status = server.status()

                    embed = discord.Embed(title="Statut du serveur",colour=0x4bb543)

                    embed.add_field(name="IP",
                                    value=os.getenv("MINECRAFT_SERVER"),
                                    inline=False)
                    embed.add_field(name="Statut",
                                    value=f"En ligne {emojis['done']}",
                                    inline=False)
                    embed.add_field(name="Ping",
                                    value=f"{round(status.latency)}ms",
                                    inline=False)
                    embed.add_field(name="Nombre de joueurs",
                                    value=f"{status.players.online}",
                                    inline=False),
                    embed.add_field(name="Version",
                                    value="1.20.6",
                                    inline=False)


                # await channel.send(embed=embed)
                    await self.msg.edit(embed=embed)
                    self.count_to_stop = 0
        except Exception:
                    embed = discord.Embed(title="Statut du serveur",colour=0xfc100d)
                    embed.add_field(name="IP",
                                    value=os.getenv("MINECRAFT_SERVER"),
                                    inline=False)
                    embed.add_field(name="Statut",
                                    value=f"Hors-ligne {emojis['failed']}",
                                    inline=False)

                    await self.msg.edit(embed=embed)
                    self.count_to_stop += 1

    # @tasks.loop(seconds=5)
    # async def check_threshold(self):
    #     if self.count_to_stop == THRESHOLD:
    #         guild = self.bot.get_guild(DISCORD_SERVER)
    #         if guild is None:
    #             print(f"Guild with ID {DISCORD_SERVER} not found.")
    #             return
            
    #         channel = guild.get_channel(ADMIN_CHANNEL)
    #         if channel is None:
    #             print(f"Channel with ID {ADMIN_CHANNEL} not found in guild {DISCORD_SERVER}.")
    #             return
    #         await channel.send(f"{emojis['failed']} Il semblerait que le serveur soit hors-ligne! ||{os.getenv('ADMIN_ROLE_TO_PING')}||\n-#Besoin de désactiver le message? Exécutez la commande .no-notify")

    @send_message.before_loop
    # @check_threshold.before_loop
    async def before_send_message(self):
        await self.bot.wait_until_ready()

        
    async def cog_load(self):
        print(f"{self.__class__.__name__} loaded!")

async def setup(bot):
    await bot.add_cog(Status(bot=bot))


