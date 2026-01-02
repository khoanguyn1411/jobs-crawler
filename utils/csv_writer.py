import os
import csv


def create_csv_writer(csv_file_path):
    file_exists = os.path.isfile(csv_file_path)

    file_path = csv_file_path

    fieldnames = [
        "job_id",
        "job_title",
        "company",
        "location",
        "industries",
        "industries_vn",
        "job_level_vn",
        "job_level",
        "job_url",
        "job_description",
        "job_requirements",
        "benefits",
        "benefits_vn",
        "salary",
        "skills",
        "upload_date"
    ]

    file_exists = os.path.isfile(file_path)
    os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)

    csv_file = open(file_path, mode="a", newline="", encoding="utf-8-sig")
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

    if not file_exists:
        writer.writeheader()
    return writer
