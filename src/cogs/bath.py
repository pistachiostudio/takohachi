import discord
from discord import app_commands
from discord.ext import commands


class Bath(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="bath",
        description="名前の先頭に🛀をつけます。"
    )
    async def b(
        self,
        interaction: discord.Interaction
    ):

        before_nick = interaction.user.display_name
        message = interaction.message
        rtn = before_nick.startswith('🛀')

        if rtn is False:
            after_nick = f'🛀{before_nick}'
            await interaction.user.edit(nick=after_nick)
            await interaction.response.send_message(
                f"🛀をつけました◎",
                ephemeral=True,
                delete_after=5
            )
            pass

        if rtn is True:
            after_nick = before_nick.lstrip('🛀')
            await interaction.user.edit(nick=after_nick)
            await interaction.response.send_message(
                f"🛀をはずしました◎",
                ephemeral=True,
                delete_after=5
            )
            pass

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Bath(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
