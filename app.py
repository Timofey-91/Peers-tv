from flask import Flask, send_file
import os

app = Flask(__name__)

BASE_DIR = os.path.join(os.getcwd(), "links", "tvc")

@app.route("/channel/<name>.m3u8")
def get_channel(name):
    filepath = os.path.join(BASE_DIR, f"{name}.m3u8")
    if not os.path.exists(filepath):
        return "Channel not found", 404
    return send_file(filepath, mimetype="application/vnd.apple.mpegurl")

@app.route("/")
def index():
    return "Peers-TV Flask server is running!"

if __name__ == "__main__":
    print(f"Serving .m3u8 files from: {BASE_DIR}")
    if os.path.exists(BASE_DIR):
        print("Содержимое папки:", os.listdir(BASE_DIR))
    else:
        print("Папка links/tvc не найдена!")
    app.run(host="0.0.0.0", port=8000)
