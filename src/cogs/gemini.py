import os

import discord
import httpx
from discord import app_commands
from discord.ext import commands

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class Gemini(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.default_character = "あなたはチャットコミュニティのみんなに愛されるBotです。みんなからくるいろんな質問にバッチリ答えてね。"  # noqa: E501

    @app_commands.command(name="gemini", description="Geminiに質問をしましょう！")
    @app_commands.describe(
        key="質問内容",
        character="Geminiに性格やキャラを与えることができます。必ず「あなたは～です。」と書いてください。",
    )  # noqa: E501
    async def gemini(self, interaction: discord.Interaction, key: str, character: str = None):
        if character is None:
            character = self.default_character

        await interaction.response.defer()

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro-exp-03-25:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": character}, {"text": key}]}]}

        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, headers=headers, json=payload, timeout=120)
                res.raise_for_status()
                json = res.json()
                answer = json["candidates"][0]["content"]["parts"][0]["text"]
        except httpx.HTTPError as e:
            await interaction.followup.send(
                f"⚠ APIリクエストエラーが発生しました。時間を置いて試してみてください。: {e}"
            )
            return
        except Exception as e:
            await interaction.followup.send(
                f"⚠ 予期せぬエラーが発生しました。時間を置いて試してみてください。: {e}"
            )
            return

        if character == self.default_character:
            character = "Default"

        embed = discord.Embed()
        embed.title = f"Q. {key}"
        embed.description = answer
        embed.color = discord.Color.dark_green()
        embed.set_footer(
            text=f" Model: gemini-2.5-pro-exp-03-25\n🪀 キャラ設定: {character}"
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Gemini(bot), guilds=[discord.Object(id=731366036649279518)])
