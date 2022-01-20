from discord.ext import commands
import discord
from datetime import datetime, timedelta, timezone


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def help(self, ctx):

        embed = discord.Embed()
        embed.set_thumbnail(url='https://raw.githubusercontent.com/pistachiostudio/takohachi/master/images/icon_tako_hachi_BG_less.png')
        embed.title = "takohachi commands help"
        embed.color = discord.Color.blue()
        embed.description = """
        Prefix は `!!` です。
        [View more info on GitHub](https://github.com/pistachiostudio/takohachi/blob/master/mannual.md)

        **mt**
        ```まりもたいむ！```
        **whatToday**
        ```今日はなんの日？```
        **apexrank <A> <B>**
        ```APEXのランクポイントを表示します。
A = origin or psn or xbl
B = YourID```
        **sp <SEARCH>**
        ```Spotifyの曲情報をゲットします。```
        **spartist <ARTIST>**
        ```Spotifyのアーティスト情報をゲットします。```
        **count**
        ```コマンドを書き込んだチャンネルの現在のメッセージの総件数を返します。```
        **countall**
        ```犬～恐竜の4チャンネルの現在のメッセージの合計を返します。```
        **addssl <URL>**
        ```SSL Checkerのデータベースに新しい監視URLを登録します。```
        [SSL Checker](https://ssl-checker.vercel.app) ｜ [SSLC database](https://docs.google.com/spreadsheets/d/1c25pvMyjQ89OBCvB9whCQQLM_BPXKyY7umsj5wmpP2k/edit?usp=sharing)"
        **card**
        ```イエローカードやレッドカードの集計結果のベスト5を返します。```
        **cardall**
        ```イエローカードやレッドカードのすべての集計結果を返します。```
        """

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Help(bot))