import requests
import os
import re

# Папка для сохранения
output_dir = "links/tvc"
os.makedirs(output_dir, exist_ok=True)

USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.0.1;)"
REFERRER = "https://peers.tv/"

# Каналы с id и offset
CHANNELS = {
    "tvc": {"id": 16, "offset": 0},             # Москва
    "tvc_plus2": {"id": 16, "offset": 7200},    # +2 часа
    "tvc_plus4": {"id": 16, "offset": 14400},   # +4 часа
    "tvc_plus7": {"id": 16, "offset": 25200},   # +7 часов (Хабаровск)
}

def get_token():
    url = "http://api.peers.tv/auth/2/token"
    payload = "grant_type=inetra%3Aanonymous&client_id=29783051&client_secret=b4d4eb438d760da95f0acb5bc6b5c760"
    headers = {
        "User-Agent": USER_AGENT,
        "Content-Type": "application/x-www-form-urlencoded",
    }
    r = requests.post(url, data=payload, headers=headers, timeout=8)
    if r.status_code != 200:
        print("Ошибка получения токена:", r.text)
        return None
    match = re.search(r'"access_token":"([^"]+)"', r.text)
    if not match:
        return None
    return match.group(1)

def get_real_stream_url(channel_id: int, offset: int = 0) -> str | None:
    token = get_token()
    if not token:
        return None
    url = f"http://api.peers.tv/timeshift/tvc/{channel_id}/playlist.m3u8?token={token}&offset={offset}"
    r = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=8)
    if r.status_code != 200:
        print("Ошибка получения ссылки:", r.text)
        return None
    return url

def save_link(name, url):
    filepath = os.path.join(output_dir, f"{name}.m3u8")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(url)  # Сохраняем только саму ссылку
    print(f"Сохранил {name}: {url}")

if __name__ == "__main__":
    for name, info in CHANNELS.items():
        url = get_real_stream_url(info["id"], info["offset"])
        if url:
            save_link(name, url)
        else:
            print(f"Ошибка получения ссылки для {name}")
