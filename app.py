from flask import Flask, send_file
import os

app = Flask(__name__)

# Папка с m3u8 файлами
BASE_DIR = os.path.join(os.getcwd(), "links", "tvc")

@app.route("/channel/<name>.m3u8")
def get_channel(name):
    filepath = os.path.join(BASE_DIR, f"{name}")
    if not os.path.exists(filepath):
        return "Channel not found", 404
    return send_file(filepath, mimetype="application/vnd.apple.mpegurl")

@app.route("/")
def index():
    return "Peers-TV Flask server is running!"

if __name__ == "__main__":
    print(f"Serving .m3u8 files from: {BASE_DIR}")
    app.run(host="0.0.0.0", port=8000)
