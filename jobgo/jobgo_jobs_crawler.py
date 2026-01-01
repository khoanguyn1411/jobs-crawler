from bs4 import BeautifulSoup
import requests
import re
import math
import time
from utils.csv_writer import create_csv_writer

headers = {"User-Agent": "Mozilla/5.0"}

BASE_URL = "https://jobsgo.vn/viec-lam.html"

TIME_SLEEP_IN_S = 3


def extract_text_by_label(job_detail_html, label, reference_tag="h3", value_tag="div"):
    soup = BeautifulSoup(job_detail_html, "lxml")

    # 1. Find the <h3> by its visible text
    reference_tag = soup.find(reference_tag, string=lambda s: s and label in s)

    if not reference_tag:
        return ""

    # 2. The content is in the next <div>
    content_div = reference_tag.find_next_sibling(value_tag)

    if not content_div:
        return ""

    # 3. Extract clean text
    text = content_div.get_text(separator="\n", strip=True)
    return text


def extract_job_detail(job_url):
    try:
        response = requests.get(job_url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')

        job_description = extract_text_by_label(
            response.content, "Mô tả công việc:")

        job_requirements = extract_text_by_label(
            response.content, "Yêu cầu công việc:")

        benefits_vn = extract_text_by_label(
            response.content, "Quyền lợi được hưởng:")

        job_level_vn = extract_text_by_label(
            response.content, "Cấp bậc:", "span", "strong")

        upload_date = extract_text_by_label(
            response.content, "Ngày đăng tuyển:", "span", "strong")

        # Find industries
        industries_text = None
        industries_label = soup.find(
            "div", class_="text-muted", string="Ngành nghề:")

        if industries_label:
            container = industries_label.parent
            strong = container.find("strong")

            if strong:
                industries = [
                    a.get_text(strip=True)
                    for a in strong.find_all("a")
                ]
                industries_text = ", ".join(industries)

        return {"job_description": job_description,
                "job_requirements": job_requirements,
                "benefits_vn": benefits_vn,
                "job_level_vn": job_level_vn,
                "industries_vn": industries_text,
                "upload_date": upload_date}

    except Exception as e:
        print(f"Error extracting detail for {job_url}: {e}")
        return {}


def get_job_meta_data():
    response = requests.get(BASE_URL, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    total_jobs = soup.find(
        "h1", string=lambda s: s and "việc làm mới nhất năm" in s).text
    match = re.search(r"\d+", total_jobs)
    total_jobs = int(match.group()) if match else 0

    job_tags = soup.select("div.job-card")  # example selector

    per_page = len(job_tags)

    total_page = math.ceil(total_jobs / per_page)

    return {"total_jobs": total_jobs, "total_page": total_page, "per_page": per_page}


def extract_id(url: str) -> str:
    match = re.search(r"-(\d+)\.html$", url)
    return match.group(1) if match else ""


def extract_job_data(page=1):
    if page == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?page={page}"

    response = requests.get(url, headers=headers)

    soup = BeautifulSoup(response.content, 'html.parser')

    job_tags = soup.select("div.job-card")  # example selector
    jobs = []

    total_jobs = soup.find(
        "h1", string=lambda s: s and "việc làm mới nhất năm" in s).text
    match = re.search(r"\d+", total_jobs)
    total_jobs = int(match.group()) if match else 0

    for job in job_tags:
        title = job.select_one("h3.job-title").get_text(strip=True)
        company = job.select_one("div.company-title").get_text(strip=True)

        salary = job.select_one(
            "div.mt-1.text-primary.fw-semibold.small span"
        )
        salary = salary.get_text(strip=True) if salary else None

        location = job.select_one(
            "div.mt-1.text-primary.fw-semibold.small span:nth-of-type(3)"
        )

        location = location.get_text(strip=True) if location else None

        job_url = job.find("a", href=True)
        job_url = job_url["href"] if job_url else None

        jobs.append({
            "job_title": title,
            "company": company,
            "salary": salary,
            "location": location,
            "job_url": job_url
        })

    return {"jobs": jobs, "total_per_page": len(jobs)}


writer = create_csv_writer("jobgo_jobs.csv")

PAGE_START = 69


def crawl_jobgo_jobs():
    meta_data_job = get_job_meta_data()
    total_page = meta_data_job["total_page"]

    for page in range(PAGE_START, total_page):
        try:
            jobs = extract_job_data(page + 1).get("jobs", [])
            for index, job in enumerate(jobs, start=1):
                job_detail = extract_job_detail(job.get("job_url"))
                job_id = extract_id(job.get("job_url"))
                data_to_write = {
                    "job_id": job_id,
                    "job_title": job.get("job_title"),
                    "company": job.get("company"),
                    "salary": job.get("salary"),
                    "location": job.get("location"),
                    "job_url": job.get("job_url"),
                    "job_description": job_detail.get("job_description", ""),
                    "job_requirements": job_detail.get("job_requirements", ""),
                    "benefits_vn": job_detail.get("benefits_vn", ""),
                    "industries_vn": job_detail.get("industries_vn", ""),
                    "job_level_vn": job_detail.get("job_level_vn", ""),
                    "upload_date": job_detail.get("upload_date")
                }

                writer.writerow(data_to_write)
                print(
                    f"Page {page + 1}/{total_page} - {index}/{len(jobs)} - job {job_id} - {job.get('job_title')}")

                time.sleep(TIME_SLEEP_IN_S)

        except Exception as e:
            print(f"Error processing page {page + 1}: {e}")
            continue
        time.sleep(TIME_SLEEP_IN_S)
