import sqlite3

# データベースに接続
conn = sqlite3.connect("data/takohachi.db")

# カーソルを取得
cur = conn.cursor()

# 新しいレコードを追加
cur.execute(
    """
    INSERT INTO val_puuids (puuid, region, name, tag, yesterday_elo)
    VALUES (?, ?, ?, ?, ?)
""",
    ("xxxxx", "ap", "xxxxx", "xxxxx", 1000),
)

# 変更をコミット
conn.commit()

# データベースとの接続を閉じる
conn.close()
