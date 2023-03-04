import sqlite3
from datetime import datetime, timedelta, timezone

import discord
from discord import app_commands
from discord.ext import commands

DB_DIRECTORY = "/data/takohachi.db"
BONUS_VALUE = 3000

class Currency(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

#/bonus ボーナスをもらうためのコマンド

    @app_commands.command(
        name="getbonus",
        description="初期ボーナス3,000pisをもらうためのコマンドです。"
    )
    async def bonus(
        self,
        interaction: discord.Interaction
    ):

        sender_id = str(interaction.user.id)
        tuple_id = (sender_id,)
        sender_user_name = str(interaction.user.name)
        channel = interaction.channel

        # user_idカラムからuser_idを探す
        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query = 'select * from currency where user_id = ? limit 1'
        c.execute(query,tuple_id)
        istrue = c.fetchall()

        # user_idカラムにuser_idがない場合dbに新規登録はbonus 1でBONUS_VALUEpisをもらい新規登録
        if len(istrue) == 0:
            sql = 'insert into currency (user_id,user_name,bonus,money) values(?,?,?,?)'
            data = (sender_id, sender_user_name, '1', BONUS_VALUE)
            c.execute(sql, data)
            db.commit()

            #ボーナス獲得メッセージを5秒間表示
            embed = discord.Embed()
            JST = timezone(timedelta(hours=+9), "JST")
            embed.timestamp = datetime.now(JST)
            embed.color = discord.Color.green()
            embed.description = f":moneybag:<@{sender_id}>はボーナスを獲得しました。"
            await interaction.response.send_message(embed=embed)

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
                embed.description = f":warning:<@{sender_id}>はすでにボーナスを獲得しています。ボーナスは一度しかもらえません。"
                await interaction.response.send_message(embed=embed)
                return

            # bonusが0の場合はmoneyの値にBONUS_VALUEを足して更新する
            else:
                query = 'select money from currency where user_id = ?'
                c.execute(query, tuple_id)
                user_money = c.fetchall()
                user_money = user_money[0][0]
                update_user_money = user_money + BONUS_VALUE
                tupled = (update_user_money, sender_id)
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
                embed.description = f":moneybag:<@{sender_id}>はボーナスを獲得し、所持金の合計が {update_user_money_t} pisになりました。"
                await interaction.response.send_message(embed=embed)
                return

# /wallet
# ここでは自分、もしくはサーバー内のユーザーの所持金を返します。

    @app_commands.command(
        name="wallet",
        description="自分、もしくはサーバー内のユーザーの所持金を返します。"
    )

    @app_commands.describe(
        user="ユーザーを指定してください。入力しない場合は自分の所持金を返します。"
    )

    async def wallet(
        self,
        interaction: discord.Interaction,
        user: discord.Member = None
    ):

        #userオプションが空欄の場合はコマンド送信者の情報をレスポンス
        if user == None:
            cmd_user_id = str(interaction.user.id)
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
            embed.description = f"<@{cmd_user_id}> の所持金は {cmd_user_money} pisです。"
            await interaction.response.send_message(embed=embed)
            return

        else:
            user = user.id
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
                embed.description = f"<@{user}> の所持金は 0 pisです。"
                await interaction.response.send_message(embed=embed)
                return
            # データベースの検索結果がある場合はそのメンションのuser_idのmoneyを返す。
            else:
                cmd_user_money = cmd_user_money[0][0]
                cmd_user_money = '{:,}'.format(cmd_user_money)
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f"<@{user}> の所持金は {cmd_user_money} pisです。"
                await interaction.response.send_message(embed=embed)
                return

# /pay <amount> <mention>
# お金を送金する処理です。

    @app_commands.command(
        name="pay",
        description="ユーザーに送金します。"
    )

    @app_commands.describe(
        amount="送金する金額を入力してください。",
        give_user="送金する相手を指定してください。"
    )

    async def pay(
        self,
        interaction: discord.Interaction,
        amount: int,
        give_user: discord.Member
    ):

        # コマンド送信者のID
        command_sender_id = str(interaction.user.id)
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
        if str(command_sender_id) == str(give_user.id):
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = f":warning:自分に送金することはできません。"
            await interaction.response.send_message(embed=embed)
            return

        else:
            #お金が足りない場合はメッセージを返す
            if update_sender_money < 0:
                sender_money_t = '{:,}'.format(sender_money)
                embed = discord.Embed()
                embed.color = discord.Color.dark_green()
                embed.description = f"所持金が足りません。\n<@{command_sender_id}> の所持金は {sender_money_t} pisです。"
                await interaction.response.send_message(embed=embed)
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
                    # トランザクションを開始
                    db.execute('BEGIN TRANSACTION')
                    try:

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
                        embed.description = f"<@{command_sender_id}> から <@{give_user_id}> へ {amount_t} pis を送金しました。"
                        await interaction.response.send_message(embed=embed)
                        return
                    except Exception as e:
                        db.rollback()
                        #エラーメッセージを送信
                        amount_t = '{:,}'.format(amount)
                        embed = discord.Embed()
                        embed.color = discord.Color.red()
                        embed.description = "⚠ エラーが発生しました。ロールバックしました。"
                        await interaction.response.send_message(embed=embed)
                        return
                    finally:
                        db.close()

                # give_userがすでにデータベースに登録がある人の場合
                else:
                    # トランザクションを開始
                    db.execute('BEGIN TRANSACTION')
                    try:
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
                        embed.description = f"<@{command_sender_id}> から <@{give_user_id}> へ {amount_t} pis を送金しました。"
                        await interaction.response.send_message(embed=embed)
                        return

                    except Exception as e:
                        db.rollback()
                        #エラーメッセージを送信
                        amount_t = '{:,}'.format(amount)
                        embed = discord.Embed()
                        embed.color = discord.Color.red()
                        embed.description = "⚠ エラーが発生しました。ロールバックしました。"
                        await interaction.response.send_message(embed=embed)

                    finally:
                        db.close()

# /rich
# ここでは金持ちランキングを表示します。
# 現状はデータベースの登録が5ユーザーに満たない場合はエラーになってしまう。

    @app_commands.command(
        name='rich',
        description='お金持ちランキングを表示します。'
    )
    async def rich(
        self,
        interaction: discord.Interaction
    ):

        # データベースのレコード数を取得する。
        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query = 'select count(*) from ' + 'currency'
        c.execute(query)
        record_num = c.fetchall()
        record_len = int(record_num[0][0])

        if record_len == 0:
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.title = 'おかねもちらんきんぐ'
            embed.description = "⚠ 現在、pisを所持しているユーザーはいません。"
            await interaction.response.send_message(embed=embed)

        elif record_len == 1:
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from currency order by money desc limit 1'
            c.execute(query)
            richest_list = c.fetchall()
            rich_text = f':one: <@{richest_list[0][0]}> {richest_list[0][3]:,} pis'
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.title = 'おかねもちらんきんぐ'
            embed.description = rich_text
            await interaction.response.send_message(embed=embed)
            return

        elif record_len == 2:
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from currency order by money desc limit 2'
            c.execute(query)
            richest_list = c.fetchall()
            rich_text = f':one: <@{richest_list[0][0]}> {richest_list[0][3]:,} pis\n:two: <@{richest_list[1][0]}> {richest_list[1][3]:,} pis'
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.title = 'おかねもちらんきんぐ'
            embed.description = rich_text
            await interaction.response.send_message(embed=embed)
            return

        elif record_len == 3:
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from currency order by money desc limit 3'
            c.execute(query)
            richest_list = c.fetchall()
            rich_text = f':one: <@{richest_list[0][0]}> {richest_list[0][3]:,} pis\n:two: <@{richest_list[1][0]}> {richest_list[1][3]:,} pis\n:three: <@{richest_list[2][0]}> {richest_list[2][3]:,} pis'
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.title = 'おかねもちらんきんぐ'
            embed.description = rich_text
            await interaction.response.send_message(embed=embed)
            return

        elif record_len == 4:
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from currency order by money desc limit 4'
            c.execute(query)
            richest_list = c.fetchall()
            rich_text = f':one: <@{richest_list[0][0]}> {richest_list[0][3]:,} pis\n:two: <@{richest_list[1][0]}> {richest_list[1][3]:,} pis\n:three: <@{richest_list[2][0]}> {richest_list[2][3]:,} pis\n:four: <@{richest_list[3][0]}> {richest_list[3][3]:,} pis'
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.title = 'おかねもちらんきんぐ'
            embed.description = rich_text
            await interaction.response.send_message(embed=embed)
            return

        elif record_len >= 5:
            db = sqlite3.connect(DB_DIRECTORY)
            c = db.cursor()
            query = 'select * from currency order by money desc limit 5'
            c.execute(query)
            richest_list = c.fetchall()
            rich_text = f':one: <@{richest_list[0][0]}> {richest_list[0][3]:,} pis\n:two: <@{richest_list[1][0]}> {richest_list[1][3]:,} pis\n:three: <@{richest_list[2][0]}> {richest_list[2][3]:,} pis\n:four: <@{richest_list[3][0]}> {richest_list[3][3]:,} pis\n:five: <@{richest_list[4][0]}> {richest_list[4][3]:,} pis'
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.title = 'おかねもちらんきんぐ'
            embed.description = rich_text
            await interaction.response.send_message(embed=embed)
            return

        else:
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = '⚠ データベースの読み込みに失敗しました。'
            await interaction.response.send_message(embed=embed)
            return


# /shop
# shopテーブルに登録されている商品の一覧を返します。
# どのようにするか検討中のため一旦コメントアウト
    """
    @app_commands.command(
        name='shop',
        description='お店の商品一覧を表示します。'
    )
    async def shop(
        self,
        interaction: discord.Interaction
    ):

        # リストすべてを返す
        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query = 'select * from shop order by price'
        c.execute(query)
        item_list = c.fetchall()
        item_text = f'''
                    商品名: {item_list[0][0]}
                    ```値段: {item_list[0][2]:,} pis | 残り{item_list[0][3]:,}個
{item_list[0][1]}```
                    商品名: {item_list[1][0]}
                    ```値段: {item_list[1][2]:,} pis | 残り{item_list[1][3]:,}個
{item_list[1][1]}```
                    商品名: {item_list[2][0]}
                    ```値段: {item_list[2][2]:,} pis | 残り{item_list[2][3]:,}個
{item_list[2][1]}```
                    '''

        embed = discord.Embed()
        embed.color = discord.Color.dark_green()
        embed.title = 'ピスタチオ商店'
        embed.description = item_text
        await interaction.response.send_message(embed=embed)
        return


# !!buy <item_name>
# shopからアイテムを買うことができます

    @app_commands.command(
        name='buy',
        description='商品を購入します。'
    )

    async def buy(self,
    interaction: discord.Interaction,
    buy_item: str
    ):

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
                await interaction.response.send_message(embed=embed)
                return

            # 商品名が問題ない場合は次に進む
            else:
                # コマンド送信者のお金が足りてるか確認する
                command_sender_id = str(interaction.user.id)
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
                    embed.description = f"所持金が足りません。\n**{buy_item}**は{item_price_t} pisです。\n<@{command_sender_id}> の所持金は {sender_money_t} pisです。"
                    await interaction.response.send_message(embed=embed)
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
                    embed.description = f"<@{command_sender_id}> は {buy_item}({item_price_t} pis) を購入しました。\n残りの所持金は {update_customer_money_t} pisです。\nご利用ありがとうございます。"
                    await interaction.response.send_message(embed=embed)
                    return
    """

    '''
    ////////////////////////////
    ここからは管理者のみのコマンド
    Productionでは
    @app_commands.default_permissions(administrator=True)
    をつけて管理者(@carataker)のみが表示されつかえるようなコマンドにする予定。
    変数のOWENER_USER_IDも最終削除する。
    ////////////////////////////
    '''

# /resetcurrency
# currencyテーブルのすべてのレコードを削除します。

    @app_commands.command(
        name="resetcurrency",
        description="[admin]currencyテーブルのすべてのレコードを削除します。"
    )
    @app_commands.default_permissions(administrator=True)

    async def resetcurrency(
        self,
        interaction: discord.Interaction
    ):

        db = sqlite3.connect(DB_DIRECTORY)
        c = db.cursor()
        query = 'delete from currency'
        c.execute(query)
        db.commit()
        embed = discord.Embed()
        embed.color = discord.Color.dark_green()
        embed.description = f"データベースのテーブル currency のデータをすべて削除しました。"
        await interaction.response.send_message(embed=embed)
        return


# /givebonus <@user_mention>
# 管理者がコマンドで与えることもできるようにする

    @app_commands.command(
        name="givebonus",
        description="[admin]指定したユーザーにボーナスを与えます。"
    )

    @app_commands.default_permissions(administrator=True)

    @app_commands.describe(
        bonus_give_user="Bonusを与えるユーザーを指定。"
    )

    async def givebonus(
        self,
        interaction: discord.Interaction,
        bonus_give_user: discord.Member
    ):

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
            embed.description = f"<@{give_user_id}> に{BONUS_VALUE_t} pis ボーナスを配布しました。"
            await interaction.response.send_message(embed=embed)
            return

        else:
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = f"<@{give_user_id}> はすでにボーナスを受け取っています。"
            await interaction.response.send_message(embed=embed)
            return

# /setmoney <amount> <bonus_flag> <@user_mention>
# 管理者がコマンドで与えることもできるようにする

    @app_commands.command(
        name="setmoney",
        description="[admin]指定したユーザーのmoneyを変更します。"
    )

    @app_commands.default_permissions(administrator=True)

    @app_commands.describe(
        amount="セットする金額を指定。",
        bonus="ボーナスフラグを1 or 0で選択",
        set_user="セットするユーザーを指定"
    )

    @app_commands.choices(
        bonus=[
            discord.app_commands.Choice(name="0",value="0"),
            discord.app_commands.Choice(name="1",value="1")
        ]
    )

    async def setmoney(
        self,
        interaction: discord.Interaction,
        amount: int,
        bonus: str,
        set_user: discord.Member
    ):

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
                embed.description = f"<@{set_user_id}> に{amount_t} pis セットしました。bonus_flagは{bonus}です。"
                await interaction.response.send_message(embed=embed)
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
                embed.description = f"<@{set_user_id}> の所持金{amount_t} pisにを更新しました。bonus_flagは{bonus}です。"
                await interaction.response.send_message(embed=embed)
                return

        else:
            embed = discord.Embed()
            embed.color = discord.Color.dark_green()
            embed.description = f"bonus_flagは0か1以外設定できません。"
            await interaction.response.send_message(embed=embed)
            return

async def setup(bot: commands.Bot):
    await bot.add_cog(
        Currency(bot),
        guilds = [discord.Object(id=731366036649279518)]
    )
