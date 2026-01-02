import json
import os


def load_urls(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return {}

    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_urls(file_path: str, data: dict):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def append_url(file_path: str, source: str, url: str):
    data = load_urls(file_path)

    if source not in data:
        data[source] = []

    if url not in data[source]:
        data[source].append(url)

    save_urls(file_path, data)
