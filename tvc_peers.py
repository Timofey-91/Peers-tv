import requests
import re
import os

output_dir = "links/tvc"
os.makedirs(output_dir, exist_ok=True)

USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.0.1;)"
REFERRER = "https://peers.tv/"

def get_token():
    url = "http://api.peers.tv/auth/2/token"
    payload = "grant_type=inetra%3Aanonymous&client_id=29783051&client_secret=b4d4eb438d760da95f0acb5bc6b5c760"
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(url, data=payload, headers=headers, timeout=8)
    if response.status_code != 200:
        return None
    return re.search(r'"access_token":"([^"]+)"', response.text).group(1)

def get_stream_url(channel, channel_id, token, offset):
    base_url = f"http://api.peers.tv/timeshift/{channel}/{channel_id}/playlist.m3u8"
    return f"{base_url}?token={token}&offset={offset}"

def save_m3u8(filename, stream_url):
    filepath = os.path.join(output_dir, filename)
    with open(filepath, "w", encoding="utf-8") as file:
        file.write("#EXTM3U\n")
        file.write("#EXT-X-VERSION:3\n")
        file.write(f"{stream_url}\n")
    print(f"Сохранил: {filepath}")

if __name__ == "__main__":
    token = get_token()
    if not token:
        print("Ошибка: не удалось получить токен.")
        exit()

    channel = "tvc"
    channel_id = 16  # базовый ID

    offsets = {
        "tvc": 0,
        "tvc_plus2": 7200,
        "tvc_plus4": 14400,
        "tvc_plus7": 50400,
    }

    for name, offset in offsets.items():
        url = get_stream_url(channel, channel_id, token, offset)
        save_m3u8(f"{name}.m3u8", url)
        print(f"{name} → {url}")
