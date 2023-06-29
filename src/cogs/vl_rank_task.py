import asyncio
import json
import sqlite3
from datetime import datetime, timedelta, timezone

import discord
import httpx
from discord.ext import commands, tasks

import cogs.valorant_api


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

        this_month = today.month
        this_day = today.day
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
                except httpx.HTTPError as e:
                    return

                # APIから必要な値を取得
                data = response.json()
                currenttierpatched = data['data']['current_data']['currenttierpatched']
                ranking_in_tier = data['data']['current_data']['ranking_in_tier']
                elo = data['data']['current_data']['elo']
                name = data['data']['name']
                tag = data['data']['tag']

                try:
                        current_season_data = data['data']['by_season'][cogs.valorant_api.current_season]
                except KeyError:
                    win_loses = "Unrated"

                final_rank_patched = current_season_data.get('final_rank_patched', "Unrated")

                if final_rank_patched == "Unrated":
                    win_loses = "Unranked"
                else:
                    wins: int = current_season_data.get('wins', 0)
                    number_of_games = current_season_data.get('number_of_games', 0)
                    loses = number_of_games - wins
                    win_loses = f"{wins}W/{loses}L"

                # 昨日と今日のeloの差分を取得
                todays_elo = elo - yesterday_elo

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

                # フォーマットに合わせて整形
                result_string = f"{emoji} `{name} #{tag}`\n- {currenttierpatched} (+{ranking_in_tier})\n- 前日比: {plusminus}{todays_elo}\n- {win_loses}\n\n"

                # DBの情報を今日の取得内容で更新
                cur.execute("UPDATE val_puuids SET name=?, tag=?, yesterday_elo=? WHERE puuid=?", (name, tag, elo, puuid))
                conn.commit()

                return result_string

            async def main():
                tasks = [fetch(row) for row in rows]
                output = await asyncio.gather(*tasks)
                join = "".join(output)
                return join

            join = await main()

            embed = discord.Embed()
            embed.set_footer(text=cogs.valorant_api.season_txt)
            embed.color = discord.Color.purple()
            embed.title = f"みんなの昨日の活動です。"
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
