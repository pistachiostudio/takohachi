import asyncio
import sqlite3

import discord
from discord.ext import commands

from libs.shop import Auth, get_data, get_skins

"""
Thanks! https://github.com/DarkPotatoKing/valostore-py
"""


class Store(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 現在のshop offerを返すコマンド。登録していないとだめですよ！
    @commands.command(aliases=["store"])
    async def shop(self, ctx):
        # ちょっと処理に時間がかかるので入力中のギミックを入れる
        async with ctx.typing():
            # dbから必要な値を取ってくる部分
            command_sender_id: str = str(ctx.author.id)  # command送信者のdiscord_id
            tuple_sender: tuple = (command_sender_id,)  # tupleに変換
            DB_DIRECTORY: str = "db/vl_store.db"  # dbのディレクトリ

            # discord_idを検索しレコードを引っ張ってくる
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = "select * from data where d_id = ?"
            c.execute(query, tuple_sender)
            register_info = c.fetchall()

            # dbへの登録があるなしの分岐。ある場合は処理をすすめる
            if len(register_info) != 0:
                # 登録情報に誤りがあり、情報が取れなかった場合の例外処理
                try:
                    # ここがriot_id, riot_pass, regionを入力する部分
                    username = register_info[0][1]  # put your riot id
                    password = register_info[0][2]  # put your riot password
                    region = register_info[0][3]  # put your region

                    auth = Auth({"username": username, "password": password})
                    user_id, headers, _ = auth.authenticate()

                    skins_data, bundles_data, weapons_data, offers_data = get_data(
                        user_id, headers, region
                    )

                    # bundle = get_bundles(skins_data, bundles_data, weapons_data)
                    skin_list = get_skins(skins_data, weapons_data, offers_data)
                    # nm_skin_list = get_night_market(skins_data, weapons_data)
                    # これnight marketがないときにエラーになる KeyError: 'BonusStore'
                    offers = f"{skin_list[0]}\n{skin_list[1]}\n{skin_list[2]}\n{skin_list[3]}"

                    embed = discord.Embed()
                    embed.color = discord.Color.red()
                    embed.description = offers
                    await ctx.reply(embed=embed)
                    return

                except KeyError:
                    embed = discord.Embed()
                    embed.color = discord.Color.red()
                    embed.description = "<:p01_pepebrim:951023068275421235>:warning: 情報を取得できません。。\n\n\
                        <@813757574058213376>にDMで `!!register`と送信して再度登録してください。"
                    await ctx.reply(embed=embed)

            # dbに登録がない場合は登録無しのコメント送信でreturn
            else:
                embed = discord.Embed()
                embed.description = "<:p01_pepebrim:951023068275421235>:warning: データベースに登録がありません。\n\n\
                    <@813757574058213376>にDMで `!!register`と送信して登録してください。"
                await ctx.reply(embed=embed)
                return

            await asyncio.sleep(1)

    # データ登録部分のコマンド。BotへのDMのみで反応する
    @commands.command()
    @commands.dm_only()
    async def register(self, ctx):
        channel = ctx.channel
        takohachi_id = "813757574058213376"

        embed = discord.Embed()
        embed.description = "<:p01_pepebrim:951023068275421235>:warning: このコマンドはあなたの`Riot ID`と\
            `Riot Password`と`Discord ID`をデータベースに保存します。\n\nデータベースは暗号化され、安全に管理されていますが、\
                万が一流出などの事故が起きても一切の責任を負いません。"
        await ctx.reply(embed=embed)

        embed = discord.Embed()
        embed.description = "<:p01_pepechamber:951023019017527336> \
            上記に同意する場合のみ、まずは `Riot ID` を入力してください。"
        await ctx.send(embed=embed)

        try:

            def check(m):
                return m.channel == channel and m.author.id != takohachi_id

            riot_id = await self.bot.wait_for("message", check=check, timeout=120)
            riot_id = riot_id.content

        # asyncio.TimeoutError が発生したらここに飛ぶ
        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.description = "<:p01_pepebrim:951023068275421235>:warning: タイムアウトしました。\n\
                再度 `!!register` コマンドからやり直してください。"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed()
        embed.description = "<:p01_pepeyoru:951023518068387880> 次に `Riot Password` を入力してください。"
        await ctx.send(embed=embed)

        try:

            def check(m):
                return m.channel == channel and m.author.id != takohachi_id

            riot_pass = await self.bot.wait_for("message", check=check, timeout=120)
            riot_pass = riot_pass.content

        # asyncio.TimeoutError が発生したらここに飛ぶ
        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.description = "<:p01_pepebrim:951023068275421235>:warning: タイムアウトしました。\n\
                再度 `!!register` コマンドからやり直してください。"
            await ctx.send(embed=embed)
            return

        embed = discord.Embed()
        embed.description = "<:p01_pepejett:977101860068524062> 最後に `Region` を入力してください。\n\
            日本の人はみんな `ap` でOKです。"
        await ctx.send(embed=embed)

        try:

            def check(m):
                return m.channel == channel and m.author.id != takohachi_id

            region = await self.bot.wait_for("message", check=check, timeout=120)
            region = region.content

            # ここからDBに登録します
            DB_DIRECTORY = "db/vl_store.db"

            command_sender_id: str = str(ctx.author.id)  # コマンド送信者のdiscord_id
            tuple_command_sender_id: tuple = (command_sender_id,)  # tupleに変換

            # d_idカラムからdiscord_idを探す
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query: str = "select * from data where d_id = ? limit 1"
            c.execute(query, tuple_command_sender_id)
            istrue = c.fetchall()

            # d_idカラムにdiscord_idがない場合dbに新規登録する
            if len(istrue) == 0:
                sql = "insert into data (d_id, r_id, r_ps, region) values(?,?,?,?)"
                data = (command_sender_id, riot_id, riot_pass, region)
                c.execute(sql, data)
                db.commit()
                db.close()

                # 登録したよメッセージを送信
                embed = discord.Embed()
                embed.description = "<:p01_pepebrim:951023068275421235>:ballot_box_with_check: \
                    登録が完了しました。\n念のため今入力したIDとPassは削除してね。\n茂林塾チャンネルで `!!shop` \
                    もしくは `!!store` コマンドを打ってみよう！(ここでも反応するよ)"
                await ctx.send(embed=embed)
                return

            # d_idがある場合は上書きする
            else:
                tupled: tuple = (riot_id, riot_pass, region, command_sender_id)
                query: str = "update data set r_id=?, r_ps=?, region=? where d_id=?"
                c.execute(query, tupled)
                db.commit()
                db.close()

                # 登録情報を更新したメッセージを送信
                embed = discord.Embed()
                embed.description = "<:p01_pepebrim:951023068275421235>:ballot_box_with_check: 登録情報を更新しました。\n\
                        念のため今入力したIDとPassは削除してください。"
                await ctx.reply(embed=embed)
                return

        # asyncio.TimeoutError が発生したらここに飛ぶ
        except asyncio.TimeoutError:
            embed = discord.Embed()
            embed.description = "<:p01_pepebrim:951023068275421235>:warning: タイムアウトしました。\n\
                再度 `!!register` コマンドからやり直してください。"
            await ctx.send(embed=embed)
            return

    # データベースの登録情報を削除するコマンド
    @commands.command()
    async def unregister(self, ctx):
        DB_DIRECTORY = "db/vl_store.db"
        command_sender_id: str = str(ctx.author.id)  # コマンド送信者のdiscord_id
        tuple_command_sender_id: tuple = (command_sender_id,)  # tupleに変換

        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query: str = "delete from data where d_id = ?"
        c.execute(query, tuple_command_sender_id)
        db.commit()
        db.close()

        embed = discord.Embed()
        embed.description = ":ballot_box_with_check: 登録情報を削除しました。"
        await ctx.reply(embed=embed)
        return


async def setup(bot: commands.Bot):
    await bot.add_cog(Store(bot))
