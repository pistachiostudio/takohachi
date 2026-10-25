import discord
from discord import app_commands
from discord.ext import commands

from settings import GUILD_ID


class Purge(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="purge", description="[admin] Purge message")
    # default_permissions はサーバー側の設定で変えられるため、実行時にも管理者かどうかを確認する。
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(amount="削除するメッセージの数(1〜1000)")
    async def purge(
        self, interaction: discord.Interaction, amount: app_commands.Range[int, 1, 1000]
    ):
        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(
            limit=amount,
            check=lambda message: not message.pinned,
            reason=f"by admin purge commands ({interaction.user})",
        )
        await interaction.followup.send(f"{len(deleted)} 件削除しました。", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Purge(bot), guilds=[discord.Object(id=GUILD_ID)])
