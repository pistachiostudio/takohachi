import sqlite3

puuid_input = input("タスクに追加するPUUIDを入力してください。")

try:
    elo_input = int(input("現在のELOを入力してください。"))
except ValueError:
    print("ELOは整数でなければなりません。")
    exit(1)

conn = sqlite3.connect("data/takohachi.db")

cur = conn.cursor()

cur.execute(
    """
    INSERT INTO val_puuids (puuid, region, name, tag, yesterday_elo)
    VALUES (?, ?, ?, ?, ?)
""",
    (puuid_input, "ap", "xxxxx", "xxxxx", elo_input),
)

conn.commit()
conn.close()

print("done!")
