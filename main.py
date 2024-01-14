import discord
import os
from keep_alive import keep_alive
from google.oauth2.service_account import Credentials
import gspread
import datetime
from datetime import timedelta, timezone, datetime
from discord.ext import tasks, commands
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

client = discord.Client(intents=discord.Intents.default())

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    "windy-winter-407404-2140fc1dd60b.json",
    scopes=scopes
)

gc = gspread.authorize(credentials)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1TyrjjfosTpoREEX4UFBIH1Y7lgpk_L6L4UU-q5SX-cs/edit?usp=sharing"
workbook = gc.open_by_url(spreadsheet_url)
worksheet = workbook.sheet1

# 〆切日数と現在の時間から、アナウンスをするか判定する
def judge_to_do_announce(days_to_last, now_hour):
  # 〆切まで4日以上ある場合はアナウンスしない
  # if(int(days_to_last) > 3):
  #   return False
  # # 0時ちょうどの場合、アナウンスする
  # elif(now_hour == 0):
  #   return True
  # # 〆切を過ぎたら3時間ごとに、9~24時にアナウンスを行う
  # elif(int(days_to_last) < 0 and now_hour % 3 == 0):
  #   return now_hour > 8 or now_hour == 0
  # # 〆切まで0~3日かつ24時以外の場合、アナウンスしない
  # else:
  #   return False
  return True

def search_channel(channel_id):
  return client.get_channel(channel_id)

def judge_whether_0minutes_now(now_minutes):
    return True if now_minutes == 0 else False

def generate_message(user_to_mention, task, days_to_last):
  # member_mention = "<@" + str(user_to_mention) + ">"
  member_mention = user_to_mention.mention
  if int(days_to_last) == 3:
    return f"{member_mention}{task}が残ってるくさいよん。{days_to_last}日後だよん。"
  elif int(days_to_last) == 2:
    return f"{member_mention}まだ{task}終わってないの？いつになったらやるんかね。あと{days_to_last}日ね。"
  elif int(days_to_last) == 1:
    return f"{member_mention}おい前日ににやるなって笑{task}そんなにすぐ終わらんて。今日は寝れないねー。"
  elif int(days_to_last) == 0:
    return f"{member_mention}今日だから。よろしくね。"
  elif int (days_to_last) < 0:
    return f"{member_mention}おや？おかしいな。"
  

async def announce_deadline(channel, message):
  await channel.send(message)


def read_from_spreadsheet():
    return worksheet.get_all_values()

def decrement_days_to_last() -> None:
    col_list = worksheet.col_values(2)
    for i in range(1, len(col_list)  - 1):
        worksheet.update_cell(i, 2, int(col_list[i]) - 1)
    return

# 返信する非同期関数を定義
async def reply(message):
  reply = f'{message.author.mention} 〆切を登録しました。'  # 返信メッセージの作成
  await message.channel.send(reply)  # 返信メッセージを送信





@tasks.loop(minutes=1)
async def reminder():
  if(client.is_ready):   
    JST = timezone(timedelta(hours=+9), 'JST')
    now_minutes = datetime.now(JST).minute
    now_hour = datetime.now(JST).hour
    if(judge_whether_0minutes_now(now_minutes)):  
      # 0時0分の場合は〆切の残り日数を1減らす
      if(now_hour == 0):
        decrement_days_to_last()
      # 0分の場合、現在時刻と〆切残り日数より、アナウンスを行うか判定する
      all_data_list = read_from_spreadsheet()
      data_list = all_data_list[1:]
      for data in data_list:
        days_to_last = data[2]       
        # アナウンスを行うか判定している
        if(judge_to_do_announce(days_to_last, now_hour)):
          # アナウンスに必要な情報を集める
          channel_id = data[0]
          channel = search_channel(int(channel_id))
          user_id = int(data[1])
          user_to_mention = await client.fetch_user(user_id)
          task = data[3]
          message = generate_message(user_to_mention, task, days_to_last)
          # アナウンスを行う
          announce_deadline(channel, message)

@client.event
async def on_ready():
  print('ログインしました')
  reminder.start()

@client.event
async def on_message(message):
  # botのメッセージなら何もしない
  if message.author.bot:
    return
  if client.user in message.mentions:  # 話しかけられたかの判定
    balloon = '\N{BALLOON}'
    await message.add_reaction(balloon)
    data_list = read_from_spreadsheet()
    user_to_mention = await client.fetch_user(data_list[1][1])
    channel = search_channel(int(data_list[1][0]))
    # await reply(message)
    decrement_days_to_last()
    # await channel.send(generate_message(user_to_mention, data_list[1][3], data_list[1][2]))
    
@bot.command()
async def ping(ctx):
    await ctx.send('pong')


TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)

