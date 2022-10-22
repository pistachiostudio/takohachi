import os
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
from discord.ext import commands

DB_DIRECTORY = os.environ["DB_DIRECTORY"]
BONUS_VALUE = 3000
OWENER_USER_ID = '538992968254619649' #一部の管理者専用のコマンドで使用

class Currency(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        # botのリアクションは無視する
        if payload.member.bot:
            return

# リアクションで初期費用のボーナスBONUS_VALUE pisを与える
# ここでは重複配布を防ぐためbonusカラムの0 or 1で配布済かどうかを判定します。

        # リアクションを許可するテキストチャットのID
        true_text_id = str('943501656283291662')
        # リアクションをする絵文字
        true_emoji = '<:p03_koya_kids:745597071033368666>'

        msg_id = str(payload.message_id)
        react_emoji = str(payload.emoji)

        #特定のチャットへ特定のリアクションでのみ発火
        if true_text_id == msg_id and true_emoji == react_emoji:

            guild = self.bot.get_guild(payload.guild_id)
            member = guild.get_member(payload.user_id)
            channel = self.bot.get_channel(payload.channel_id)
            msg = await channel.fetch_message(payload.message_id)
            #リアクションした人のID
            react_user_id = str(payload.user_id)
            tuple_id = (react_user_id,)
            #リアクションした人のuser name
            react_user_name = str(payload.member)

            # user_idカラムからuser_idを探す
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from currency where user_id = ? limit 1'
            c.execute(query,tuple_id)
            istrue = c.fetchall()

            # user_idカラムにuser_idがない場合dbに新規登録はbonus 1でBONUS_VALUEpisをもらい新規登録
            if len(istrue) == 0:
                sql = 'insert into currency (user_id,user_name,bonus,money) values(?,?,?,?)'
                data = (react_user_id, react_user_name, '1', BONUS_VALUE)
                c.execute(sql, data)
                db.commit()

                #ボーナス獲得メッセージを5秒間表示
                embed = discord.Embed()
                JST = timezone(timedelta(hours=+9), "JST")
                embed.timestamp = datetime.now(JST)
                embed.color = discord.Color.green()
                embed.description = f":moneybag:<@{react_user_id}>はボーナスを獲得しました。"
                await channel.send(embed=embed, delete_after = 5.0)

            else:
                # user_idがある場合はbonusカラムをチェックする
                query = 'select bonus from currency where user_id = ?'
                c.execute(query, tuple_id)
                bonus_flag = c.fetchall()
                bonus_flag = bonus_flag[0][0]

                # bonusが1の場合はすでに獲得済みのエラーメッセージを5秒間
                if bonus_flag == '1':
                    embed = discord.Embed()
                    JST = timezone(timedelta(hours=+9), "JST")
                    embed.timestamp = datetime.now(JST)
                    embed.color = discord.Color.red()
                    embed.description = f":warning:<@{react_user_id}>はすでにボーナスを獲得しています。ボーナスは一度しかもらえません。"
                    await channel.send(embed=embed, delete_after = 5.0)
                    return

                # bonusが0の場合はmoneyの値にBONUS_VALUEを足して更新する
                else:
                    query = 'select money from currency where user_id = ?'
                    c.execute(query, tuple_id)
                    user_money = c.fetchall()
                    user_money = user_money[0][0]
                    update_user_money = user_money + BONUS_VALUE
                    tupled = (update_user_money, react_user_id)

                    # user_idのmoneyをupdate_user_moneyに更新する
                    sql = 'update currency set money = ? where user_id = ?'
                    c.execute(sql, tupled)
                    db.commit()

                    # bonusをつかったので0から1に更新する
                    sql = 'update currency set bonus = "1" where user_id = ?'
                    c.execute(sql, tuple_id)
                    db.commit()

                    #ボーナス獲得メッセージを5秒間表示
                    update_user_money_t = '{:,}'.format(update_user_money)
                    embed = discord.Embed()
                    JST = timezone(timedelta(hours=+9), "JST")
                    embed.timestamp = datetime.now(JST)
                    embed.color = discord.Color.green()
                    embed.description = f":moneybag:<@{react_user_id}>はボーナスを獲得し、所持金の合計が {update_user_money_t} PISになりました。"
                    await channel.send(embed=embed, delete_after = 5.0)

        else:
            return


# !!wallet !!wallet <mention> コマンド
# ここでは自分、もしくはサーバー内のユーザーの所持金を返します。

    @commands.command()
    async def wallet(self, ctx,  *, user = 'default'):

        #引数がない場合はコマンド送信者の情報をレスポンス
        if user == 'default':
            cmd_user_id = str(ctx.author.id)
            tuple_user_id = (cmd_user_id,)
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select money from currency where user_id = ?'
            c.execute(query, tuple_user_id)
            cmd_user_money = c.fetchall()
            cmd_user_money = cmd_user_money[0][0]
            cmd_user_money = '{:,}'.format(cmd_user_money)
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = f"<@{cmd_user_id}> の所持金は {cmd_user_money} PISです。"
            await ctx.send(embed=embed)
            return

        #引数がある場合の条件分岐
        else:
            #引数をメンションのユーザー指定にしていない場合はエラーを返す
            is_mention = user.startswith('<@!')
            if is_mention == False:
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f"userをmentionで指定してください"
                await ctx.send(embed=embed)
                return

            #引数がしっかりメンションになっている場合の条件分岐
            else:
                user = user.lstrip('<@!')
                user = user.rstrip('>')
                tuple_user_mention = (user,)
                db = sqlite3.connect(DB_DIRECTORY)
                c = db.cursor()
                query = 'select money from currency where user_id = ?'
                c.execute(query, tuple_user_mention)
                cmd_user_money = c.fetchall()

                # データベースの検索結果がない場合は所持金0を返す
                if len(cmd_user_money) == 0:
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"<@{user}> の所持金は 0 PISです。"
                    await ctx.send(embed=embed)
                    return

                # データベースの検索結果がある場合はそのメンションのuser_idのmoneyを返す。
                else:
                    cmd_user_money = cmd_user_money[0][0]
                    cmd_user_money = '{:,}'.format(cmd_user_money)
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"<@{user}> の所持金は {cmd_user_money} PISです。"
                    await ctx.send(embed=embed)
                    return


# !!pay <amount> <mention> コマンド
# ここではお金を送金する処理です。

    @commands.command()
    async def pay(self, ctx, amount: int, give_user: discord.Member):

        # コマンド送信者のID
        command_sender_id = str(ctx.author.id)
        tuple_command_sender_id = (command_sender_id,)

        # コマンド送信者のお金が足りてるか確認する
        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query = 'select money from currency where user_id = ?'
        c.execute(query, tuple_command_sender_id)
        sender_money = c.fetchall()
        sender_money = sender_money[0][0]
        update_sender_money = int(sender_money) - int(amount)

        # その前に自分自身に送金している場合はエラーを返す。
        if str(command_sender_id) == str(command_sender_id):
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = f":warning:自分に送金することはできません。"
            await ctx.send(embed=embed)
            return

        else:
            #お金が足りない場合はメッセージを返す
            if update_sender_money < 0:
                sender_money_t = '{:,}'.format(sender_money)
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f"所持金が足りません。\n<@{command_sender_id}> の所持金は {sender_money_t} PISです。"
                await ctx.send(embed=embed)
                return

            #お金が足りる場合
            else:
                #dbにgive_userのuser_idが登録されているかを確認する
                give_user_id = str(give_user.id)
                tuple_give_user_id = (give_user_id,)
                db = sqlite3.connect(DB_DIRECTORY)
                c = db.cursor()
                query = 'select money from currency where user_id = ?'
                c.execute(query, tuple_give_user_id)
                give_user_money = c.fetchall()

                # データベースに登録がない場合はbonusを'0'、moneyをamountで新規登録する
                if len(give_user_money) == 0:
                    sql = 'insert into currency (user_id,user_name,bonus,money) values(?,?,?,?)'
                    data = (str(give_user_id), str(give_user), '0', int(amount))
                    c.execute(sql, data)
                    db.commit()

                    #かつコマンド送信者の所持金からamountをマイナスしてアップデート
                    sender_update_tuple = (int(update_sender_money), str(command_sender_id),)
                    sql = 'update currency set money = ? where user_id = ?'
                    c.execute(sql, sender_update_tuple)
                    db.commit()

                    #送金完了のメッセージを送信
                    amount_t = '{:,}'.format(amount)
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"<@{command_sender_id}> から <@{give_user_id}> へ {amount_t} PIS を送金しました。"
                    await ctx.send(embed=embed)
                    return

                # give_userがすでにデータベースに登録がある人の場合
                else:
                    #give_userのmoneyに+amountしてアップデート
                    db = sqlite3.connect(DB_DIRECTORY)
                    c = db.cursor()
                    query = 'select money from currency where user_id = ?'
                    c.execute(query, tuple_give_user_id)
                    give_user_currency = c.fetchall()
                    give_user_currency = give_user_currency[0][0]
                    update_give_user_money = int(give_user_currency) + int(amount)
                    give_user_update_tuple = (int(update_give_user_money), str(give_user_id),)
                    sql = 'update currency set money = ? where user_id = ?'
                    c.execute(sql, give_user_update_tuple)
                    db.commit()

                    #かつコマンド送信者の所持金からamountをマイナスしてアップデート
                    sender_update_tuple = (int(update_sender_money), str(command_sender_id),)
                    sql = 'update currency set money = ? where user_id = ?'
                    c.execute(sql, sender_update_tuple)
                    db.commit()

                    #送金完了のメッセージを送信
                    amount_t = '{:,}'.format(amount)
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"<@{command_sender_id}> から <@{give_user_id}> へ {amount_t} PIS を送金しました。"
                    await ctx.send(embed=embed)
                    return

# !!rich コマンド お金持ちランキング
# ここでは金持ちランキングを表示します。
# 現状はデータベースの登録が5ユーザーに満たない場合はエラーになってしまう。

    @commands.command()
    async def rich(self, ctx):

        # money上位5件を上限に返す。
        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query = 'select * from currency order by money desc limit 15'
        c.execute(query)
        richest_list = c.fetchall()
        rich_text = f'''
                    :one: <@{richest_list[0][0]}> {richest_list[0][3]:,} PIS

                    :two: <@{richest_list[1][0]}> {richest_list[1][3]:,} PIS

                    :three: <@{richest_list[2][0]}> {richest_list[2][3]:,} PIS

                    :four: <@{richest_list[3][0]}> {richest_list[3][3]:,} PIS

                    :five: <@{richest_list[4][0]}> {richest_list[4][3]:,} PIS
                    '''

        embed = discord.Embed()
        embed.color = discord.Color.dark_green()
        embed.description = rich_text
        await ctx.send(embed=embed)
        return


# !!shop
# shopテーブルに登録されている商品の一覧を返します。

    @commands.command()
    async def shop(self, ctx):

        # リストすべてを返す
        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query = 'select * from shop order by price'
        c.execute(query)
        item_list = c.fetchall()
        item_text = f'''
                    商品名: {item_list[0][0]}
                    ```値段: {item_list[0][2]:,} PIS | 残り{item_list[0][3]:,}個
{item_list[0][1]}```
                    商品名: {item_list[1][0]}
                    ```値段: {item_list[1][2]:,} PIS | 残り{item_list[1][3]:,}個
{item_list[1][1]}```
                    商品名: {item_list[2][0]}
                    ```値段: {item_list[2][2]:,} PIS | 残り{item_list[2][3]:,}個
{item_list[2][1]}```
                    '''

        embed = discord.Embed()
        embed.color = discord.Color.dark_green()
        embed.title = 'ピスタチオ商店'
        embed.description = item_text
        await ctx.send(embed=embed)
        return


# !!buy <item_name>
# shopからアイテムを買うことができます

    @commands.command()
    async def buy(self, ctx, buy_item:str = 'default'):

        #引数の指定がない場合はメッセージ
        if buy_item == 'default':
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = ':warning:買いたい商品を指定してください。\n!!buy <商品名> です。商品一覧は!!shopコマンドを使用してください。'
            await ctx.send(embed=embed)
            return

        else:
            # 引数buy_itemがdbのitem_nameと一致するか確認
            tuple_item_name = (buy_item,)
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from shop where item_name = ?'
            c.execute(query, tuple_item_name)
            item_all_record = c.fetchall()

            if len(item_all_record) == 0:
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f":warning:その商品は現在販売されていないようです。!!shopコマンドで販売中の商品を確認してください。"
                await ctx.send(embed=embed)
                return

            # 商品名が問題ない場合は次に進む
            else:
                # コマンド送信者のお金が足りてるか確認する
                command_sender_id = str(ctx.author.id)
                tuple_command_sender_id = (command_sender_id,)

                # コマンド送信者の所持金
                db = sqlite3.connect(DB_DIRECTORY)
                c = db.cursor()
                query = 'select money from currency where user_id = ?'
                c.execute(query, tuple_command_sender_id)
                sender_money = c.fetchall()
                sender_money = sender_money[0][0]

                # 商品の値段
                db = sqlite3.connect(DB_DIRECTORY)
                c = db.cursor()
                query = 'select price from shop where item_name = ?'
                c.execute(query, tuple_item_name)
                item_price = c.fetchall()
                item_price = item_price[0][0]

                # 所持金 - 値段
                update_customer_money = int(sender_money) - int(item_price)

                #お金が足りない場合はメッセージを返す
                if update_customer_money < 0:
                    sender_money_t = '{:,}'.format(sender_money)
                    item_price_t = '{:,}'.format(item_price)
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"所持金が足りません。\n**{buy_item}**は{item_price_t} PISです。\n<@{command_sender_id}> の所持金は {sender_money_t} PISです。"
                    await ctx.send(embed=embed)
                    return

                #お金が足りる場合は購入処理に進む。
                else:
                    #購入者の所持金から商品代金をマイナスして更新する
                    sender_update_tuple = (int(update_customer_money), str(command_sender_id),)
                    sql = 'update currency set money = ? where user_id = ?'
                    c.execute(sql, sender_update_tuple)
                    db.commit()

                    #shopデータベースの残り個数を更新する
                    db = sqlite3.connect(DB_DIRECTORY)
                    c = db.cursor()
                    query = 'select quantity from shop where item_name = ?'
                    c.execute(query, tuple_item_name)
                    item_quantity = c.fetchall()
                    item_quantity = item_quantity[0][0]

                    update_item_quantity = int(item_quantity) - 1
                    tuple_item_quantity = (int(update_item_quantity), str(buy_item),)
                    sql = 'update shop set quantity = ? where item_name = ?'
                    c.execute(sql, tuple_item_quantity)
                    db.commit()

                    #購入完了のメッセージを送信
                    item_price_t = '{:,}'.format(item_price)
                    update_customer_money_t = '{:,}'.format(update_customer_money)
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"<@{command_sender_id}> は {buy_item}({item_price_t} PIS) を購入しました。\n残りの所持金は {update_customer_money_t} PISです。\nご利用ありがとうございます。"
                    await ctx.send(embed=embed)
                    return


    '''
    ////////////////////////////
    ここからは管理者のみのコマンド
    ////////////////////////////
    '''


# !!resetcurrency
# currencyテーブルのすべてのレコードを削除します。

    @commands.command()
    async def resetcurrency(self, ctx):

        #俺だけが使えるコマンド
        command_sender_id = str(ctx.author.id)
        if command_sender_id == OWENER_USER_ID:
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'delete from currency'
            c.execute(query)
            db.commit()
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = f"データベースのテーブル currency のデータをすべて削除しました。"
            await ctx.send(embed=embed)
            return

        else:
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = 'そのコマンドは許可されていません。'
            await ctx.send(embed=embed)
            return


# !!givebonus <@user_mention>
# 管理者がコマンドで与えることもできるようにする

    @commands.command()
    async def givebonus(self, ctx, bonus_give_user: discord.Member):

        #俺だけが使えるコマンド
        command_sender_id = str(ctx.author.id)
        if command_sender_id == OWENER_USER_ID:

            # user_idカラムからuser_idを探す
            give_user_id = str(bonus_give_user.id)
            tuple_give_user_id = (give_user_id,)
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from currency where user_id = ? limit 1'
            c.execute(query,tuple_give_user_id)
            istrue = c.fetchall()

            # user_idカラムにuser_idがない場合（dbに新規登録）はbonus 1でBONUS_VALUE円をもらい新規登録
            if len(istrue) == 0:
                sql = 'insert into currency (user_id,user_name,bonus,money) values(?,?,?,?)'
                data = (str(give_user_id), str(bonus_give_user), '1', BONUS_VALUE)
                c.execute(sql, data)
                db.commit()

                BONUS_VALUE_t = '{:,}'.format(BONUS_VALUE)
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f"<@{give_user_id}> に{BONUS_VALUE_t} PIS ボーナスを配布しました。"
                await ctx.send(embed=embed)
                return

            else:
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f"<@{give_user_id}> はすでにボーナスを受け取っています。"
                await ctx.send(embed=embed)
                return

        else:
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = 'そのコマンドは許可されていません。'
            await ctx.send(embed=embed)
            return


# !!setmoney <amount> <bonus_flag> <@user_mention>se
# 管理者がコマンドで与えることもできるようにする

    @commands.command()
    async def setmoney(self, ctx, amount: int, bonus: str, set_user: discord.Member):

        #俺だけが使えるコマンド
        command_sender_id = str(ctx.author.id)
        if command_sender_id == OWENER_USER_ID:

            #bonusは0か1しかセットできない
            if bonus == '0' or bonus ==  '1':
                # user_idカラムからuser_idを探す
                set_user_id = str(set_user.id)
                tuple_set_user_id = (set_user_id,)
                db = sqlite3.connect(DB_DIRECTORY)
                c = db.cursor()
                query = 'select * from currency where user_id = ? limit 1'
                c.execute(query,tuple_set_user_id)
                istrue = c.fetchall()

                # 新規登録の場合
                if len(istrue) == 0:
                    sql = 'insert into currency (user_id,user_name,bonus,money) values(?,?,?,?)'
                    data = (str(set_user_id), str(set_user), str(bonus), int(amount))
                    c.execute(sql, data)
                    db.commit()

                    amount_t = '{:,}'.format(amount)
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"<@{set_user_id}> に{amount_t} PIS セットしました。bonus_flagは{bonus}です。"
                    await ctx.send(embed=embed)
                    return

                # 新規登録ではない場合も更新する
                else:
                    set_update_tuple = (str(bonus), int(amount), str(set_user_id))
                    sql = 'update currency set bonus = ?, money = ? where user_id = ?'
                    c.execute(sql, set_update_tuple)
                    db.commit()

                    amount_t = '{:,}'.format(amount)
                    embed = discord.Embed()
                    embed.color = discord.Color.dark_green()
                    embed.description = f"<@{set_user_id}> の所持金{amount_t} PISにを更新しました。bonus_flagは{bonus}です。"
                    await ctx.send(embed=embed)
                    return

            else:
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f"bonus_flagは0か1以外設定できません。"
                await ctx.send(embed=embed)
                return

        else:
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = 'そのコマンドは許可されていません。'
            await ctx.send(embed=embed)
            return


def setup(bot):
    bot.add_cog(Currency(bot))
