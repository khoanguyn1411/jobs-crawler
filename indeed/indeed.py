from bs4 import BeautifulSoup
import requests
import re
import math
import time
from utils.csv_writer import create_csv_writer


headers = {"User-Agent": "Mozilla/5.0"}

FULL_TIME_URL = "https://vn.indeed.com/jobs?q=full+time&l=&fromage=last&from=searchOnDesktopSerp%2CrelatedQueries&cf-turnstile-response=0._Bsgb8NrCAdT8TLXm8ajeFOB1lvGSZH91sm_5FZqGRCqipUEJ93lKndmpaUkQkt-pKQ2Vg6t4fbpeKX3ep6xSOiPuHdiXfrq-n8ckhz8N915fLf4uyFBx0BDYWKX5CCw0tkq1FW7MXsZ904nGkAIHBnBKjEOrKqRB9rbvxoFKeuNxg6hJmCFOxzz_zmTlXltiwE_bVxdf6GpomYPr_SOtLcQ4zaiT63y-U2xExYcRYH622HqyPyN6WoMlbK7JYdWt-7DqC2HG_DulkbW70JfcSk6w4UqcRA5wsOQXAJqOvNAcbPQbIlJxQHtzzjutbiDHAJRNBZzNbzDTqyQkSlX2JNvYI4vAuYdilstEEz9TQ7rnkGSys7eOXuaI18754ccAYNYJ1HUH2DFAvbz6Zp9GiGQF-vn_4duAS9jzm-gEclmJZQdkcCrKgtX92KTkbITnwx0UlZai27FvDPDFG09FFmTKObzmlL1X2GLt25PqbJmF_EPy19yFKlSqP-hmXAbKHfVokrvVG1_pgIbUrlDwd8QuB9dpGpxXdxWRThmR9bqc67WPUEVCtL_aJJA4nuqKOP_xGHD1aKWjvfhDpP9z6NL_DqrxZGZKCvCv3v7y1sGMc_jWlbWde714YNbDfRo2GHYPAEl9WEt42NprsGUM5Xyud95lZpHvjv87fSWBOboM33yqptchV4bOK7Q3Jmpe4-m-EhuWZgY-q1J831XyiQiSbQyVQulsgurmJ2DmCigeBn9wWZGWpE6_gh3gnCMNx6tcd2UtZtcirdR8fXwo4weHl1uNE6xBoAUq55If5s-tAeZS8ZgE-EYz6D8gBWxcvfDIIwxVXdswVDJoVmZMn96P2O5InQF4aAcZzJCOpqhR-KV6iAvl0Ww5hGGWsSgJzaO1RDDCUBYGQ6nPYu2d47oGmwb_FGNputuhLcC7tY.rtA2o6xtuKbWhace-i5xig.4639ecb50807f58114f6add4e1bc3be36cb8af246fa958d2525061c17580b06c&vjk=2d8910e035548c50"
TIME_SLEEP_IN_S = 2
PAGE_START = 424


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


def crawl_indeed_jobs():
    meta_data_job = get_job_meta_data()
    total_page = meta_data_job["total_page"]
    pass
