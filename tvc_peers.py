import requests
import os
import re

output_dir = "links/tvc"
os.makedirs(output_dir, exist_ok=True)

USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.0.1;)"
REFERRER = "https://peers.tv/"

CHANNELS = {
    "tvc": 16,
    "tvc_plus2": 16,
    "tvc_plus4": 16,
    "tvc_plus7": 16,
}

def get_token():
    url = "http://api.peers.tv/auth/2/token"
    payload = "grant_type=inetra%3Aanonymous&client_id=29783051&client_secret=b4d4eb438d760da95f0acb5bc6b5c760"
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url, data=payload, headers=headers, timeout=8)
    if r.status_code != 200:
        return None
    match = re.search(r'"access_token":"([^"]+)"', r.text)
    if not match:
        return None
    return match.group(1)

def get_real_stream_url(channel_id):
    # Получаем реальный поток Timeshift для канала
    token = get_token()
    if not token:
        return None
    url = f"http://api.peers.tv/timeshift/tvc/{channel_id}/playlist.m3u8?token={token}"
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=8)
    if r.status_code != 200:
        return None
    # Берём первую строку с .m3u8 или .ts сегментом
    return url

def save_link(name, url):
    filepath = os.path.join(output_dir, f"{name}.m3u8")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(url)  # Только URL, без #EXTM3U
    print(f"Сохранил {name}: {url}")

if __name__ == "__main__":
    for name, ch_id in CHANNELS.items():
        url = get_real_stream_url(ch_id)
        if url:
            save_link(name, url)
        else:
            print(f"Ошибка получения ссылки для {name}")
