import requests
import re

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0"
}
url = "https://team-up-website-sveltekit.vercel.app/leaderboard/1023107249532571648/Pool%E5%8F%B0%E7%90%83%F0%9F%98%8B/overall_player/all"

if __name__ == "__main__":
    resp = requests.get(url=url, headers=header)  
    resp = resp.content.decode(requests.utils.get_encodings_from_content(resp.text)[0])
    rul = re.compile("<div.*?<p.*?>(?P<rank>.*?)<.*?button.*?<p>(?P<name>.*?)</p.*?<p.*?>(?P<score>.*?)</p>.*?</div>")
    with open(file="1.txt",mode="w", encoding="utf-8") as f:
        for i in re.finditer(rul, resp):\
            f.write(f"{i.group('rank'):<2} {i.group('name'):<20}              {i.group('score')}\n")
