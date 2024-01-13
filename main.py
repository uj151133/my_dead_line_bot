import discord
import os
from keep_alive import keep_alive
from google.oauth2.service_account import Credentials
import gspread
from datetime import timedelta, timezone

@tasks.loop(minutes=1)
async def loop():
 if(is_ready):   
   JST = timezone(timedelta(hours=+9), 'JST')
   now_minutes = datetime.now(JST).minute
   now_hour = datetime.now(JST).hour
   
   if(judge_whether_0minutes_now(now_minutes)):  
     # 0時0分の場合は〆切の残り日数を1減らす
     if(now_hour == 0):
       decrement_days_to_last()

     # 0分の場合、現在時刻と〆切残り日数より、アナウンスを行うか判定する
     data_list = read_from_spreadsheet()
     for data in data_list:
       days_to_last = data[2]       
       
       # アナウンスを行うか判定している
       if(judge_to_do_announce(days_to_last, now_hour)):
         # アナウンスに必要な情報を集める
         channel_id = data[0]
         channel = search_channel(int(channel_id))
         user_id = int(data[1])
         user_to_mention = await bot.fetch_user(user_id)
         task = data[3]
         
         message_add_to_last = generate_message(days_to_last)
         # アナウンスを行う
         await announce_deadline(channel, user_to_mention, task, days_to_last, message_add_to_last)

# 〆切日数と現在の時間から、アナウンスをするか判定する
def judge_to_do_announce(days_to_last, now_hour):
 # 〆切まで4日以上ある場合はアナウンスしない
 if(days_to_last > 3):
   return False
 # 0時ちょうどの場合、アナウンスする
 elif(now_hour == 0):
   return True
 # 〆切を過ぎたら3時間ごとに、9~24時にアナウンスを行う
 elif(days_to_last < 0 and now_hour % 3 == 0):
   return now_hour > 8 or now_hour == 0
 # 〆切まで0~3日かつ24時以外の場合、アナウンスしない
 else:
   return False

def judge_whether_0minutes_now(now_minutes):
    return True if now_minutes == 0 else False


    
    

scopes = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

credentials = Credentials.from_service_account_file(
    "windy-winter-407404-2140fc1dd60b.json",
    scopes=scopes
)

gc = gspread.authorize(credentials)
spreadsheet_url = "https://docs.google.com/spreadsheets/d/1TyrjjfosTpoREEX4UFBIH1Y7lgpk_L6L4UU-q5SX-cs/edit?usp=sharing"
workbook = gc.open_by_url(spreadsheet_url)
worksheet = worksheet.sheet1

def read_from_spreadsheet():
    return spreadsheet.sheet1.get_all_values()

def decrement_days_to_last() -> None:
    col_list = worksheet.col_values(2)
    for i in range(1, len(col_list)  - 1):
        worksheet.update_cell(i, 2, col_list[i] - 1)
    return


client = discord.Client(intents=discord.Intents.default())

@client.event
async def on_ready():
    print('ログインしました')

@client.event
async def on_message(message):
    balloon = '\N{BALLOON}'
    await message.add_reaction(balloon)
    await message.channel.send(spreadsheet.sheet1.get_all_values())

TOKEN = os.getenv("DISCORD_TOKEN")
# Web サーバの立ち上げ
keep_alive()
client.run(TOKEN)
