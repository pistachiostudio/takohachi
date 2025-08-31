import os
from pathlib import Path

CLIENT_SECRETS_PATH = Path("/app/client_secrets.json").resolve()
ADD_SSL_CLIENT_SECRETS_PATH = Path("/app/addssl_client_secrets.json").resolve()

# Discord設定
# 設定できていない場合はエラーになってほしいので environ["HOGEHOGE"] を使っている
GUILD_ID = int(os.environ["GUILD_ID"])
REBOOT_LOG_CHANNEL_ID = int(os.environ["REBOOT_LOG_CHANNEL_ID"])
