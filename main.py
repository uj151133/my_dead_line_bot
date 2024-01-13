import discord
import os
from keep_alive import keep_alive

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('ログインしました')

@client.event
async def on_message(message):
    bear = '\N{Teddy Bear}'
    honey = '\N{HONEY POT}'
    await message.add_reaction(bear)

TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
