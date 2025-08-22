import os

TOKEN = os.getenv("PEERS_TOKEN")
if not TOKEN:
    raise ValueError("Ошибка: токен не найден. Установи PEERS_TOKEN в GitHub Secrets.")

CHANNEL_NAME = "tvc"
CHANNEL_ID = 16

# Сдвиги (в секундах): 0, +2 часа, +4 часа, +7 часов
OFFSETS = {
    "tvc": 10,              # без сдвига (10 секунд для старта)
    "tvc_plus2": 2 * 3600,  # +2 часа
    "tvc_plus4": 4 * 3600,  # +4 часа
    "tvc_plus7": 7 * 3600,  # +7 часов
}

def build_url(channel_name, channel_id, offset=0):
    return f"http://api.peers.tv/timeshift/{channel_name}/{channel_id}/playlist.m3u8?token={TOKEN}&offset={offset}"

def save_m3u8(filename, url):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write("#EXT-X-VERSION:3\n")
        f.write("#EXT-X-STREAM-INF:PROGRAM-ID=1\n")
        f.write(url + "\n")

def main():
    for name, offset in OFFSETS.items():
        url = build_url(CHANNEL_NAME, CHANNEL_ID, offset)
        save_m3u8(f"{name}.m3u8", url)
        print(f"Сгенерирован {name}.m3u8 → {url}")

if __name__ == "__main__":
    main()
