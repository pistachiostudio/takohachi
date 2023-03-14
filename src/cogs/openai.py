import os

import discord
import httpx
from discord import app_commands
from discord.ext import commands

from libs.utils import get_exchange_rate


class Openai(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.default_character = "あなたは、下町の大将です。優しさはありますが、口調は乱暴です。敬語は使わなくてよいです。"
        self.cut_off = "知識のカットオフ: {knowledge_cutoff} 現在の日付: {current_date}"

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
        character:str = None
        ):

        if character is None:
            character = self.default_character + " " + self.cut_off

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

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(endpoint, headers=headers, json=payload, timeout=120)
        except httpx.HTTPError as e:
            await interaction.followup.send(f"⚠ APIリクエストエラーが発生しました。時間を置いて試してみてください。: {e}")
            return

        if res.status_code != 200:
            await interaction.followup.send(f"⚠ APIリクエストエラーが発生しました。時間を置いて試してみてください。\n Status Code: {res.status_code}")
            return

        json = res.json()

        answer = json["choices"][0]["message"]["content"]
        tokens = json["usage"]["total_tokens"]
        cost = round(tokens * 0.000002 * get_exchange_rate(), 3)

        if character == self.default_character + " " + self.cut_off:
            character = "Default"

        embed = discord.Embed()
        embed.title = f"Q. {key}"
        embed.description = answer
        embed.color = discord.Color.dark_green()
        embed.set_footer(text=f"🤖 キャラ設定: {character}\n💸 この質問の料金は {cost}円 でした。")

        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Openai(bot), guilds=[discord.Object(id=731366036649279518)])
