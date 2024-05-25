import discord
from discord.ext import commands
import os
import asyncio
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# モデルの指定 (修正)
model = genai.GenerativeModel(model_name="models/chat-bison-001")

# システムメッセージの設定 (キャラクター設定を反映)
system_message = """
あなたは女子校での生活体験を提供するbotです。私は唯一の男性です。

【世界観】
・男は一人です。ただし、校則により更衣室や浴場やトイレなどはかわらず使えます。
・女子は男を見下していたり、塩対応だったり、事務的だったり、軽蔑的だったりします。
・男は一時間に一度すぐさま寝ないと死んでしまう病気を抱えています。女子たちは配慮を余儀なくされる。
・代わりに、男は女子の衣服を洗う役目をやっています。制服や下着や靴下や上履きやヒールと汗の染み付いたものを押し付けられる日々です。
・男はからかわれていじわるされて敗北する日々を送っています。

【ルール】
・地の文で進行。
・とある科学の超電磁砲のキャラクターを登場させること。台詞の前に名前を明記すること。
"""

# Discord botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 会話履歴を保存する辞書
conversation_history = {}

def split_text(text, chunk_size=1900):  # Discordの文字数制限を考慮
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.command()
async def story(ctx, *, prompt):
    user_id = ctx.author.id
    input_text = prompt

    # 会話履歴の初期化
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    try:
        # 過去の会話履歴を考慮して応答を生成
        prompt = system_message + "\n".join(conversation_history[user_id][-5:]) + "\n" + input_text  # 直近5件の履歴を使用
        response = model.generate_text(
            prompt=prompt,
            temperature=0.7,  # 応答の多様性を調整 (0.0 ~ 1.0)
            max_output_tokens=512,  # 応答の最大トークン数
        )

        # 回答を会話履歴に追加
        conversation_history[user_id].append(input_text)
        conversation_history[user_id].append(response.result)

        # 回答を送信
        splitted_text = split_text(response.result)
        for chunk in splitted_text:
            await ctx.send(chunk)
            await asyncio.sleep(1)  # 1秒待機

    except Exception as e:
        await ctx.send(f"An error occurred: {e}")

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_NONE",
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_NONE",
  },
]

bot.run(os.getenv('DISCORD_BOT_TOKEN'))
