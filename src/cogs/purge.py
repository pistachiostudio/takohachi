import discord
from discord import app_commands
from discord.ext import commands


class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="purge",
        description="[admin] Purge message"
    )

    @app_commands.default_permissions(administrator=True)

    @app_commands.describe(
        amount="削除するメッセージの数"
    )

    async def purge(
        self,
        interaction: discord.Interaction,
        amount: int
    ):

        await interaction.response.defer()

        channel = interaction.channel

        def is_not_pinned(message):
            return not message.pinned

        await channel.purge(
            limit=amount,
            check=is_not_pinned,
            reason="by admin purge commands"
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Purge(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
