import requests
import time
from bs4 import BeautifulSoup
import json

url = "https://ms.vietnamworks.com/job-search/v1.0/search"

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://www.vietnamworks.com",
    "Referer": "https://www.vietnamworks.com/",
}

per_page = 20

payload = {
    "query": "python",
    "filters": [],
    "ranges": [],
    "order": [],
    "page": 0,
    "limit": per_page
}

meta_response = requests.post(url, json=payload, headers=headers)

data = meta_response.json()

jobMetaData = data['meta']

total_page = jobMetaData['nbPages']

delay_time = 3  # seconds between requests


def find_job_description(job_detail_html):
    soup = BeautifulSoup(job_detail_html, "lxml")

    # 1. Find the <h2> by its visible text
    h2 = soup.find("h2", string=lambda s: s and "Mô tả công việc" in s)

    if not h2:
        return ""

    # 2. The content is in the next <div>
    content_div = h2.find_next_sibling("div")

    if not content_div:
        return ""

    # 3. Extract clean text
    text = content_div.get_text(separator="\n", strip=True)
    return text

detail_page_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

for page in range(total_page):
    response = requests.post(url, json={
        "query": "python",
        "filters": [],
        "ranges": [],
        "order": [],
        "page": page,
        "limit": per_page
    }, headers=headers).json()
    
    for job in response["data"]:
        job_detail = requests.post(job["jobUrl"], headers=detail_page_headers)
        job_detail_html = job_detail.text
        
        job_description = find_job_description(job_detail_html)
        
        print(f"job_description: {job_description}")
        
        time.sleep(delay_time)
        
    time.sleep(delay_time)
