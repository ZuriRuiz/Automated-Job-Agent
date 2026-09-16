import requests
import html
import re
from datetime import datetime, timezone


ASHBY_BOARDS = [
    {
        "slug": "Skydropx",
        "company": "Skydropx"
    },
    {
        "slug": "tempo",
        "company": "Tempo"
    },
    {
        "slug": "maintainx",
        "company": "MaintainX"
    },
    {
        "slug": "glacier",
        "company": "Glacier"
    },
    {
        "slug": "demandbase",
        "company": "Demandbase"
    },
    {
        "slug": "synthesia",
        "company": "Synthesia"
    },
    {
        "slug": "iceye",
        "company": "ICEYE"
    },
    {
        "slug": "coram-ai",
        "company": "Coram AI"
    },
    {
        "slug": "Ashby",
        "company": "Ashby"
    },
    {
        "slug": "Scale%20Army%20Careers",
        "company": "Scale Army"
    }
]


def clean_html(text):
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def detect_seniority(title, description):
    title_lower = title.lower()

    if "lead" in title_lower:
        return "Lead"

    if "principal" in title_lower:
        return "Principal"

    if (
        "senior" in title_lower
        or "sr." in title_lower
        or "sr " in title_lower
    ):
        return "Senior"

    if (
        "mid-level" in title_lower
        or "mid level" in title_lower
    ):
        return "Mid"

    if (
        "junior" in title_lower
        or "jr." in title_lower
        or "jr " in title_lower
    ):
        return "Junior"

    description_lower = description.lower()

    if (
        "senior-level" in description_lower
        or "senior level" in description_lower
    ):
        return "Senior"

    if (
        "mid-level" in description_lower
        or "mid level" in description_lower
    ):
        return "Mid"

    if (
        "junior-level" in description_lower
        or "junior level" in description_lower
    ):
        return "Junior"

    return ""


def extract_skills(description):
    skill_keywords = [
        "UX Strategy",
        "Product Design",
        "User Research",
        "Usability Testing",
        "Wireframing",
        "Prototyping",
        "Design Systems",
        "Information Architecture",
        "Journey Mapping",
        "Accessibility",
        "A/B Testing",
        "Data Analysis",
        "Interaction Design",
        "Agile",
        "Scrum"
    ]

    description_lower = description.lower()

    return [
        skill
        for skill in skill_keywords
        if skill.lower() in description_lower
    ]


def extract_tools(description):
    tool_keywords = [
        "Figma",
        "FigJam",
        "Whimsical",
        "Framer",
        "Hotjar",
        "Maze",
        "Useberry",
        "Miro",
        "Jira",
        "Notion",
        "Claude"
    ]

    description_lower = description.lower()

    return [
        tool
        for tool in tool_keywords
        if tool.lower() in description_lower
    ]


def get_ashby_jobs(board):
    url = (
        "https://api.ashbyhq.com/posting-api/"
        f"job-board/{board}"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data.get(
        "jobs",
        []
    )


def normalize_job(
    job,
    company,
    board
):
    title = job.get(
        "title",
        ""
    )

    description = clean_html(
        job.get(
            "descriptionHtml",
            job.get(
                "description",
                ""
            )
        )
    )

    location_name = job.get(
        "location",
        ""
    )

    if isinstance(
        location_name,
        dict
    ):
        location_name = location_name.get(
            "name",
            ""
        )

    location_lower = str(
        location_name
    ).lower()

    if "remote" in location_lower:
        work_type = "Remote"
        remote = True

    elif "hybrid" in location_lower:
        work_type = "Hybrid"
        remote = False

    else:
        work_type = "On-site"
        remote = False

    job_url = job.get(
        "jobUrl",
        ""
    )

    return {
        "id": str(
            job_url
            or job.get(
                "id",
                ""
            )
        ),
        "title": title,
        "company": company,
        "location": {
            "country": "",
            "city": location_name,
            "remote": remote
        },
        "work_type": work_type,
        "seniority": detect_seniority(
            title,
            description
        ),
        "description": description,
        "requirements": [],
        "skills": extract_skills(
            description
        ),
        "tools": extract_tools(
            description
        ),
        "industry": "",
        "language_requirements": [],
        "employment_type": "",
        "salary": {
            "min": None,
            "max": None,
            "currency": ""
        },
        "url": job_url,
        "source": "ashby",
        "published_at": "",
        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source_board": board
    }


def get_all_ashby_jobs():

    all_jobs = []

    for board in ASHBY_BOARDS:

        company = board["company"]
        slug = board["slug"]

        print(
            f"\nFetching Ashby board: "
            f"{company}"
        )

        try:

            jobs = get_ashby_jobs(
                slug
            )

            print(
                f"Jobs found at {company}: "
                f"{len(jobs)}"
            )

            for job in jobs:

                normalized_job = normalize_job(
                    job,
                    company,
                    slug
                )

                all_jobs.append(
                    normalized_job
                )

        except Exception as error:

            print(
                f"WARNING: Could not fetch "
                f"{company}: {error}"
            )

    return all_jobs


if __name__ == "__main__":

    jobs = get_all_ashby_jobs()

    print("\n==============================")
    print("ASHBY TEST")
    print("==============================")

    print(
        f"\nTotal jobs: {len(jobs)}"
    )

    for job in jobs:

        print(
            f"\n{job['company']} | "
            f"{job['title']}"
        )
