import os
from unittest.mock import MagicMock, patch

from cogs import card_count


def _count(cell, emoji):
    worksheet = MagicMock()
    # 未登録(None)なら、追加した行を2回目のfindで見つける
    worksheet.find.side_effect = [cell, MagicMock(row=9)]
    worksheet.cell.return_value.value = "4"
    with (
        patch.dict(os.environ, {"CARDCOUNT_KEY": "key"}),
        patch("cogs.card_count.google_sheets.open_first_sheet", return_value=worksheet),
    ):
        card_count.count_card("user#1", 42, card_count.CARD_COLUMNS[emoji])
    return worksheet


def test_existing_user_counts_up_the_matching_column():
    cell = MagicMock(row=5, col=1)
    red = _count(cell, "<a:p00_card_red:934125658529988648>")
    red.update_cell.assert_called_once_with(5, 3, 5)  # C列(レッド)
    red.sort.assert_called_once_with((5, "des"))

    siren = _count(cell, "<:p05_siren:801693375043862580>")
    siren.update_cell.assert_called_once_with(5, 4, 5)  # D列(サイレン)


def test_new_user_is_appended_with_sum_and_user_id():
    worksheet = _count(None, "<:p05_card_yellow:934125477424140308>")
    worksheet.append_row.assert_called_once_with(["user#1", 1, 0, 0])
    worksheet.update_cell.assert_any_call(9, 5, "=SUM(B9:D9)")
    worksheet.update_cell.assert_any_call(9, 6, "42")


def test_all_cogs_can_be_imported(monkeypatch):
    import importlib
    import pkgutil

    import cogs

    for name in ("VALORANT_TOKEN", "INU_VC_ID", "NEKO_VC_ID", "KAME_VC_ID", "KYORYU_VC_ID"):
        monkeypatch.setenv(name, "1")
    for module in pkgutil.iter_modules(cogs.__path__):
        importlib.import_module(f"cogs.{module.name}")
