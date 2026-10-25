import os

# Discord設定
# 設定できていない場合はエラーになってほしいので environ["HOGEHOGE"] を使っている
GUILD_ID = int(os.environ["GUILD_ID"])
REBOOT_LOG_CHANNEL_ID = int(os.environ["REBOOT_LOG_CHANNEL_ID"])
