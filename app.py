from flask import Flask, send_file
import os

app = Flask(__name__)
OUTPUT_DIR = os.path.join(os.getcwd(), "links", "tvc")  # полный путь

@app.route("/channel/<name>.m3u8")
def get_channel(name):
    path = os.path.join(OUTPUT_DIR, f"{name}.m3u8")
    if not os.path.exists(path):
        return "Channel not found", 404
    return send_file(path, mimetype="application/vnd.apple.mpegurl")

if __name__ == "__main__":
    print("Serving from:", OUTPUT_DIR)
    app.run(host="0.0.0.0", port=8000)
