import discord
import os
import asyncio  # asyncioのインポートを追加

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('models/chat-bison-001')
chat = model.start_chat(history=[])

### discord initial
intents = discord.Intents.default()
intents.message_content = True
discord = discord.Client(intents=intents)

def split_text(text, chunk_size=1500):
  # テキスト文字列をchunk_sizeで指定した大きさに分割し、リストに格納する
  return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@discord.event
async def on_ready():
  print(f'We have logged in as {discord.user}')

@discord.event
async def on_message(message):
  if message.author == discord.user:
    return
  if message.author.bot == True:
    return

  input_text = message.content

  answer = chat.send_message(input_text)

  splitted_text = split_text(answer.text)
  for chunk in splitted_text:
    await message.channel.send(chunk)
    await asyncio.sleep(1)  # 1秒待機

discord.run(os.environ['DISCORD_BOT_TOKEN'])
