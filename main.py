import discord
import os

import google.generativeai as genai
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash-latest')
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

discord.run(os.environ['DISCORD_BOT_TOKEN'])