import os

import discord
import httpx
from discord import app_commands
from discord.ext import commands

from libs.utils import get_exchange_rate


class Openai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="gpt",
        description="ChatGPTに質問をしましょう！"
        )

    @app_commands.describe(
        key="質問内容",
        character="ChatGPTに性格やキャラを与えることができます。必ず「あなたは～です。」と書いてください。"
        )

    async def openai(
        self,
        interaction: discord.Interaction,
        key: str,
        character:str = "あなたは、OpenAI によってトレーニングされた大規模な言語モデルである ChatGPT です。できるだけ簡潔に答えてください。知識のカットオフ: {knowledge_cutoff} 現在の日付: {current_date}"
        ):

        await interaction.response.defer()

        endpoint = "https://api.openai.com/v1/chat/completions"

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}'
        }

        payload = {
            "model": "gpt-3.5-turbo",
            "messages" : [
                {"role": "system", "content": character},
                {"role": "user", "content": key}
            ],
            "max_tokens": 1000
        }

        async with httpx.AsyncClient() as client:
            res = await client.post(endpoint, headers=headers, json=payload)
        json = res.json()

        answer = json["choices"][0]["message"]["content"]
        tokens = json["usage"]["total_tokens"]
        cost = round(tokens * 0.000002 * get_exchange_rate(), 3)

        if character == "あなたは、OpenAI によってトレーニングされた大規模な言語モデルである ChatGPT です。できるだけ簡潔に答えてください。知識のカットオフ: {knowledge_cutoff} 現在の日付: {current_date}":
            character = "Default"

        embed = discord.Embed()
        embed.title = f"Q. {key}"
        embed.description = answer
        embed.color = discord.Color.dark_green()
        embed.set_footer(text=f"🤖 キャラ設定: {character}\n💸 この質問の料金は {cost}円 でした。")

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Openai(bot), guilds=[discord.Object(id=731366036649279518)])
