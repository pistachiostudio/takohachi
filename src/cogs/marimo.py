import datetime
import random

import discord
from discord import app_commands
from discord.ext import commands


class Marimo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="mt",
        description="まりもたいむ"
    )
    async def mt(
        self,
        interaction: discord.Interaction
    ):

        # summer time == hours=-4, not == hours=-5
        now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4)))
        pnow = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+1)))
        JST = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=+9)))
        marimo_time = f"{now.month}/{now.day} {now.hour}:{now.minute:02}"
        paul_time = f"{pnow.month}/{pnow.day} {pnow.hour}:{pnow.minute:02}"
        japan_time = f"{JST.month}/{JST.day} {JST.hour}:{JST.minute:02}"

        #slot
        slot_list = ['🍒', '🔔', '🍉', '🍇', '🍋', '🐈', '🐬', '🦕', '🐢', '🐕']
        slot_left = random.choice(slot_list)
        slot_center = random.choice(slot_list)
        slot_right = random.choice(slot_list)

        # interaction.response.send_message() は、一回のみしか使えないので、
        # 2.0から追加されたembedsで対応する。
        embed1 = discord.Embed()
        embed1.color = discord.Color.dark_green()
        embed1.set_footer(text=f"mt slot: {slot_left}{slot_center}{slot_right}")
        embed1.description = f"marimo time = **{marimo_time}**\npaul time = **{paul_time}**\n(In Japan = {japan_time})"

        embed2 = discord.Embed()
        embed2.color = discord.Color.dark_green()
        embed2.description = f"🎉Congratulations!! {interaction.user.mention} hits the Jackpot!!🎉"

        if slot_left == slot_center == slot_right:
            embeds = [embed1, embed2]
        else:
            embeds = [embed1]

        await interaction.response.send_message(embeds=embeds)

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Marimo(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
