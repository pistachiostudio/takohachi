"""save_image 用の Google Drive リフレッシュトークンを取得する。

GCP で作った OAuth クライアント(種類: デスクトップ アプリ)の
クライアント ID とシークレットを入力すると、ブラウザで Google の認可画面が開く。
画像の保存先フォルダを持っているアカウントで許可すると、リフレッシュトークンが表示される。

    python scripts/get_drive_refresh_token.py

標準ライブラリだけで動くので、uv sync していない環境でも実行できる。
"""

import getpass
import http.server
import json
import secrets
import urllib.parse
import urllib.request
import webbrowser

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
# 既存のフォルダにファイルを追加するため、drive.file ではなく drive を使う
SCOPE = "https://www.googleapis.com/auth/drive"


def wait_for_code(server: http.server.HTTPServer) -> dict[str, str]:
    """リダイレクトを1回だけ受け取り、クエリパラメータを返す。"""
    result: dict[str, str] = {}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            query = urllib.parse.urlparse(self.path).query
            result.update({k: v[0] for k, v in urllib.parse.parse_qs(query).items()})
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write("認可を受け取りました。このタブは閉じて大丈夫です。".encode())

        def log_message(self, format, *args):
            pass

    server.RequestHandlerClass = Handler
    server.handle_request()
    return result


def main():
    client_id = input("クライアント ID: ").strip()
    client_secret = getpass.getpass("クライアント シークレット(入力は表示されません): ").strip()

    server = http.server.HTTPServer(("127.0.0.1", 0), http.server.BaseHTTPRequestHandler)
    redirect_uri = f"http://127.0.0.1:{server.server_port}"
    state = secrets.token_urlsafe(16)

    url = (
        AUTH_URL
        + "?"
        + urllib.parse.urlencode(
            {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "response_type": "code",
                "scope": SCOPE,
                # リフレッシュトークンを必ず発行させる
                "access_type": "offline",
                "prompt": "consent",
                "state": state,
            }
        )
    )
    print(f"\nブラウザで認可画面を開きます。開かない場合は次の URL を開いてください:\n{url}\n")
    webbrowser.open(url)

    params = wait_for_code(server)
    if params.get("state") != state:
        raise SystemExit("state が一致しません。もう一度やり直してください。")
    if "code" not in params:
        raise SystemExit(f"認可されませんでした: {params.get('error')}")

    data = urllib.parse.urlencode(
        {
            "code": params["code"],
            "client_id": client_id,
            "client_secret": client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
    ).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=data)) as res:
        token = json.load(res)

    if "refresh_token" not in token:
        raise SystemExit("リフレッシュトークンが返されませんでした。もう一度やり直してください。")
    print("Railway の DRIVE_OAUTH_REFRESH_TOKEN に次の値を設定してください:\n")
    print(token["refresh_token"])


if __name__ == "__main__":
    main()
