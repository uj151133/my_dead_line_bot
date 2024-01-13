import discord
import os
from keep_alive import keep_alive
from google.oauth2.service_account import Credentials
import gspread

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    "./windy-winter-407404-2140fc1dd60b.json/",
    scopes=scopes
)

gc = gspread.authorize(credentials)

client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('ログインしました')

@client.event
async def on_message(message):
    balloon = '\N{BALLOON}'
    await message.add_reaction(balloon)
    # await message.channel.send(balloon)

TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
