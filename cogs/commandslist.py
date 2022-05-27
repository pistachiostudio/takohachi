from discord.ext import commands
import discord
from datetime import datetime, timedelta, timezone


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
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

**!!mt**
```まりもたいむ！```
**!!whatToday**
```今日はなんの日？```
**!!apexrank <A> <B>**
```APEXのランクポイントを表示します。
A = origin or psn or xbl
B = YourID```
**!!sp <SEARCH WORDS>**
```Spotifyの曲情報をゲットします。```
**!!spartist <ARTIST WORDS>**
```Spotifyのアーティスト情報をゲットします。```
**!!count**
```コマンドを書き込んだチャンネルの現在のメッセージの総件数を返します。```
**!!countall**
```犬～恐竜の4チャンネルの現在のメッセージの合計を返します。```
**!!card**
```イエローカードやレッドカードの集計結果のベスト5を返します。```
**!!cardall**
```イエローカードやレッドカードのすべての集計結果を返します。```
**!!addssl <URL>**
```SSL Checkerのデータベースに新しい監視URLを登録します。```
**!!d**
```Valorantのマップをランダムで返します。diceのdです。```
**!!b**
```自分のニックネームの頭に🛀をつけます。もう一度同じコマンドで🛀をはずします。bathのbです。```
"""

        await ctx.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Help(bot))
