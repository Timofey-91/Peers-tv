from flask import Flask, send_file, abort
import os

app = Flask(__name__)
CHANNEL_DIR = "links/tvc"

CHANNELS = ["tvc", "tvc_plus2", "tvc_plus4", "tvc_plus7"]

@app.route("/channel/<name>.m3u8")
def channel(name):
    if name not in CHANNELS:
        return abort(404)
    path = os.path.join(CHANNEL_DIR, f"{name}.m3u8")
    if not os.path.exists(path):
        return abort(404)
    return send_file(path, mimetype="application/vnd.apple.mpegurl")

@app.route("/")
def index():
    return "Peers-TV proxy server is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
