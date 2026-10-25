import sqlite3

import discord
from discord import app_commands
from discord.ext import commands

from libs.utils import now_jst
from settings import GUILD_ID

DB_PATH = "/data/takohachi.db"
BONUS_VALUE = 3000
RANK_EMOJIS = [":one:", ":two:", ":three:", ":four:", ":five:"]

# --- DB操作 ---
# テーブル: currency(user_id text, user_name text, bonus text, money int)
# 残高の増減は「読んでから書く」のではなく1つのUPDATE文で行い、
# 同時に実行されても二重払い・残高のマイナスが起きないようにする。


def get_money(conn: sqlite3.Connection, user_id: str) -> int | None:
    """所持金を返す。未登録ならNone。"""
    row = conn.execute("select money from currency where user_id = ?", (user_id,)).fetchone()
    return None if row is None else row[0]


def claim_bonus(conn: sqlite3.Connection, user_id: str, user_name: str) -> int | None:
    """ボーナスを受け取り、受け取り後の所持金を返す。受け取り済みならNone。"""
    with conn:
        cur = conn.execute(
            "update currency set money = money + ?, bonus = '1' where user_id = ? and bonus != '1'",
            (BONUS_VALUE, user_id),
        )
        if cur.rowcount:
            return get_money(conn, user_id)
        if get_money(conn, user_id) is not None:
            return None
        conn.execute(
            "insert into currency (user_id, user_name, bonus, money) values (?, ?, '1', ?)",
            (user_id, user_name, BONUS_VALUE),
        )
        return BONUS_VALUE


def transfer(
    conn: sqlite3.Connection, sender_id: str, receiver_id: str, receiver_name: str, amount: int
) -> bool:
    """sender から receiver へ amount を送金する。所持金が足りなければ何もせずFalse。"""
    with conn:
        cur = conn.execute(
            "update currency set money = money - ? where user_id = ? and money >= ?",
            (amount, sender_id, amount),
        )
        if not cur.rowcount:
            return False
        cur = conn.execute(
            "update currency set money = money + ? where user_id = ?", (amount, receiver_id)
        )
        if not cur.rowcount:
            # 未登録の相手は、ボーナス未受け取り(bonus='0')として登録する
            conn.execute(
                "insert into currency (user_id, user_name, bonus, money) values (?, ?, '0', ?)",
                (receiver_id, receiver_name, amount),
            )
        return True


def set_money(conn: sqlite3.Connection, user_id: str, user_name: str, bonus: str, amount: int):
    with conn:
        cur = conn.execute(
            "update currency set bonus = ?, money = ? where user_id = ?", (bonus, amount, user_id)
        )
        if not cur.rowcount:
            conn.execute(
                "insert into currency (user_id, user_name, bonus, money) values (?, ?, ?, ?)",
                (user_id, user_name, bonus, amount),
            )


def top_users(conn: sqlite3.Connection, limit: int = 5) -> list[tuple[str, int]]:
    return conn.execute(
        "select user_id, money from currency order by money desc limit ?", (limit,)
    ).fetchall()


# --- コマンド ---


def _embed(description: str, color: discord.Color | None = None, **kwargs) -> discord.Embed:
    return discord.Embed(
        description=description, color=color or discord.Color.dark_green(), **kwargs
    )


