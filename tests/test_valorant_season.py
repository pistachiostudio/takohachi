def test_format_season_txt(monkeypatch):
    # valorant_api.pyはモジュールレベルでVALORANT_TOKENを要求するため、
    # importする前にダミー値をセットする
    monkeypatch.setenv("VALORANT_TOKEN", "dummy")

    from cogs.valorant_api import _format_season_txt

    assert _format_season_txt("V26", "ACT V") == "V26 // Act 5"
    assert _format_season_txt("V26", "ACT VI") == "V26 // Act 6"
    assert _format_season_txt("Closed Beta", "ACT I") == "Closed Beta // Act 1"


def test_format_season_txt_unknown_roman_numeral(monkeypatch):
    # 未知のローマ数字表記の場合は変換せずそのまま使う
    monkeypatch.setenv("VALORANT_TOKEN", "dummy")

    from cogs.valorant_api import _format_season_txt

    assert _format_season_txt("V26", "ACT X") == "V26 // Act X"
