from bs4 import BeautifulSoup
import requests
import re
import math
import time
from crawlers.utils.csv_writer import create_csv_writer
from crawlers.utils.url_store import append_url
import random

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/121.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8",


}

BASE_URL = "https://www.topcv.vn/tim-viec-lam-moi-nhat"
TIME_SLEEP_IN_S = random.uniform(6, 9)
PAGE_START = 1
TOTAL_PAGE = 578


def extract_jobs(page=1):
    url = f"{BASE_URL}?page={page}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    job_tags = soup.select("div.job-ta")
    return {
        "per_page": len(job_tags),
        "jobs": job_tags
    }


def get_job_detail_url(job_tag):
    job_url = job_tag.select_one("a").get("href")
    return job_url


def extract_text_by_label(job_detail_html, label, reference_tag="h3", reference_tag_class=None, value_selector="div"):
    soup = BeautifulSoup(job_detail_html, "lxml")

    # 1. Find the <h3> by its visible text
    reference_tag = soup.find(
        reference_tag,
        class_=reference_tag_class if reference_tag else None,
        string=lambda s: s and label in s)

    if not reference_tag:
        return ""

    # 2. The content is in the next <div>
    content_div = reference_tag.parent.select_one(value_selector)

    if not content_div:
        return ""

    # 3. Extract clean text
    text = content_div.get_text(separator="\n", strip=True)

    return text


def get_industries(job_detail_html):
    soup = BeautifulSoup(job_detail_html, "lxml")
    industries_vn = ""
    for group in soup.select("div.job-tags__group"):
        name_el = group.select_one("div.job-tags__group-name")
        if not name_el:
            continue

        if name_el.get_text(strip=True).rstrip(":") == "Chuyên môn":
            tags = [
                a.get_text(strip=True)
                for a in group.select("div.job-tags__group-list-tag a.item")
            ]
            industries_vn = ", ".join(tags)
            break
    return industries_vn


def extract_id(url: str) -> str:
    match = re.search(r"([j]?\d+)\.html", url)
    if not match:
        return ""

    job_id = match.group(1)
    return job_id.lstrip("j")


def get_skills(job_detail_html):
    soup = BeautifulSoup(job_detail_html, "lxml")

    # 1. Find the title by text
    title = soup.find(
        "div",
        class_="box-title",
        string=lambda s: s and s.strip() == "Kỹ năng cần có"
    )

    if not title:
        return ""

    # 2. Go up to the container box
    box = title.find_parent("div", class_="box-category")
    if not box:
        return ""

    # 3. Extract all skill tags inside this box
    skills = [
        span.get_text(strip=True)
        for span in box.select("div.box-category-tags span.box-category-tag")
    ]

    return ", ".join(skills)


def extract_job_detail(job_url):
    response = requests.get(job_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')

    job_id = extract_id(job_url)

    job_title = soup.select_one(
        "h1.job-detail__info--title ").get_text(strip=True)

    company = soup.select_one(
        "div.company-name-label").select_one("a").get_text(strip=True)

    location = extract_text_by_label(
        job_detail_html=response.content, label="Địa điểm", reference_tag="div", reference_tag_class="job-detail__info--section-content-title", value_selector="a")

    industries_vn = get_industries(response.content)
    job_level_vn = extract_text_by_label(
        job_detail_html=response.content, label="Cấp bậc", reference_tag="div", reference_tag_class="box-general-group-info-title", value_selector="div.box-general-group-info-value")

    job_description = extract_text_by_label(
        job_detail_html=response.content, label="Mô tả công việc", reference_tag="h3", value_selector="div")

    job_requirements = extract_text_by_label(
        job_detail_html=response.content, label="Yêu cầu ứng viên", reference_tag="h3", value_selector="div")

    benefits_vn = extract_text_by_label(
        job_detail_html=response.content, label="Quyền lợi", reference_tag="h3", value_selector="div")

    salary = extract_text_by_label(
        job_detail_html=response.content, label="Mức lương", reference_tag="div", reference_tag_class="job-detail__info--section-content-title", value_selector="div.box-general-group-info-value")

    skills = get_skills(response.content)

    return {
        "job_id": job_id,
        "job_title": job_title,
        "job_url": job_url,
        "company": company,
        "location": location,
        "industries_vn": industries_vn,
        "job_level_vn": job_level_vn,
        "job_description": job_description,
        "job_requirements": job_requirements,
        "benefits_vn": benefits_vn,
        "salary": salary,
        "skills": skills,
    }


writer = create_csv_writer("./crawling_results/topcv_jobs.csv")


def crawl_topcv_jobs():
    meta_data = extract_jobs()
    per_page = meta_data.get("per_page")
    for page in range(PAGE_START, TOTAL_PAGE):
        try:
            job_page_data = extract_jobs(page)
            jobs = job_page_data.get("jobs")
            for index, job_tag in enumerate(jobs):
                try:
                    job_detail_url = get_job_detail_url(job_tag)
                    job_detail = extract_job_detail(job_detail_url)
                    data_to_write = {
                        "job_id": job_detail.get("job_id"),
                        "job_title": job_detail.get("job_title"),
                        "company": job_detail.get("company"),
                        "salary": job_detail.get("salary"),
                        "location": job_detail.get("location"),
                        "job_url": job_detail.get("job_url"),
                        "job_description": job_detail.get("job_description", ""),
                        "job_requirements": job_detail.get("job_requirements", ""),
                        "benefits_vn": job_detail.get("benefits_vn", ""),
                        "industries_vn": job_detail.get("industries_vn", ""),
                        "job_level_vn": job_detail.get("job_level_vn", ""),
                        "skills": job_detail.get("skills", ""),
                    }

                    writer.writerow(data_to_write)
                    print(
                        f"Page {page}/{TOTAL_PAGE} - {index + 1}/{len(jobs)} - job {job_detail.get('job_id')} - {job_detail.get('job_title')}")
                    time.sleep(TIME_SLEEP_IN_S)

                except Exception as e:
                    print(
                        f"Error processing job {job_detail_url}, skipping and store to .json file")
                    append_url(file_path="./crawling_results/topcv_brand_jobs.json",
                               source="topcv_brand_urls", url=job_detail_url)
                    time.sleep(TIME_SLEEP_IN_S)
                    continue

            time.sleep(TIME_SLEEP_IN_S)

        except Exception as e:
            print(f"Error processing page {page + 1}: {e}")
            time.sleep(TIME_SLEEP_IN_S)
            continue
