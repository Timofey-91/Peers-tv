from flask import Flask, Response
import requests, re

app = Flask(__name__)

USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.0.1;)"
CHANNELS = {
    "tvc": 16,
    "tvc_plus2": 16,
    "tvc_plus4": 16,
    "tvc_plus7": 16
}
OFFSETS = {
    "tvc": 0,
    "tvc_plus2": 7200,
    "tvc_plus4": 14400,
    "tvc_plus7": 50400  # +7 часов для Владивостока
}

def get_token():
    url = "http://api.peers.tv/auth/2/token"
    payload = "grant_type=inetra%3Aanonymous&client_id=29783051&client_secret=b4d4eb438d760da95f0acb5bc6b5c760"
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url, data=payload, headers=headers, timeout=8)
    if r.status_code != 200:
        return None
    return re.search(r'"access_token":"([^"]+)"', r.text).group(1)

@app.route("/channel/<name>.m3u8")
def channel_m3u8(name):
    if name not in CHANNELS:
        return "Channel not found", 404
    token = get_token()
    if not token:
        return "Cannot get token", 500

    channel_id = CHANNELS[name]
    offset = OFFSETS.get(name, 0)
    url = f"http://api.peers.tv/timeshift/tvc/{channel_id}/playlist.m3u8?token={token}&offset={offset}"

    m3u8_content = f"#EXTM3U\n{url}\n"
    return Response(m3u8_content, mimetype="application/vnd.apple.mpegurl")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
