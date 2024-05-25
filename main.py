import discord
import os
import asyncio  # asyncioのインポートを追加

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro-latest')
chat = model.start_chat(history=[])

# システムメッセージの設定 (プロンプトに直接含める)
system_message = """
あなたは「ツンデレちゃん」です。
ツンデレな性格で、語尾に「～のよ」を付けて話します。
一人称は「私」、二人称は「あなた」です。
好きなことはゲームとアニメ、特にRPGとSFものが好きです。
嫌いなことは勉強と運動です。
口癖は「別に、あなたのためじゃないんだからね！」です。
"""

# Discord botの設定
intents = discord.Intents.default()
intents.message_content = True
discord_client = discord.Client(intents=intents)

def split_text(text, chunk_size=1900):  # Discordの文字数制限を考慮
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

@discord_client.event
async def on_ready():
    print(f'Logged in as {discord_client.user}')

@discord_client.event
async def on_message(message):
    if message.author == discord_client.user or message.author.bot:
        return

    input_text = message.content

    try:
        # テキスト生成リクエスト (システムメッセージをプロンプトに含める)
        prompt = system_message + "\n" + input_text
        response = model.generate_text(
            prompt=prompt,
            temperature=0.7,  # 応答の多様性を調整 (0.0 ~ 1.0)
            max_output_tokens=512,  # 応答の最大トークン数
        )

        # 安全性チェック（必要に応じて調整）
        for rating in response.safety_ratings:
            if rating.category in [genai.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                                  genai.HarmCategory.HARM_CATEGORY_HARASSMENT,
                                  genai.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                                  genai.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT] and \
               rating.probability >= genai.HarmProbability.HARM_PROBABILITY_LIKELY:  # 可能性が高い場合のみブロック
                await message.channel.send("申し訳ありませんが、不適切な内容を含む可能性があるため、この質問にはお答えできません。")
                return

        splitted_text = split_text(response.result)
        for chunk in splitted_text:
            await message.channel.send(chunk)
    except Exception as e:
        await message.channel.send(f"An error occurred: {e}")

discord_client.run(os.getenv('DISCORD_BOT_TOKEN'))
