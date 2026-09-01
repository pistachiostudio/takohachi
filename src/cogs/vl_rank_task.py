import asyncio
import logging
import os
import random
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
import httpx
from discord.ext import commands, tasks

from cogs import valorant_api

# fetch()の戻り値のうち、前日の基準(yesterday_season)がまだ記録されていない
# ため差分計算ができなかったことを示すセンチネル。
# デプロイ直後やプレイヤー新規追加時に発生し、この状態は「誰もプレイしていない」
# とは異なるため、「誰もプレイしていない」メッセージの判定から除外する。
NO_BASELINE = object()

# fetch()の戻り値のうち、前日の基準はあったが1試合もプレイしていなかったことを
# 示すセンチネル。API取得失敗時のNoneとは異なり、こちらは「誰もプレイしていない」
# 判定に使ってよい(=状況が明確に分かっている)。
NO_PLAY = object()

# 前日誰もプレイしていなかった日に、ランダムで1つ選んで投稿するメッセージ
NO_PLAY_MESSAGES: list[str] = [
    "🦎 しーん...\n\n今日はVALORANT、誰もプレイしてなかったみたいです。\nみんなどこ行っちゃったのかな...\n\nまた明日待ってますね。",
    "🐹💨 シーン...\n\n今日も誰も来ないのかな。\nボッチ、一人で待ってますよ...\n\n(泣)",
    "💔 今日は誰もプレイしてなかったみたい...寂しいな。",
    "🌙 昨日の夜、誰もVALORANTを起動しなかったようです。\nみんな元気にしてるかな...?",
    "📭 今日の戦績、空っぽでした。\nまた遊んでくれるの待ってますね...",
    "🍃 静かな一日でした。\n誰もランクを回さなかったみたい。\nたまにはそんな日もありますよね。",
    "👻 …だれもいない。\nVALORANT部屋、閑古鳥が鳴いています。",
    "🎮💤 コントローラーがお昼寝していました。\n昨日は誰も対戦しなかったみたいです。",
    "🕯️ 今日は戦績報告、お休みです。\n誰もプレイしなかったので…また今度。",
    "🐾 誰かの足跡を探しましたが、見つかりませんでした。\n今日はみんなお休みだったみたいですね。",
]

# ランクに合わせてバッジを表示するための辞書
rank_badge_dict: dict[str, str] = {
    "Unrated": "<:Unranked_Rank:1123928409676972092>",
    "Iron 1": "<:Iron_1_Rank:1123927841680150620>",
    "Iron 2": "<:Iron_2_Rank:1123927843613720657>",
    "Iron 3": "<:Iron_3_Rank:1123927839146774578>",
    "Bronze 1": "<:Bronze_1_Rank:1123927742027677716>",
    "Bronze 2": "<:Bronze_2_Rank:1123927743537623133>",
    "Bronze 3": "<:Bronze_3_Rank:1123927746729492513>",
    "Silver 1": "<:Silver_1_Rank:1123927897284018226>",
    "Silver 2": "<:Silver_2_Rank:1123927899016286318>",
    "Silver 3": "<:Silver_3_Rank:1123927892540272652>",
    "Gold 1": "<:Gold_1_Rank:1123927794527764563>",
    "Gold 2": "<:Gold_2_Rank:1123927790006308874>",
    "Gold 3": "<:Gold_3_Rank:1123927793210753054>",
    "Platinum 1": "<:Platinum_1_Rank:1123927860395130952>",
    "Platinum 2": "<:Platinum_2_Rank:1123927863930912838>",
    "Platinum 3": "<:Platinum_3_Rank:1123927865600249917>",
    "Diamond 1": "<:Diamond_1_Rank:1123927768363712512>",
    "Diamond 2": "<:Diamond_2_Rank:1123927771584938104>",
    "Diamond 3": "<:Diamond_3_Rank:1123927766853746708>",
    "Ascendant 1": "<:Ascendant_1_Rank:1123927717042204793>",
    "Ascendant 2": "<:Ascendant_2_Rank:1123927719554588703>",
    "Ascendant 3": "<:Ascendant_3_Rank:1123927715540652042>",
    "Immortal 1": "<:Immortal_1_Rank:1123927813209206907>",
    "Immortal 2": "<:Immortal_2_Rank:1123927816673689732>",
    "Immortal 3": "<:Immortal_3_Rank:1123927819228024872>",
    "Radiant": "<:Radiant_Rank:1123927894725496842>",
}

VALORANT_TOKEN = os.environ["VALORANT_TOKEN"]


