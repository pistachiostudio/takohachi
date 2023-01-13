import discord
from discord import app_commands
from discord.ext import commands


class Ping(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="ping",
        description="Catch the ping of the bot!"
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):

        latency: float = self.bot.latency
        latency_ms: int = round(latency * 1000)

        await interaction.response.send_message(f'🏓Pong! ({latency_ms}ms)')

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Ping(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
