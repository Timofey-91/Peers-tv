import requests
from flask import Flask, Response

app = Flask(__name__)

GITHUB_URL = "https://raw.githubusercontent.com/Dimonovich/TV/Dimonovich/FREE/TV"

# Сопоставляем наши роуты с названиями каналов в плейлисте
CHANNEL_MAP = {
    "tvc": "ТВЦ",
    "tvc+2": "ТВЦ +2",
    "tvc+4": "ТВЦ +4",
}

def get_channel_url(channel_name):
    try:
        resp = requests.get(GITHUB_URL, timeout=10)
        resp.raise_for_status()
        lines = resp.text.splitlines()
        for i, line in enumerate(lines):
            if channel_name in line:
                return lines[i+1] if i+1 < len(lines) else None
    except Exception as e:
        print(f"Ошибка при получении канала {channel_name}: {e}")
    return None

@app.route("/channel/<name>.m3u8")
def channel(name):
    if name not in CHANNEL_MAP:
        return Response("#EXTM3U\n# Канал не найден\n", mimetype="application/vnd.apple.mpegurl")

    channel_url = get_channel_url(CHANNEL_MAP[name])
    if not channel_url:
        return Response("#EXTM3U\n# Ссылка не найдена\n", mimetype="application/vnd.apple.mpegurl")

    m3u = f"#EXTM3U\n#EXTINF:-1,{CHANNEL_MAP[name]}\n{channel_url}\n"
    return Response(m3u, mimetype="application/vnd.apple.mpegurl")

@app.route("/")
def index():
    return "Работает! Доступные каналы: /channel/tvc.m3u8, /channel/tvc+2.m3u8, /channel/tvc+4.m3u8"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
