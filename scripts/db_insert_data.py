import sqlite3

puuid_input = input("タスクに追加するPUUIDを入力してください。")

try:
    elo_input = int(input("現在のELOを入力してください。"))
except ValueError:
    print("ELOは整数でなければなりません。")
    exit(1)

try:
    region_input = input("プレイヤーのリージョンを入力してください。(eu, na, latam, br, ap, kr): ")
    if region_input not in ['eu', 'na', 'latam', 'br', 'ap', 'kr']:
        raise ValueError("無効なリージョンが入力されました。")
except ValueError:
    print("無効なリージョンが入力されました。")
    exit(1)

try:
    discord_uid_input = int(input("プレイヤーのDiscord UIDを入力してください。整数です。"))
except ValueError:
    print("Discord UIDは整数でなければなりません。")
    exit(1)

conn = sqlite3.connect("data/takohachi.db")

cur = conn.cursor()

cur.execute(
    """
    INSERT INTO val_puuids (puuid, region, name, tag, yesterday_elo, yesterday_win, yesterday_lose, d_uid)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""",
    (puuid_input, region_input, "xxxxx", "xxxxx", elo_input, 0, 0, discord_uid_input),
)

conn.commit()
conn.close()

print("done!")
