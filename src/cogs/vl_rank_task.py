import asyncio
import os
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
import httpx
from discord.ext import commands, tasks

from cogs.valorant_api import current_season, season_txt

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
        self.index = 0
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
            db_path = "/data/takohachi.db"

            # データベースに接続とカーソルの取得
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            # レコードを全て取得し、yesterday_eloで降順にソート
            cur.execute("SELECT * FROM val_puuids ORDER BY yesterday_elo DESC")
            rows = cur.fetchall()

            async def fetch(row):
                (
                    puuid,
                    region,
                    name,
                    tag,
                    yesterday_elo,
                    yesterday_win,
                    yesterday_lose,
                    d_uid,
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
                    return

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
                    return

                # jsonから必要な値を取得
                data = response.json()
                currenttierpatched: str = data["data"]["current_data"]["currenttierpatched"]
                ranking_in_tier: str = data["data"]["current_data"]["ranking_in_tier"]
                elo: int = data["data"]["current_data"]["elo"]

                # 新シーズンになって1試合もやってない場合は
                # アクトごとのレスポンス部分はKeyErrorが発生するのでその判定を行う
                try:
                    current_season_data = data["data"]["by_season"][current_season]
                    final_rank_patched: str = current_season_data.get(
                        "final_rank_patched", "Unrated"
                    )
                    number_of_games: int = current_season_data.get("number_of_games", 0)
                    # 正確なwinsを取得するために変更
                    wins: int = len(data["data"]["by_season"][current_season]["act_rank_wins"])
                    loses: int = number_of_games - wins
                except KeyError:
                    wins = 0
                    loses = 0
                    final_rank_patched = "Unrated"

                # ランクがUnratedの場合はELOなども一旦0にする。
                # Unratedではなくランクがついている場合は通常の処理。
                if final_rank_patched == "Unrated":
                    current_rank_info = "Unrated"
                    currenttierpatched = "Unrated"
                    todays_elo = 0
                    elo = 0
                else:
                    current_rank_info = f"{currenttierpatched} (+{ranking_in_tier})"
                    todays_elo: int = elo - yesterday_elo

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
                result_string = f"{emoji} <@{d_uid}> {rank_emoji}\n- Name: `{api_name}#{api_tag}`\n- {current_rank_info}\n- Daily changes: {plusminus}{todays_elo}\n- Daily matches: {daily_wins}W/{daily_loses}L\n- Current act: {wins}W/{loses}L\n- Lifetime: {total_act_rank_wins}W/{total_act_rank_loses}L\n\n"  # noqa: E501

                # DBの情報を今日の取得内容で更新
                cur.execute(
                    "UPDATE val_puuids SET region=?, name=?, tag=?, yesterday_elo=?, yesterday_win=?, yesterday_lose=? WHERE puuid=?",  # noqa: E501
                    (api_region, api_name, api_tag, elo, wins, loses, puuid),
                )
                conn.commit()

                return result_string

            async def main():
                tasks = [fetch(row) for row in rows]
                output = await asyncio.gather(*tasks)

                # 分割されたメッセージのリストを初期化
                messages = []
                current_message = ""
                for player_info in output:
                    # 現在のメッセージと追加するプレイヤー情報を合わせた長さを確認
                    if len(current_message) + len(player_info) > 4096:
                        # 現在のメッセージをリストに追加して、新しいメッセージを開始
                        messages.append(current_message)
                        current_message = player_info
                    else:
                        current_message += player_info

                # 最後のメッセージをリストに追加
                if current_message:
                    messages.append(current_message)

                return messages

            # main関数を実行してメッセージのリストを取得
            messages = await main()

            # 各メッセージを順番に送信
            for msg in messages:
                embed = discord.Embed()
                embed.set_footer(
                    text=f"{season_txt}\n※ WLはランクのみの集計です。\n※ 引き分けは負けとしてカウントされます。\nchr: {len(msg)}"  # noqa: E501
                )
                embed.color = discord.Color.purple()
                embed.title = "みんなの昨日の活動です。"
                embed.description = msg
                await channel.send(embed=embed)

            conn.close()

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print("waiting until bot booting")
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(RankTasks(bot))
