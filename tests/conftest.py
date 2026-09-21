import os

# cogs/settings は import 時に環境変数を読むため、テスト用のダミー値を先に入れておく。
for name, value in {
    "DIC_KEY": "test-dic-key",
    "PREFIX": "!!",
    "GUILD_ID": "1",
    "REBOOT_LOG_CHANNEL_ID": "1",
}.items():
    os.environ.setdefault(name, value)
