from utils.csv_writer import create_csv_writer
import requests
import time
import json
from bs4 import BeautifulSoup

headers = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Origin": "https://www.vietnamworks.com",
    "Referer": "https://www.vietnamworks.com/",
}

URL = "https://ms.vietnamworks.com/job-search/v1.0/search"
PER_PAGE = 20
PAGE_START = 133
DELAY_TIME_IN_S = 4


def create_payload(page=0):
    return {
        "userId": 0,
        "query": "",
        "filter": [],
        "ranges": [],
        "order": [],
        "hitsPerPage": PER_PAGE,
        "page": page,
        "retrieveFields": [
            "address", "benefits", "jobTitle", "salaryMax", "isSalaryVisible", "jobLevelVI", "isShowLogo", "salaryMin", "companyLogo", "userId", "jobLevel", "jobLevelId", "jobId", "jobUrl", "companyId", "approvedOn", "isAnonymous", "alias", "expiredOn", "industries", "industriesV3",
            "workingLocations", "services", "companyName", "salary", "onlineOn", "simpleServices", "visibilityDisplay", "isShowLogoInSearch", "priorityOrder", "skills", "profilePublishedSiteMask", "jobDescription", "jobRequirement", "prettySalary", "requiredCoverLetter", "languageSelectedVI", "languageSelected", "languageSelectedId", "typeWorkingId", "createdOn", "isAdrLiteJob"
        ],
        "summaryVersion": ""
    }


meta_response = requests.post(URL, json=create_payload(), headers=headers)

data = meta_response.json()

jobMetaData = data['meta']

total_page = jobMetaData['nbPages']


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


def join_data(data, field):
    try:
        return ", ".join([item.get(field) for item in data if item.get(field)])
    except Exception:
        return ""


csv_writer = create_csv_writer("./crawling_results/vietnamworks_jobs.csv")


def crawl_vietnamworks_jobs():
    print(f"Job Metadata: {jobMetaData}")

    for page in range(PAGE_START, total_page):
        response = requests.post(
            URL, json=create_payload(page), headers=headers).json()

        for index, job in enumerate(response["data"]):
            try:

                job_detail = requests.post(
                    job["jobUrl"], headers=detail_page_headers)
                job_detail_html = job_detail.text

                job_description = find_job_description(job_detail_html)
                job_requirements = find_job_requirements(job_detail_html)
            except Exception as e:
                print(f"Error processing job {job.get('jobId')}: {e}")
                continue

            csv_writer.writerow({
                "job_id": job.get("jobId"),
                "job_title": job.get("jobTitle"),
                "company": job.get("companyName"),
                "location": job.get("address"),
                "industries_vn": join_data(job.get("industriesV3", []), "industryV3NameVI"),
                "industries": join_data(job.get("industriesV3", []), "industryV3Name"),
                "job_level": job.get("jobLevel"),
                "job_level_vn": job.get("jobLevelVI"),
                "job_url": job.get("jobUrl"),
                "job_description": job_description,
                "job_requirements": job_requirements,
                "benefits": join_data(job.get("benefits", []), "benefitName"),
                "benefits_vn": join_data(job.get("benefits", []), "benefitNameVI"),
                "salary": job.get("prettySalary"),
                "skills": join_data(job.get("skills", []), "skillName"),
                "upload_date": job.get("onlineOn")
            })

            print(
                f"Page {page + 1}/{total_page} - {index + 1}/{len(response['data'])} - job {job.get('jobId')} - {job.get('jobTitle')}")

            time.sleep(DELAY_TIME_IN_S)

        time.sleep(DELAY_TIME_IN_S)
