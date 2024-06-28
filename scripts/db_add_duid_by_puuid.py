import sqlite3

# PUUIDの入力
puuid_input = input("タスクに追加するPUUIDを入力してください。")

# Discord UIDの入力
try:
    discord_uid_input = int(input("プレイヤーのDiscord UIDを入力してください。整数です。"))
except ValueError:
    print("Discord UIDは整数でなければなりません。")
    exit(1)

# データベースへの接続
conn = sqlite3.connect("data/takohachi.db")
cur = conn.cursor()

# PUUIDの存在確認
cur.execute("SELECT COUNT(*) FROM val_puuids WHERE puuid = ?", (puuid_input,))
puuid_exists = cur.fetchone()[0]

if puuid_exists == 0:
    print("指定されたPUUIDは存在しません。")
    conn.close()
    exit(1)

# Discord UIDの挿入
cur.execute(
    """
    UPDATE val_puuids
    SET d_uid = ?
    WHERE puuid = ?
    """,
    (discord_uid_input, puuid_input)
)

conn.commit()
conn.close()

print("done!")
