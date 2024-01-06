import sqlite3

puuid_input = input("タスクに追加するPUUIDを入力してください。")

try:
    elo_input = int(input("現在のELOを入力してください。"))
except ValueError:
    print("ELOは整数でなければなりません。")
    exit(1)

region_input = input("プレイヤーのリージョンを入力してください。(eu, na, latam, br, ap, kr)")

conn = sqlite3.connect("data/takohachi.db")

cur = conn.cursor()

cur.execute(
    """
    INSERT INTO val_puuids (puuid, region, name, tag, yesterday_elo, yesterday_win, yesterday_lose)
    VALUES (?, ?, ?, ?, ?, ?, ?)
""",
    (puuid_input, region_input, "xxxxx", "xxxxx", elo_input, 0, 0),
)

conn.commit()
conn.close()

print("done!")