class Currency(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(DB_PATH)

    @app_commands.command(
        name="getbonus", description="初期ボーナス3,000pisをもらうためのコマンドです。"
    )
    async def bonus(self, interaction: discord.Interaction):
        user = interaction.user
        conn = self._connect()
        try:
            money = claim_bonus(conn, str(user.id), str(user.name))
        finally:
            conn.close()

        if money is None:
            embed = _embed(
                f":warning:{user.mention}はすでにボーナスを獲得しています。"
                "ボーナスは一度しかもらえません。",
                discord.Color.red(),
                timestamp=now_jst(),
            )
        else:
            embed = _embed(
                f":moneybag:{user.mention}はボーナスを獲得し、所持金の合計が {money:,} pisになりました。",
                discord.Color.green(),
                timestamp=now_jst(),
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="wallet", description="自分、もしくはサーバー内のユーザーの所持金を返します。"
    )
    @app_commands.describe(
        user="ユーザーを指定してください。入力しない場合は自分の所持金を返します。"
    )
    async def wallet(self, interaction: discord.Interaction, user: discord.Member | None = None):
        user = user or interaction.user
        conn = self._connect()
        try:
            money = get_money(conn, str(user.id)) or 0
        finally:
            conn.close()
        await interaction.response.send_message(
            embed=_embed(f"{user.mention} の所持金は {money:,} pisです。")
        )

    @app_commands.command(name="pay", description="ユーザーに送金します。")
    @app_commands.describe(
        amount="送金する金額を入力してください。", give_user="送金する相手を指定してください。"
    )
    async def pay(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, None],
        give_user: discord.Member,
    ):
        sender = interaction.user
        if sender.id == give_user.id:
            await interaction.response.send_message(
                embed=_embed(":warning:自分に送金することはできません。")
            )
            return

        conn = self._connect()
        try:
            ok = transfer(conn, str(sender.id), str(give_user.id), str(give_user), amount)
            sender_money = get_money(conn, str(sender.id)) or 0
        finally:
            conn.close()

        if ok:
            message = (
                f"{sender.mention} から {give_user.mention} へ {amount:,} pis を送金しました。"
            )
        else:
            message = (
                f"所持金が足りません。\n{sender.mention} の所持金は {sender_money:,} pisです。"
            )
        await interaction.response.send_message(embed=_embed(message))

    @app_commands.command(name="rich", description="お金持ちランキングを表示します。")
    async def rich(self, interaction: discord.Interaction):
        conn = self._connect()
        try:
            users = top_users(conn, len(RANK_EMOJIS))
        finally:
            conn.close()

        if users:
            description = "\n".join(
                f"{emoji} <@{user_id}> {money:,} pis"
                for emoji, (user_id, money) in zip(RANK_EMOJIS, users)
            )
        else:
            description = "⚠ 現在、pisを所持しているユーザーはいません。"
        await interaction.response.send_message(
            embed=_embed(description, title="おかねもちらんきんぐ")
        )

    # --- ここからは管理者のみのコマンド ---
    # default_permissions は「既定で誰に見せるか」の設定で、サーバー側の設定で変えられるため、
    # 実行時にも has_permissions で管理者かどうかを確認する。

    @app_commands.command(
        name="resetcurrency",
        description="[admin]currencyテーブルのすべてのレコードを削除します。",
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    async def resetcurrency(self, interaction: discord.Interaction):
        conn = self._connect()
        try:
            with conn:
                conn.execute("delete from currency")
        finally:
            conn.close()
        await interaction.response.send_message(
            embed=_embed("データベースのテーブル currency のデータをすべて削除しました。")
        )

    @app_commands.command(
        name="givebonus", description="[admin]指定したユーザーにボーナスを与えます。"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(bonus_give_user="Bonusを与えるユーザーを指定。")
    async def givebonus(self, interaction: discord.Interaction, bonus_give_user: discord.Member):
        user_id = str(bonus_give_user.id)
        conn = self._connect()
        try:
            registered = get_money(conn, user_id) is not None
            if not registered:
                set_money(conn, user_id, str(bonus_give_user), "1", BONUS_VALUE)
        finally:
            conn.close()

        if registered:
            message = f"{bonus_give_user.mention} はすでにボーナスを受け取っています。"
        else:
            message = f"{bonus_give_user.mention} に{BONUS_VALUE:,} pis ボーナスを配布しました。"
        await interaction.response.send_message(embed=_embed(message))

    @app_commands.command(
        name="setmoney", description="[admin]指定したユーザーのmoneyを変更します。"
    )
    @app_commands.default_permissions(administrator=True)
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        amount="セットする金額を指定。",
        bonus="ボーナスフラグを1 or 0で選択",
        set_user="セットするユーザーを指定",
    )
    @app_commands.choices(
        bonus=[app_commands.Choice(name="0", value="0"), app_commands.Choice(name="1", value="1")]
    )
    async def setmoney(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 0, None],
        bonus: str,
        set_user: discord.Member,
    ):
        conn = self._connect()
        try:
            set_money(conn, str(set_user.id), str(set_user), bonus, amount)
        finally:
            conn.close()
        await interaction.response.send_message(
            embed=_embed(
                f"{set_user.mention} の所持金を{amount:,} pisに更新しました。bonus_flagは{bonus}です。"
            )
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(Currency(bot), guilds=[discord.Object(id=GUILD_ID)])
