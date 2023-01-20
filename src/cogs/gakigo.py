from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

from .api import get_trigger_repository

class Gakigo(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.trigger_repo = get_trigger_repository()

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # botのリアクションは無視する
        if payload.member.bot:
            return
        # 該当の絵文字以外は無視
        if str(payload.emoji) != "<:p01_neko:863117588757872730>":
            return
        channel = self.bot.get_channel(payload.channel_id)
        if not channel:
            return
        message = await channel.fetch_message(payload.message_id)
        trigger = "dendou" # 固定値失礼します
        data = self.trigger_repo.select(trigger)

        if not data:
            return
        else:
            if data["response"]:
                await message.channel.send(f'{data["response"]}')
            else:
                embed = discord.Embed()
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                if data["title"]:
                    embed.title = f'{data["title"]}'
                if data["description"]:
                    embed.description = f'{data["description"]}\n\n[Check DB](https://docs.google.com/spreadsheets/d/15QCsHsmtZAs1FtiCplLmybU80WyxWw4C7G6ESf2b9f4/edit#gid=1264027664&range=A1)'
                if data["right_small_image_URL"]:
                    embed.set_thumbnail(url=f'{data["right_small_image_URL"]}')
                if data["big_image_URL"]:
                    embed.set_image(url=f'{data["big_image_URL"]}')
                embed.color = discord.Color.dark_blue()
                await message.channel.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Gakigo(bot))

