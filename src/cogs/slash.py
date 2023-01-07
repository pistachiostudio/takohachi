import discord
from discord import app_commands
from discord.ext import commands


class Slash(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="slash_test",
        description="first slash commands!")

    async def introduce(
        self,
        interaction: discord.Interaction,
        name: str,
        age: int
    ):

        await interaction.response.send_message(f"Hello, my name is {name} and I am {age} years old!")

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Slash(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
