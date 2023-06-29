import asyncio
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
import httpx
from discord.ext import commands, tasks

from cogs.valorant_api import current_season, season_txt

# ランクに合わせてバッジを表示するための辞書
rank_badge_dict: dict[str, str] = {
    "Unranked": "<:Unranked_Rank:1123928409676972092>",
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
        today = datetime.now(JST)

        this_hour = today.hour
        this_minute = today.minute

        if this_hour == 7 and 0 <= this_minute <= 9:
            DB_DIRECTORY = "/data/takohachi.db"

            # データベースに接続とカーソルの取得
            conn = sqlite3.connect(DB_DIRECTORY)
            cur = conn.cursor()

            # レコードを全て取得し、yesterday_eloで降順にソート
            cur.execute("SELECT * FROM val_puuids ORDER BY yesterday_elo DESC")
            rows = cur.fetchall()

            async def fetch(row):
                puuid, region, name, tag, yesterday_elo = row

                # 非同期でリクエスト
                try:
                    url = f"https://api.henrikdev.xyz/valorant/v2/by-puuid/mmr/{region}/{puuid}"
                    async with httpx.AsyncClient() as client:
                        response = await client.get(url, timeout=60)
                except httpx.HTTPError:
                    return

                # APIから必要な値を取得
                data = response.json()
                currenttierpatched = data["data"]["current_data"]["currenttierpatched"]
                ranking_in_tier = data["data"]["current_data"]["ranking_in_tier"]
                elo: int = data["data"]["current_data"]["elo"]
                name = data["data"]["name"]
                tag = data["data"]["tag"]

                try:
                    current_season_data = data["data"]["by_season"][current_season]
                except KeyError:
                    win_loses = "-W/-L"

                final_rank_patched = current_season_data.get("final_rank_patched", "Unrated")

                if final_rank_patched == "Unrated":
                    win_loses = "-W/-L"
                else:
                    wins: int = current_season_data.get("wins", 0)
                    number_of_games: int = current_season_data.get("number_of_games", 0)
                    loses: int = number_of_games - wins
                    win_loses = f"{wins}W/{loses}L"

                if win_loses == "-W/-L":
                    current_rank_info = "Unranked"
                    currenttierpatched = "Unranked"
                    todays_elo: int = 0
                else:
                    current_rank_info = f"{currenttierpatched} (+{ranking_in_tier})"
                    todays_elo: int = elo - yesterday_elo

                # todays_eloの値に応じて絵文字を選択
                if todays_elo > 0:
                    emoji = "<a:p10_jppy_verygood:984636995752046673>"
                    plusminus = "+"
                elif todays_elo < 0:
                    emoji = "<a:p10_jppy_bad:984637001867329586>"
                    plusminus = ""
                else:
                    emoji = "<a:p10_jppy_soso:984636999799541760>"
                    plusminus = "±"

                # ランクに合わせランクのバッジの絵文字を取得
                rank_emoji = rank_badge_dict.get(
                    currenttierpatched, "<:p02_win8_1_nogoodgesture:1098118812655693896>"
                )

                # フォーマットに合わせて整形
                result_string = f"{emoji} `{name} #{tag}` {rank_emoji}\n- {current_rank_info}\n- 前日比:\
                  {plusminus}{todays_elo}\n- {win_loses}\n\n"

                # DBの情報を今日の取得内容で更新
                cur.execute(
                    "UPDATE val_puuids SET name=?, tag=?, yesterday_elo=? WHERE puuid=?",
                    (name, tag, elo, puuid),
                )
                conn.commit()

                return result_string

            async def main():
                tasks = [fetch(row) for row in rows]
                output = await asyncio.gather(*tasks)
                join = "".join(output)
                return join

            join = await main()

            embed = discord.Embed()
            embed.set_footer(text=season_txt)
            embed.color = discord.Color.purple()
            embed.title = "みんなの昨日の活動です。"
            embed.description = f"{join}"
            await channel.send(embed=embed)

            conn.close()

    # デプロイ後Botが完全に起動してからタスクを回す
    @printer.before_loop
    async def before_printer(self):
        print("waiting until bot booting")
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(RankTasks(bot))