class RankTasks(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=600.0)
    async def printer(self):
        channel = self.bot.get_channel(int("924924594706583562"))

        # タイムゾーンの生成
        JST = timezone(timedelta(hours=+9), "JST")
        now = datetime.now(JST)

        now_hour = now.hour
        now_minute = now.minute

        if now_hour == 7 and 0 <= now_minute <= 9:
            try:
                await self._post_daily_ranking(channel)
            except Exception:
                # discord.HTTPExceptionなどtasks.loopの自動リトライ対象外の例外が
                # ここで発生するとループ自体が停止し、二度と朝の投稿が行われなく
                # なるため、ここで捕まえて次回ループを継続させる。
                logging.exception("Failed to post daily valorant ranking")

    async def _post_daily_ranking(self, channel):
        # 投稿の度にシーズン(Act)情報を最新化する
        await valorant_api.update_current_season()

        db_path = "/data/takohachi.db"

        # データベースに接続とカーソルの取得
        conn = sqlite3.connect(db_path)
        try:
            cur = conn.cursor()

            # yesterday_seasonカラムが無ければ追加する(マイグレーション)
            cur.execute("PRAGMA table_info(val_puuids)")
            columns = {row[1] for row in cur.fetchall()}
            if "yesterday_season" not in columns:
                cur.execute("ALTER TABLE val_puuids ADD COLUMN yesterday_season TEXT")
                conn.commit()

            # レコードを全て取得し、yesterday_eloで降順にソート
            cur.execute(
                "SELECT puuid, region, name, tag, yesterday_elo, yesterday_win, "
                "yesterday_lose, d_uid, yesterday_season FROM val_puuids "
                "ORDER BY yesterday_elo DESC"
            )
            rows = cur.fetchall()

            async def fetch(row):
                # region, name, tagはDB保存値だが、API呼び出しで最新のapi_region/
                # api_name/api_tagを取得し直すためここでは使わない
                (
                    puuid,
                    _region,
                    _name,
                    _tag,
                    yesterday_elo,
                    yesterday_win,
                    yesterday_lose,
                    d_uid,
                    yesterday_season,
                ) = row

                headers = {"Authorization": VALORANT_TOKEN}

                # 非同期でキャッシュをパージしてリクエスト。最新のnameとtagを取得する。
                try:
                    account_url = f"https://api.henrikdev.xyz/valorant/v1/by-puuid/account/{puuid}?force=true"
                    async with httpx.AsyncClient() as client:
                        name_tag_response = await client.get(
                            account_url, headers=headers, timeout=60
                        )
                except httpx.HTTPError:
                    # API取得失敗時はNoneを返す。この人の状況は不明なため、
                    # 「誰もプレイしていない」の判定(NO_PLAY)には使わない。
                    return None

                # jsonから必要な値を取得
                account_data = name_tag_response.json()
                api_name: str = account_data["data"]["name"]
                api_tag: str = account_data["data"]["tag"]
                api_region: str = account_data["data"]["region"]

                # mmrのエンドポイントを非同期でリクエスト
                try:
                    url = (
                        f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{api_region}/{puuid}"
                    )
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, headers=headers, timeout=60)
                except httpx.HTTPError:
                    # API取得失敗時はNoneを返す。この人の状況は不明なため、
                    # 「誰もプレイしていない」の判定(NO_PLAY)には使わない。
                    return None

                # jsonから必要な値を取得
                data = response.json()
                currenttierpatched: str = data["data"]["current_data"]["currenttierpatched"]
                ranking_in_tier: str = data["data"]["current_data"]["ranking_in_tier"]
                elo: int = data["data"]["current_data"]["elo"]

                # 新シーズンになって1試合もやってない場合は
                # アクトごとのレスポンス部分はKeyErrorが発生するのでその判定を行う
                try:
                    current_season_data = data["data"]["by_season"][valorant_api.current_season]
                    final_rank_patched: str = current_season_data.get(
                        "final_rank_patched", "Unrated"
                    )
                    number_of_games: int = current_season_data.get("number_of_games", 0)
                    # 正確なwinsを取得するために変更
                    wins: int = len(
                        data["data"]["by_season"][valorant_api.current_season]["act_rank_wins"]
                    )
                    loses: int = number_of_games - wins
                except KeyError:
                    wins = 0
                    loses = 0
                    final_rank_patched = "Unrated"

                def update_db():
                    cur.execute(
                        "UPDATE val_puuids SET region=?, name=?, tag=?, yesterday_elo=?, yesterday_win=?, yesterday_lose=?, yesterday_season=? WHERE puuid=?",  # noqa: E501
                        (
                            api_region,
                            api_name,
                            api_tag,
                            elo,
                            wins,
                            loses,
                            valorant_api.current_season,
                            puuid,
                        ),
                    )
                    conn.commit()

                # yesterday_seasonが未記録(マイグレーション直後や新規追加プレイヤー)の
                # 場合、前日の基準が存在しないため差分計算ができない。
                # DBに現在の値を書き込んで投稿対象からは除外し、翌日以降から
                # 正しい差分が計算できるようにする。
                if yesterday_season is None:
                    update_db()
                    return NO_BASELINE

                # シーズンが切り替わっていたら、前日のelo/勝敗は前シーズンのものなので
                # 差分計算に使わず基準なし扱いにする(そうしないと新シーズン開始直後に
                # 大きくマイナス、あるいは大きくプラスの戦績になってしまう)
                season_changed = yesterday_season != valorant_api.current_season
                if season_changed:
                    yesterday_win = 0
                    yesterday_lose = 0

                # ランクがUnratedの場合はELOなども一旦0にする。
                # Unratedではなくランクがついている場合は通常の処理。
                if final_rank_patched == "Unrated":
                    current_rank_info = "Unrated"
                    currenttierpatched = "Unrated"
                    todays_elo = 0
                    elo = 0
                else:
                    current_rank_info = f"{currenttierpatched} (+{ranking_in_tier})"
                    todays_elo = 0 if season_changed else elo - yesterday_elo

                # ELOに合わせて絵文字を取得
                conditions = [
                    (50, float("inf"), "<a:p10_jppy_verygood:984636995752046673>", "+"),
                    (1, 49, "<a:p10_jppy_good:984636997916327986>", "+"),
                    (0, 0, "<a:p10_jppy_soso:984636999799541760>", "±"),
                    (-49, -1, "<a:p10_jppy_bad:984637001867329586>", ""),
                    (-99, -50, "<a:p10_jppy_terrible:984637004094505001>", ""),
                    (float("-inf"), -100, "<a:p10_jppy_worst:984637006040682496>", ""),
                ]

                for min_limit, max_limit, e, pm in conditions:
                    if min_limit <= todays_elo <= max_limit:
                        emoji = e
                        plusminus = pm
                        break

                # ランクに合わせてバッジの絵文字を取得
                rank_emoji = rank_badge_dict.get(
                    currenttierpatched, "<:p02_win8_1_nogoodgesture:1098118812655693896>"
                )

                # デイリーのWLを取得
                daily_wins: int = wins - yesterday_win
                daily_loses: int = loses - yesterday_lose

                # 前日1試合もプレイしていない場合は投稿対象から除外する
                if daily_wins <= 0 and daily_loses <= 0:
                    update_db()
                    return NO_PLAY

                # これまでのランクすべてのWLを取得
                total_act_rank_wins = 0
                total_number_of_games = 0
                season_data = data["data"]["by_season"]

                for season, info in season_data.items():
                    if "act_rank_wins" in info:
                        total_act_rank_wins += len(info["act_rank_wins"])
                    if "number_of_games" in info:
                        total_number_of_games += info["number_of_games"]
                total_act_rank_loses: int = total_number_of_games - total_act_rank_wins

                # フォーマットに合わせて整形
                result_string = f"{emoji} <@{d_uid}> {rank_emoji}\n- Name: `{api_name}#{api_tag}`\n- {current_rank_info}\n- Daily changes: {plusminus}{todays_elo}\n- Daily matches: {daily_wins}W/{daily_loses}L\n- Current act: {wins}W/{loses}L\n- Lifetime: {total_act_rank_wins}W/{total_act_rank_loses}L"  # noqa: E501

                # DBの情報を今日の取得内容で更新
                update_db()

                return result_string

            fetch_tasks = [fetch(row) for row in rows]
            output = await asyncio.gather(*fetch_tasks)

            # 前日プレイしていた人(文字列の結果)のみ抽出
            player_infos = [info for info in output if isinstance(info, str)]
            # 前日の状況が明確に分かった人(プレイした人、または基準ありで
            # プレイしなかった人=NO_PLAY)が1人でもいれば、「誰もプレイしていない」
            # という判定は正しいとみなせる。
            # 基準なし(NO_BASELINE)やAPI取得失敗(None)しかない場合は、実態が
            # 不明なため誤って「誰もプレイしていない」と投稿しない。
            had_baseline = any(isinstance(info, str) or info is NO_PLAY for info in output)

            def build_embed(description: str) -> discord.Embed:
                embed = discord.Embed()
                embed.set_footer(text=valorant_api.season_txt)
                embed.color = discord.Color.purple()
                embed.description = description
                return embed

            if not player_infos:
                if had_baseline:
                    # 前日誰もプレイしていなかった場合は、その旨を1件だけ投稿する
                    await channel.send(embed=build_embed(random.choice(NO_PLAY_MESSAGES)))
                return

            # プレイヤーごとに1投稿ずつ送信
            for player_info in player_infos:
                await channel.send(embed=build_embed(player_info))
        finally:
            conn.close()

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print("waiting until bot booting")
        await self.bot.wait_until_ready()
        await valorant_api.update_current_season()


async def setup(bot: commands.Bot):
    await bot.add_cog(RankTasks(bot))
