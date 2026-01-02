import argparse

from crawlers.jobgo.jobgo_jobs_crawler import crawl_jobgo_jobs
from crawlers.vietnamworks.vietnamworks_jobs_crawler import crawl_vietnamworks_jobs
from crawlers.topcv.topcv_jobs_crawler import crawl_topcv_jobs


def main():
    parser = argparse.ArgumentParser(
        description="Job portal crawler"
    )

    parser.add_argument(
        "site",
        choices=["vietnamworks", "jobgo", "topcv"],
        help="Which site to crawl"
    )

    args = parser.parse_args()

    if args.site == "vietnamworks":
        crawl_vietnamworks_jobs()

    elif args.site == "jobgo":
        crawl_jobgo_jobs()

    elif args.site == "topcv":
        crawl_topcv_jobs()


if __name__ == "__main__":
    main()
