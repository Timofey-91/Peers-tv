from flask import Flask, Response
import requests
import re

app = Flask(__name__)

USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.0.1;)"
REFERRER = "https://peers.tv/"

CHANNELS = {
    "rentv": {"id": 16, "offset": 7200},
    "tvc_plus2": {"id": 16, "offset": 7200},
    "tvc_plus4": {"id": 16, "offset": 10},
    "tvc_plus7": {"id": 16, "offset": 36000},  # +1 час Владивосток
}

def get_token():
    url = "http://api.peers.tv/auth/2/token"
    payload = "grant_type=inetra%3Aanonymous&client_id=29783051&client_secret=b4d4eb438d760da95f0acb5bc6b5c760"
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url, data=payload, headers=headers, timeout=8)
    r.raise_for_status()
    return re.search(r'"access_token":"([^"]+)"', r.text).group(1)

@app.route("/channel/<name>.m3u8")
def channel(name):
    if name not in CHANNELS:
        return "Channel not found", 404

    token = get_token()
    ch = CHANNELS[name]
    url = f"http://api.peers.tv/timeshift/tvc/{ch['id']}/playlist.m3u8?token={token}&offset={ch['offset']}"

    headers = {"User-Agent": USER_AGENT, "Referer": REFERRER}
    r = requests.get(url, headers=headers, stream=True, timeout=10)

    return Response(r.iter_content(chunk_size=1024), content_type="application/vnd.apple.mpegurl")

@app.route("/")
def index():
    return "Peers-TV proxy server is running!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
