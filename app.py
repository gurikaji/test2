import os
from flask import Flask, render_template, send_from_directory, jsonify

app = Flask(__name__)

# 写真・動画を入れておくフォルダ名
MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
os.makedirs(MEDIA_FOLDER, exist_ok=True)

# 対応する拡張子
IMAGE_EXTS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
VIDEO_EXTS = {'.mp4', '.webm', '.mov', '.ogg'}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/media')
def get_media_list():
    files = []
    # ファイル名順に並べて取得
    for filename in sorted(os.listdir(MEDIA_FOLDER)):
        ext = os.path.splitext(filename)[1].lower()
        if ext in IMAGE_EXTS:
            files.append({'name': filename, 'type': 'image', 'url': f'/media/{filename}'})
        elif ext in VIDEO_EXTS:
            files.append({'name': filename, 'type': 'video', 'url': f'/media/{filename}'})
    return jsonify(files)

@app.route('/media/<path:filename>')
def serve_media(filename):
    return send_from_directory(MEDIA_FOLDER, filename)

if __name__ == '__main__':
    print("ブラウザで http://127.0.0.1:5000 を開いてください")
    app.run(host='0.0.0.0', port=5000, debug=True)