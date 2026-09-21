from unittest.mock import MagicMock

from cogs import repository
from cogs.repository import TriggerRepository

HEADER = ["trigger", "alias01", "alias02", "response", "title", "description"]


def _repo(rows):
    """gspreadに接続せずに、シートの中身だけを差し替えたTriggerRepositoryを作る。"""
    repo = TriggerRepository.__new__(TriggerRepository)
    repo.header_list = HEADER
    repo.worksheet = MagicMock()
    # 1〜2行目はヘッダー周辺、3行目以降がデータ
    repo.worksheet.get_all_values.return_value = [["memo"], HEADER, *rows]
    repo._rows_cache = None
    repo._rows_cached_at = 0.0
    return repo


def test_list_entries_maps_columns_and_skips_empty_trigger():
    repo = _repo(
        [
            ["gomi", "ごみ", "", "", "ゴミの日", "月木"],
            ["", "x", "", "", "", ""],
            ["short"],  # 列が足りない行
        ]
    )

    entries = repo.list_entries()

    assert [e["trigger"] for e in entries] == ["gomi", "short"]
    assert entries[0] == {
        "trigger": "gomi",
        "alias01": "ごみ",
        "alias02": "",
        "title": "ゴミの日",
        "description": "月木",
    }
    assert entries[1]["title"] == ""


def test_rows_are_cached_until_ttl(monkeypatch):
    repo = _repo([["gomi"]])
    now = [1000.0]
    monkeypatch.setattr(repository.time, "monotonic", lambda: now[0])

    repo.list_triggers()
    repo.list_entries()
    assert repo.worksheet.get_all_values.call_count == 1

    now[0] += repository.ROWS_CACHE_TTL_SECONDS + 1
    repo.list_triggers()
    assert repo.worksheet.get_all_values.call_count == 2
