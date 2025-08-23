import os
import requests
from flask import Flask, Response, abort

app = Flask(__name__)

PEERS_API = "http://api.peers.tv/peerstv/2/channels/"
USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.0.1;)"


def get_channels():
    """Загружаем список каналов с Peers.TV API"""
    resp = requests.get(PEERS_API, headers={"User-Agent": USER_AGENT})
    if resp.status_code != 200:
        return None
    return resp.json()


def get_channel_id(alias: str):
    """Находим id канала по alias (например 'tvc+4')"""
    channels = get_channels()
    if not channels:
        return None

    for ch in channels.get("channels", []):
        if ch.get("alias") == alias:
            return ch.get("id")
    return None


def get_stream_url(channel_id: int):
    """Получаем реальную ссылку для timeshift"""
    url = f"http://api.peers.tv/timeshift/{channel_id}/playlist.m3u8"
    headers = {"User-Agent": USER_AGENT, "Referer": "https://peers.tv/"}
    resp = requests.get(url, headers=headers, allow_redirects=False)

    if resp.status_code in (302, 301):
        return resp.headers.get("Location")  # реальный m3u8
    elif resp.status_code == 200:
        return url
    return None


@app.route("/channel/<alias>.m3u8")
def channel(alias):
    """Прокси-ссылка для канала"""
    channel_id = get_channel_id(alias)
    if not channel_id:
        return abort(404, f"Канал {alias} не найден")

    real_url = get_stream_url(channel_id)
    if not real_url:
        return abort(502, "Не удалось получить ссылку")

    # Делаем прокси-запрос
    r = requests.get(real_url, headers={"User-Agent": USER_AGENT}, stream=True)
    return Response(r.iter_content(chunk_size=8192),
                    content_type="application/vnd.apple.mpegurl")


@app.route("/")
def index():
    return "Peers.TV proxy работает 🚀. Пример: /channel/tvc+4.m3u8"


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
