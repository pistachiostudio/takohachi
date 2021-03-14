from discord.ext import commands
from discord.ext import tasks
from datetime import datetime

class Notify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notifier.start()
        self.channel = None


    def cog_unload(self):
        self.notifier.cancel()

    @commands.command()
    async def set_notify_channel(self, ctx):
        self.channel = ctx.channel
        await ctx.send(f"「{ctx.channel.name}」に時報を通知します！")


    @tasks.loop(seconds=10.0)
    async def notifier(self):
        print("start_notifier")
        now = datetime.now()
        if self.channel:
            await self.channel.send(f"{now.strftime('%Y/%m/%d %H:%M:%S')} now!")

    @notifier.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()
        print("start")

    @notifier.after_loop
    async def after_check(self):
        print("end")


def setup(bot):
    bot.add_cog(Notify(bot))