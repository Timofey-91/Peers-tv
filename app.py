import requests
import xml.etree.ElementTree as ET
from flask import Flask, Response, abort

app = Flask(__name__)

PEERS_API = "http://api.peers.tv/peerstv/2/"
PLAYER_UA = "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:35.0) Gecko/20100101 Firefox/35.0"

# Кэшируем список каналов (чтобы не дёргать API каждый раз)
channel_cache = {}

def load_channels():
    """Загружаем список каналов из Peers.TV"""
    global channel_cache
    try:
        resp = requests.get(PEERS_API, headers={"User-Agent": PLAYER_UA}, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)

        namespace = {"p": "http://xspf.org/ns/0/"}
        channels = {}
        for track in root.findall("./p:trackList/p:track", namespace):
            title = track.find("./p:title", namespace).text.strip()
            url = track.find("./p:location", namespace).text.strip()
            channels[title.lower()] = url
        channel_cache = channels
        return channels
    except Exception as e:
        print(f"[ERROR] Не удалось загрузить список каналов: {e}")
        return {}

@app.route("/")
def index():
    """Просто список доступных каналов"""
    if not channel_cache:
        load_channels()
    return "<br>".join([f"/channel/{name}.m3u8" for name in channel_cache.keys()])

@app.route("/channel/<name>.m3u8")
def get_channel(name):
    """Получение m3u8 ссылки по названию канала"""
    if not channel_cache:
        load_channels()

    # нормализуем название
    key = name.lower().replace("+", "plus").replace("%20", " ")

    if key not in channel_cache:
        abort(404, f"Канал '{name}' не найден")

    real_url = channel_cache[key]

    # можно либо просто редиректить, либо проксировать
    try:
        resp = requests.get(real_url, headers={"User-Agent": PLAYER_UA}, timeout=10)
        return Response(resp.content, mimetype="application/vnd.apple.mpegurl")
    except Exception as e:
        abort(502, f"Ошибка получения потока: {e}")

if __name__ == "__main__":
    load_channels()
    app.run(host="0.0.0.0", port=5000, debug=True)
