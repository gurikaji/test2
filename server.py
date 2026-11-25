import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_FOLDER = os.path.join(BASE_DIR, "media")
TEMPLATE_PATH = os.path.join(BASE_DIR, "templates", "index.html")

os.makedirs(MEDIA_FOLDER, exist_ok=True)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
VIDEO_EXTS = {".mp4", ".webm", ".mov", ".ogg"}


def get_media_list():
    files = []
    for filename in sorted(os.listdir(MEDIA_FOLDER)):
        full_path = os.path.join(MEDIA_FOLDER, filename)
        if not os.path.isfile(full_path):
            continue
        ext = os.path.splitext(filename)[1].lower()
        if ext in IMAGE_EXTS:
            files.append({"name": filename, "type": "image", "url": f"/media/{filename}"})
        elif ext in VIDEO_EXTS:
            files.append({"name": filename, "type": "video", "url": f"/media/{filename}"})
    return files


class ViewerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        # トップページ（index.html）
        if path == "/":
            if not os.path.isfile(TEMPLATE_PATH):
                self.send_error(404, "index.html not found")
                return
            with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
                body = f.read().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # メディア一覧API（/api/media）
        if path == "/api/media":
            data = get_media_list()
            body = json.dumps(data, ensure_ascii=False).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        # 画像・動画ファイル配信（/media/ファイル名）
        if path.startswith("/media/"):
            rel_name = path[len("/media/") :]
            safe_path = os.path.abspath(os.path.join(MEDIA_FOLDER, rel_name))
            base_abs = os.path.abspath(MEDIA_FOLDER)
            # フォルダ外へのアクセス防止
            if not safe_path.startswith(base_abs + os.sep) or not os.path.isfile(safe_path):
                self.send_error(404, "File not found")
                return

            content_type, _ = mimetypes.guess_type(safe_path)
            if not content_type:
                content_type = "application/octet-stream"

            with open(safe_path, "rb") as f:
                body = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return

        self.send_error(404, "Not found")

    def log_message(self, format, *args):
        # ターミナルのログをシンプルにする（必要なら消してOK）
        return


def main():
    host = "127.0.0.1"
    port = 5000
    server = ThreadingHTTPServer((host, port), ViewerHandler)
    print(f"ブラウザで http://{host}:{port} を開いてください（停止は Ctrl + C）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nサーバーを停止しました")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()