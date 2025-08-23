import os
import json
import time
import requests
from flask import Flask, Response, jsonify

app = Flask(__name__)

CACHE_FILE = "cache.json"
CACHE_TTL = 24 * 3600  # 24 часа
DIMONOVICH_URL = "https://raw.githubusercontent.com/Dimonovich/TV/Dimonovich/FREE/TV"

CHANNELS_TO_SERVE = ["ТВЦ", "ТВЦ +2", "ТВЦ +4"]


def fetch_channels():
    """Скачиваем плейлист Dimonovich и вытаскиваем только нужные каналы"""
    try:
        resp = requests.get(DIMONOVICH_URL, timeout=10)
        resp.raise_for_status()
        lines = resp.text.splitlines()

        result = {}
        current_name = None

        for line in lines:
            if line.startswith("#EXTINF"):
                for name in CHANNELS_TO_SERVE:
                    if name in line:
                        current_name = name
                        break
            elif line.startswith("http") and current_name:
                result[current_name] = line.strip()
                current_name = None

        return result
    except Exception as e:
        print(f"[ERROR] Не удалось загрузить список каналов: {e}")
        return {}


def load_cache():
    """Загружаем кеш из файла, если он свежий"""
    if os.path.exists(CACHE_FILE):
        mtime = os.path.getmtime(CACHE_FILE)
        if time.time() - mtime < CACHE_TTL:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}


def save_cache(data):
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.route("/channel/<name>.m3u8")
def serve_channel(name):
    cache = load_cache()

    if not cache:
        cache = fetch_channels()
        if cache:
            save_cache(cache)

    channel_name = name.replace("_", " ").upper()

    for ch, url in cache.items():
        if ch.upper() == channel_name:
            return Response(f"#EXTM3U\n#EXTINF:-1,{ch}\n{url}", mimetype="application/vnd.apple.mpegurl")

    return Response("#EXTM3U\n#EXTINF:-1,Канал не найден\n", mimetype="application/vnd.apple.mpegurl")


@app.route("/channels")
def list_channels():
    cache = load_cache()
    if not cache:
        cache = fetch_channels()
        if cache:
            save_cache(cache)
    return jsonify(cache)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)
