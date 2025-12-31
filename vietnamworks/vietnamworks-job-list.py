import requests
import time
from bs4 import BeautifulSoup
import json
import csv
import os


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

def create_csv_writer():
    file_exists = os.path.isfile('vietnameworks.csv')
    
    file_path = "vietnamworks_jobs.csv"

    fieldnames = [
        "job_id",
        "job_title",
        "company",
        "location",
        "industries",
        "industries_vn",
        "function",
        "function_vn",
        "job_url",
        "job_description",
        "job_requirements",
        "benefits",
        "benefits_vn",
        "salary",
        "skills"
    ]

    file_exists = os.path.isfile(file_path)

    csv_file = open(file_path, mode="a", newline="", encoding="utf-8-sig")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    if not file_exists:
        writer.writeheader()
    return writer


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

def find_job_requirements(job_detail_html):
    soup = BeautifulSoup(job_detail_html, "lxml")

    # 1. Find the <h2> by its visible text
    h2 = soup.find("h2", string=lambda s: s and "Yêu cầu công việc" in s)

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
    
    for index, job in enumerate(response["data"]):
        job_detail = requests.post(job["jobUrl"], headers=detail_page_headers)
        job_detail_html = job_detail.text
        
        job_description = find_job_description(job_detail_html)
        job_requirements = find_job_requirements(job_detail_html)
        
        csv_writer = create_csv_writer()
        
        csv_writer.writerow({
            "job_id": job.get("jobId"),
            "job_title": job.get("jobTitle"),
            "company": job.get("companyName"),
            "location": job.get("address"),
            "industries_vn": ", ".join([industry.get("industryV3NameVI") for industry in job.get("industriesV3", []) if industry.get("industryV3NameVI")]),
            "industries": ", ".join([industry.get("industryV3Name") for industry in job.get("industriesV3", []) if industry.get("industryV3Name")]),
            "function_vn": job.get("jobFunctionsV3", {}).get("jobFunctionV3NameVI"),
            "function": job.get("jobFunctionsV3", {}).get("jobFunctionV3Name"),
            "job_url": job.get("jobUrl"),
            "job_description": job_description,
            "job_requirements": job_requirements,
            "benefits": ", ".join([benefit.get("benefitName") for benefit in job.get("benefits", []) if benefit.get("benefitName")]),
            "benefits_vn": ", ".join([benefit.get("benefitNameVI") for benefit in job.get("benefits", []) if benefit.get("benefitNameVI")]),
            "salary": job.get("prettySalary"),
            "skills": ", ".join([skill.get("skillName") for skill in job.get("skills", []) if skill.get("skillName")])
        })
        
        print(f"Page {page + 1}/{total_page} - {index + 1}/{len(response['data'])} - job {job.get('jobId')} - {job.get('jobTitle')}")

        time.sleep(delay_time)
        
    time.sleep(delay_time)
