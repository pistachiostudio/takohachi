import logging
import os

from libs.http_client import HTTPClient

logger = logging.getLogger(__name__)

VALORANT_TOKEN = os.environ["VALORANT_TOKEN"]

# 現在のシーズン(Act)情報。update_current_season()で自動更新される。
# HenrikDevのeXaY形式のシーズンIDは、シーズン開始前にキーだけ先行して
# 生成されることがあるため、v1/contentのisActiveフラグを正としてUUIDで
# 特定し、そのUUIDをリーダーボード上位プレイヤーのv3 MMRデータと突き合わせて
# eXaY形式に変換する。
current_season = "e11a5"
season_txt = "V26 // Act 5"

# v1/contentのact名("ACT V"など)はローマ数字表記のため、
# 公式の表記("Season 2026 // Act 5"の略記"V26 // Act 5")に合わせて
# アラビア数字に変換する。
_ROMAN_TO_ARABIC = {
    "I": "1",
    "II": "2",
    "III": "3",
    "IV": "4",
    "V": "5",
    "VI": "6",
    "VII": "7",
    "VIII": "8",
    "IX": "9",
}


def _format_season_txt(episode_name: str, act_name: str) -> str:
    roman = act_name.removeprefix("ACT ").strip()
    act_number = _ROMAN_TO_ARABIC.get(roman, roman)
    return f"{episode_name} // Act {act_number}"


async def update_current_season(region: str = "ap") -> None:
    """現在のシーズン(Act)情報をAPIから取得し、モジュール変数を更新する。"""
    global current_season, season_txt

    headers = {"Authorization": VALORANT_TOKEN}
    client = HTTPClient()

    try:
        content = await client.get(
            "https://api.henrikdev.xyz/valorant/v1/content", headers=headers, timeout=15
        )
        acts = content["data"]["acts"]
        active_act = next(a for a in acts if a["type"] == "act" and a["isActive"])
        active_episode = next(a for a in acts if a["id"] == active_act["parentId"])
        active_act_id = active_act["id"]
        new_season_txt = _format_season_txt(active_episode["name"], active_act["name"])

        leaderboard = await client.get(
            f"https://api.henrikdev.xyz/valorant/v3/leaderboard/{region}/pc",
            params={"size": 1},
            headers=headers,
            timeout=15,
        )
        top_puuid = leaderboard["data"]["players"][0]["puuid"]

        mmr = await client.get(
            f"https://api.henrikdev.xyz/valorant/v3/by-puuid/mmr/{region}/pc/{top_puuid}",
            headers=headers,
            timeout=15,
        )
        seasonal = next(s for s in mmr["data"]["seasonal"] if s["season"]["id"] == active_act_id)
        new_current_season = seasonal["season"]["short"]

    except Exception:
        logger.exception("Failed to update current valorant season, keeping previous value")
        return

    current_season = new_current_season
    season_txt = new_season_txt
    logger.info(f"Updated current valorant season: {current_season} ({season_txt})")
