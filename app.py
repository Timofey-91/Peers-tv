import requests
from flask import Flask, Response, jsonify

app = Flask(__name__)

API_BASE = "http://api.peers.tv"
DEVICE_ID = "simpletv"   # можно любое, peers.tv примет
PROFILE = "2"            # профиль (в Lua тоже был "2")

# какие каналы оставляем
CHANNELS_TO_KEEP = ["ТВЦ", "ТВЦ+2", "ТВЦ+4"]

# кэш для токена и плейлиста
auth_token = None
channels_cache = {}


def get_auth_token():
    """Авторизация и получение access_token"""
    global auth_token
    url = f"{API_BASE}/auth/{PROFILE}/token"
    payload = {"device": DEVICE_ID}
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        data = r.json()
        auth_token = data.get("access_token")
        return auth_token
    except Exception as e:
        print(f"[ERROR] Не удалось получить токен: {e}")
        return None


def load_playlist():
    """Загружаем плейлист и фильтруем каналы"""
    global channels_cache
    token = auth_token or get_auth_token()
    if not token:
        return {}

    url = f"{API_BASE}/iptv/{PROFILE}/playlist.m3u?access_token={token}"
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        text = r.text
    except Exception as e:
        print(f"[ERROR] Не удалось загрузить плейлист: {e}")
        return {}

    # Парсим M3U вручную
    channels = {}
    current_name = None
    for line in text.splitlines():
        if line.startswith("#EXTINF:"):
            # имя канала после запятой
            if "," in line:
                current_name = line.split(",", 1)[1].strip()
        elif line.endswith(".m3u8") and current_name:
            if any(ch in current_name for ch in CHANNELS_TO_KEEP):
                channels[current_name] = line.strip()
            current_name = None

    channels_cache = channels
    return channels


@app.route("/")
def index():
    return jsonify({
        "status": "ok",
        "channels": list(channels_cache.keys()) or "Нет загруженных каналов"
    })


@app.route("/channel/<name>.m3u8")
def get_channel(name):
    """Отдаём m3u8 для конкретного канала"""
    if not channels_cache:
        load_playlist()

    # ищем совпадение по имени
    for ch_name, url in channels_cache.items():
        if name.lower() in ch_name.lower().replace(" ", ""):
            try:
                r = requests.get(url, stream=True, timeout=10)
                return Response(r.iter_content(chunk_size=1024),
                                content_type="application/vnd.apple.mpegurl")
            except Exception as e:
                return Response(f"# Ошибка при загрузке: {e}", mimetype="text/plain")

    return Response("# Канал не найден", mimetype="text/plain")


if __name__ == "__main__":
    get_auth_token()
    load_playlist()
    app.run(host="0.0.0.0", port=5000, debug=True)
