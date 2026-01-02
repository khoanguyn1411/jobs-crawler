import argparse

from jobgo.jobgo_jobs_crawler import crawl_jobgo_jobs
from vietnamworks.vietnamworks_jobs_crawler import crawl_vietnamworks_jobs
from indeed.indeed_jobs_crawler import crawl_indeed_jobs


def main():
    parser = argparse.ArgumentParser(
        description="Job portal crawler"
    )

    parser.add_argument(
        "site",
        choices=["vietnamworks", "jobgo", "indeed", "all"],
        help="Which site to crawl"
    )

    args = parser.parse_args()

    if args.site == "vietnamworks":
        crawl_vietnamworks_jobs()

    elif args.site == "jobgo":
        crawl_jobgo_jobs()

    elif args.site == "indeed":
        crawl_indeed_jobs()

    elif args.site == "all":
        crawl_vietnamworks_jobs()
        crawl_jobgo_jobs()
        crawl_indeed_jobs()


if __name__ == "__main__":
    main()
