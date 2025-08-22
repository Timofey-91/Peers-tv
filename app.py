from flask import Flask, send_file
import os

app = Flask(__name__)

# Папка, где лежат ваши .m3u8 файлы
BASE_DIR = os.path.join(os.getcwd(), "links", "tvc")

@app.route("/channel/<name>.m3u8")
def get_channel(name):
    filepath = os.path.join(BASE_DIR, f"{name}.m3u8")
    if not os.path.exists(filepath):
        return "Channel not found", 404
    # Отдаём файл с правильным MIME типом для .m3u8
    return send_file(filepath, mimetype="application/vnd.apple.mpegurl")

@app.route("/")
def index():
    # Просто проверка, что сервер работает
    return "Peers-TV Flask server is running!"

if __name__ == "__main__":
    print(f"Serving .m3u8 files from: {BASE_DIR}")
    app.run(host="0.0.0.0", port=8000)
