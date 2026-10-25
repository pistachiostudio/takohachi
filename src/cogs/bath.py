import discord
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID

BATH = "🛀"


class Bath(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="bath", description="名前の先頭に🛀をつけます。")
    async def b(self, interaction: discord.Interaction):
        nick = interaction.user.display_name
        if nick.startswith(BATH):
            await interaction.user.edit(nick=nick.lstrip(BATH))
            message = "🛀をはずしました◎"
        else:
            await interaction.user.edit(nick=f"{BATH}{nick}")
            message = "🛀をつけました◎"
        await interaction.response.send_message(message, ephemeral=True, delete_after=5)


async def setup(bot: commands.Bot):
    await bot.add_cog(Bath(bot), guilds=[discord.Object(id=GUILD_ID)])
