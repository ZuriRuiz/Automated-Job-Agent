import requests
import html
import re
from datetime import datetime, timezone


RECRUITEE_BOARDS = [
    {
        "subdomain": "lenskartcareers",
        "company": "Lenskart"
    },
    {
        "subdomain": "skycellag",
        "company": "SkyCell"
    },
    {
        "subdomain": "aikidosecurity",
        "company": "Aikido Security"
    },
    {
        "subdomain": "miaplaza",
        "company": "Miaplaza"
    },
    {
        "subdomain": "aptitudesoftware1",
        "company": "Aptitude Software"
    }
]


def clean_html(text):

    text = html.unescape(
        text or ""
    )

    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def detect_seniority(
    title,
    description
):

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
        if skill.lower()
        in description_lower
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
        if tool.lower()
        in description_lower
    ]


def get_recruitee_jobs(
    subdomain
):

    url = (
        f"https://{subdomain}.recruitee.com/"
        "api/offers/"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if isinstance(
        data,
        dict
    ):

        return data.get(
            "offers",
            data.get(
                "jobs",
                []
            )
        )

    if isinstance(
        data,
        list
    ):

        return data

    return []


def normalize_job(
    job,
    company,
    subdomain
):

    title = job.get(
        "title",
        ""
    )

    description = clean_html(
        job.get(
            "description",
            job.get(
                "description_html",
                ""
            )
        )
    )

    city = job.get(
        "city",
        ""
    )

    country = job.get(
        "country",
        ""
    )

    location_name = ", ".join(
        value
        for value in [
            city,
            country
        ]
        if value
    )

    remote = bool(
        job.get(
            "remote",
            False
        )
    )

    hybrid = bool(
        job.get(
            "hybrid",
            False
        )
    )

    if remote:

        work_type = "Remote"

    elif hybrid:

        work_type = "Hybrid"

    else:

        work_type = "On-site"

    job_id = job.get(
        "id",
        job.get(
            "slug",
            ""
        )
    )

    url = (
        job.get(
            "careers_url",
            ""
        )
        or job.get(
            "url",
            ""
        )
    )

    return {

        "id": str(job_id),

        "title": title,

        "company": company,

        "location": {
            "country": country,
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

        "url": url,

        "source": "recruitee",

        "published_at": "",

        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "source_board": subdomain
    }


def get_all_recruitee_jobs():

    all_jobs = []

    for board in RECRUITEE_BOARDS:

        company = board["company"]
        subdomain = board["subdomain"]

        print(
            "\nFetching Recruitee board: "
            f"{company}"
        )

        try:

            jobs = get_recruitee_jobs(
                subdomain
            )

            print(
                f"Jobs found at {company}: "
                f"{len(jobs)}"
            )

            for job in jobs:

                normalized_job = (
                    normalize_job(
                        job,
                        company,
                        subdomain
                    )
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

    jobs = get_all_recruitee_jobs()

    print(
        "\n=============================="
    )

    print(
        "RECRUITEE TEST"
    )

    print(
        "=============================="
    )

    print(
        f"\nTotal jobs: {len(jobs)}"
    )

    for job in jobs:

        print(
            f"\n{job['company']} | "
            f"{job['title']}"
        )
