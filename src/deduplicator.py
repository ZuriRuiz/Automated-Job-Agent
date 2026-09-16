# ============================================================
# ZURIBOT 2000™ - DEDUPLICATOR
# ============================================================

import json
import re
from pathlib import Path
from datetime import datetime, timezone


SEEN_JOBS_PATH = "data/seen_jobs.json"


# ============================================================
# BASIC UTILITIES
# ============================================================

def load_seen_jobs(path=SEEN_JOBS_PATH):
    path_obj = Path(path)

    if not path_obj.exists():
        return {}

    with path_obj.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_seen_jobs(seen_jobs, path=SEEN_JOBS_PATH):
    path_obj = Path(path)

    with path_obj.open("w", encoding="utf-8") as file:
        json.dump(
            seen_jobs,
            file,
            indent=2,
            ensure_ascii=False
        )


def normalize_text(value):
    if value is None:
        return ""

    value = str(value).lower().strip()
    value = re.sub(r"\s+", " ", value)

    return value


# ============================================================
# JOB FIELDS
# ============================================================

def normalize_title(title):
    return normalize_text(title)


def normalize_company(company):
    return normalize_text(company)


def get_location_value(job):
    location = job.get("location", {})

    if isinstance(location, dict):
        country = normalize_text(location.get("country", ""))
        city = normalize_text(location.get("city", ""))

        if country:
            return country

        if city:
            return city

        return ""

    return normalize_text(location)


def get_work_type(job):
    return normalize_text(
        job.get("work_type", "")
    )


# ============================================================
# EXACT KEY
# ============================================================

def get_exact_job_key(job):
    source = normalize_text(
        job.get("source", "unknown")
    )

    source_board = normalize_text(
        job.get("source_board", "unknown")
    )

    job_id = normalize_text(
        job.get(
            "job_id",
            job.get("id", "")
        )
    )

    url = normalize_text(
        job.get("url", "")
    )

    if job_id:
        return (
            f"{source}:"
            f"{source_board}:"
            f"id:{job_id}"
        )

    if url:
        return (
            f"{source}:"
            f"{source_board}:"
            f"url:{url}"
        )

    return ""


# ============================================================
# SEMANTIC KEY
# ============================================================

def get_semantic_job_key(job):
    company = normalize_company(
        job.get("company", "")
    )

    title = normalize_title(
        job.get("title", "")
    )

    location = get_location_value(job)

    work_type = get_work_type(job)

    return (
        f"{company}:"
        f"{title}:"
        f"{location}:"
        f"{work_type}"
    )


# ============================================================
# MASTER KEY
# ============================================================

def get_job_key(job):
    exact_key = get_exact_job_key(job)

    if exact_key:
        return exact_key

    return get_semantic_job_key(job)


# ============================================================
# COUNTRY CONSOLIDATION
# ============================================================

def get_country_from_job(job):
    location = job.get("location", {})

    if isinstance(location, dict):
        country = location.get("country", "")

        if country:
            return str(country).strip()

        city = location.get("city", "")

        if city:
            return str(city).strip()

    elif location:
        return str(location).strip()

    return ""


def consolidate_locations(jobs):
    countries = []

    for job in jobs:
        country = get_country_from_job(job)

        if not country:
            continue

        normalized = normalize_text(country)

        if normalized not in [
            normalize_text(existing)
            for existing in countries
        ]:
            countries.append(country)

    return countries


# ============================================================
# CONSOLIDATE DUPLICATE JOBS
# ============================================================

def consolidate_duplicate_jobs(jobs):
    """
    Consolidates the same job appearing multiple times
    with different country variants.

    Example:

    Same Workable ID:
        Product Designer - Argentina
        Product Designer - Brazil
        Product Designer - Mexico

    Becomes ONE job with:

        available_countries:
            Argentina
            Brazil
            Mexico
    """

    groups = {}

    for job in jobs:
        key = get_job_key(job)

        if key not in groups:
            groups[key] = []

        groups[key].append(job)

    consolidated_jobs = []

    for key, group in groups.items():

        base_job = dict(group[0])

        countries = consolidate_locations(group)

        if countries:

            location = dict(
                base_job.get("location", {})
            )

            # Argentina first when available
            countries_sorted = sorted(
                countries,
                key=lambda country: (
                    normalize_text(country) != "argentina",
                    normalize_text(country)
                )
            )

            location["country"] = countries_sorted[0]

            location["city"] = countries_sorted[0]

            base_job["location"] = location

            base_job["available_countries"] = (
                countries_sorted
            )

        consolidated_jobs.append(base_job)

    return consolidated_jobs


