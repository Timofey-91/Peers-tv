import requests
import re
import os

OUTPUT_DIR = "links/tvc"
os.makedirs(OUTPUT_DIR, exist_ok=True)

USER_AGENT = "Dalvik/2.1.0 (Linux; U; Android 8.0.1;)"
REFERRER = "https://peers.tv/"

CHANNELS = {
    "tvc": {"id": 16, "offset": 0},
    "tvc_plus2": {"id": 16, "offset": 7200},
    "tvc_plus4": {"id": 16, "offset": 14400},
    "tvc_plus7": {"id": 16, "offset": 25200 + 10800},  # +1 час для Владивостока
}

def get_token():
    url = "http://api.peers.tv/auth/2/token"
    payload = "grant_type=inetra%3Aanonymous&client_id=29783051&client_secret=b4d4eb438d760da95f0acb5bc6b5c760"
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/x-www-form-urlencoded"}
    r = requests.post(url, data=payload, headers=headers, timeout=8)
    r.raise_for_status()
    return re.search(r'"access_token":"([^"]+)"', r.text).group(1)

def save_m3u8(name, url):
    path = os.path.join(OUTPUT_DIR, f"{name}.m3u8")
    r = requests.get(url, headers={"User-Agent": USER_AGENT, "Referer": REFERRER}, timeout=10)
    with open(path, "wb") as f:
        f.write(r.content)
    print(f"Saved {name}.m3u8")

if __name__ == "__main__":
    token = get_token()
    for name, ch in CHANNELS.items():
        url = f"http://api.peers.tv/timeshift/tvc/{ch['id']}/playlist.m3u8?token={token}&offset={ch['offset']}"
        save_m3u8(name, url)
