import os

import discord
from discord import app_commands
from discord.ext import commands

from libs.embed import create_embed
from libs.http_client import HTTPClient, handle_api_error
from settings import GUILD_ID

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

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={GEMINI_API_KEY}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": character}, {"text": key}]}]}

        try:
            client = HTTPClient()
            response = await client.post(url, json=payload, headers=headers, timeout=120)
            answer = response["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            await handle_api_error(interaction, e, "Gemini API")
            return

        if character == self.default_character:
            character = "Default"

        embed = create_embed(
            title=f"Q. {key}",
            description=answer,
            color=discord.Color.dark_green(),
            footer_text=f" Model: gemini-2.5-pro-exp-03-25\n🪀 キャラ設定: {character}",
        )

        await interaction.followup.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Gemini(bot), guilds=[discord.Object(id=GUILD_ID)])