# ============================================================
# UNIQUE JOBS
# ============================================================

def get_unique_jobs(jobs):
    """
    First consolidates country variants,
    then returns one record per real opportunity.
    """

    return consolidate_duplicate_jobs(jobs)


# ============================================================
# NEW JOBS
# ============================================================

def get_new_jobs(jobs, seen_jobs):

    unique_jobs = get_unique_jobs(jobs)

    new_jobs = []

    for job in unique_jobs:

        job_key = get_job_key(job)

        if job_key not in seen_jobs:
            new_jobs.append(job)

    return new_jobs


# ============================================================
# MARK AS SEEN
# ============================================================

def mark_jobs_as_seen(jobs, seen_jobs):

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    for job in jobs:

        job_key = get_job_key(job)

        seen_jobs[job_key] = timestamp


# ============================================================
# DUPLICATE DIAGNOSTICS
# ============================================================

def get_duplicate_groups(jobs):

    groups = {}

    for job in jobs:

        key = get_job_key(job)

        if key not in groups:
            groups[key] = []

        groups[key].append(job)

    return {
        key: group
        for key, group in groups.items()
        if len(group) > 1
    }


def print_duplicate_diagnostics(jobs):

    duplicate_groups = get_duplicate_groups(jobs)

    duplicate_records = sum(
        len(group) - 1
        for group in duplicate_groups.values()
    )

    print("\n==============================")
    print("DEDUPLICATION DIAGNOSTICS")
    print("==============================")

    print(f"\nInput jobs: {len(jobs)}")

    print(
        f"Duplicate groups: "
        f"{len(duplicate_groups)}"
    )

    print(
        f"Duplicate records: "
        f"{duplicate_records}"
    )

    for index, (key, group) in enumerate(
        duplicate_groups.items(),
        start=1
    ):

        print(
            f"\n--- DUPLICATE GROUP {index} ---"
        )

        print(f"Key: {key}")

        for job in group:

            print(
                f"\n  Title: "
                f"{job.get('title', '')}"
            )

            print(
                f"  Company: "
                f"{job.get('company', '')}"
            )

            print(
                f"  Source: "
                f"{job.get('source', '')}"
            )

            print(
                f"  Board: "
                f"{job.get('source_board', '')}"
            )

            print(
                f"  ID: "
                f"{job.get('job_id', job.get('id', ''))}"
            )

            print(
                f"  Work type: "
                f"{job.get('work_type', '')}"
            )

            print(
                f"  Location: "
                f"{job.get('location', '')}"
            )

            print(
                f"  URL: "
                f"{job.get('url', '')}"
            )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("\n==============================")
    print("DEDUPLICATOR TEST")
    print("==============================")

    test_job_1 = {
        "id": "TEST001",
        "job_id": "TEST001",
        "title": "Senior Product Designer",
        "company": "Newsela",
        "source": "greenhouse",
        "source_board": "newsela",
        "location": {
            "country": "Argentina",
            "city": "Buenos Aires",
            "remote": True
        },
        "work_type": "Remote",
        "url": ""
    }

    test_job_2 = {
        "id": "TEST001",
        "job_id": "TEST001",
        "title": "Senior Product Designer",
        "company": "Newsela",
        "source": "greenhouse",
        "source_board": "newsela",
        "location": {
            "country": "Brazil",
            "city": "Brazil",
            "remote": True
        },
        "work_type": "Remote",
        "url": ""
    }

    jobs = [
        test_job_1,
        test_job_2
    ]

    unique_jobs = get_unique_jobs(jobs)

    print(
        f"\nInput jobs: {len(jobs)}"
    )

    print(
        f"Unique jobs: {len(unique_jobs)}"
    )

    print(
        "\nConsolidated countries:"
    )

    print(
        unique_jobs[0].get(
            "available_countries",
            []
        )
    )

    seen_jobs = {}

    new_jobs = get_new_jobs(
        jobs,
        seen_jobs
    )

    print(
        f"\nFirst check: "
        f"{len(new_jobs)} new job(s)"
    )

    mark_jobs_as_seen(
        new_jobs,
        seen_jobs
    )

    new_jobs_second_check = get_new_jobs(
        jobs,
        seen_jobs
    )

    print(
        f"Second check: "
        f"{len(new_jobs_second_check)} new job(s)"
    )

    print_duplicate_diagnostics(jobs)

    print("\nSeen jobs:")

    for key, timestamp in seen_jobs.items():
        print(
            f"- {key} → {timestamp}"
        )


