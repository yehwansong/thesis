#!/usr/bin/env python3
"""
Downloads 100 sun images from Wikimedia Commons into ./sun_images/
Requirements: pip install requests
"""

import os
import time
import requests

SAVE_DIR = "sun_images"
os.makedirs(SAVE_DIR, exist_ok=True)

QUERIES = [
    "sun", "solar flare", "sunspot", "solar eclipse", "sun corona",
    "solar prominence", "solar disk", "sun chromosphere", "NASA sun",
    "sun photosphere", "solar wind", "coronal mass ejection",
    "sun ultraviolet", "solar granulation", "sun X-ray",
    "heliostat", "solar observation", "sun hydrogen alpha",
    "solar active region", "sun infrared"
]

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "SunImageCollector/1.0 (educational use)"})

def search_wikimedia(query, limit=5):
    """Search Wikimedia Commons for image titles."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": 6,
        "srlimit": limit,
        "format": "json"
    }
    r = SESSION.get(url, params=params, timeout=10)
    r.raise_for_status()
    return [item["title"] for item in r.json().get("query", {}).get("search", [])]

def get_image_url(title):
    """Get direct image URL from a File: title."""
    url = "https://en.wikipedia.org/w/api.php"
    params = {
        "action": "query",
        "titles": title,
        "prop": "imageinfo",
        "iiprop": "url",
        "iiurlwidth": 1000,
        "format": "json"
    }
    r = SESSION.get(url, params=params, timeout=10)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", {})
    info = list(pages.values())[0].get("imageinfo", [{}])[0]
    return info.get("thumburl") or info.get("url")

def download(url, path):
    r = SESSION.get(url, timeout=20, stream=True)
    r.raise_for_status()
    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

def main():
    collected = set()
    count = 0
    target = 100

    for query in QUERIES:
        if count >= target:
            break
        print(f"[{count}/{target}] Searching: {query}")
        try:
            titles = search_wikimedia(query, limit=6)
        except Exception as e:
            print(f"  Search failed: {e}")
            continue

        for title in titles:
            if count >= target:
                break
            if title in collected:
                continue
            collected.add(title)

            try:
                img_url = get_image_url(title)
                if not img_url:
                    continue
                ext = img_url.split("?")[0].rsplit(".", 1)[-1].lower()
                if ext not in ("jpg", "jpeg", "png", "gif"):
                    continue

                filename = f"{count+1:03d}_{title.replace('File:','').replace('/','_')[:60]}.{ext}"
                filepath = os.path.join(SAVE_DIR, filename)

                download(img_url, filepath)
                size_kb = os.path.getsize(filepath) // 1024
                print(f"  [{count+1}] {filename} ({size_kb} KB)")
                count += 1
                time.sleep(0.3)  # be polite to the API

            except Exception as e:
                print(f"  Failed {title}: {e}")

    print(f"\nDone. {count} images saved to ./{SAVE_DIR}/")

if __name__ == "__main__":
    main()
