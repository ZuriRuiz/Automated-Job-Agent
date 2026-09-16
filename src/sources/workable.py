import requests
import html
import re
from datetime import datetime, timezone


WORKABLE_BOARDS = [
    {
        "slug": "pavago",
        "company": "Pavago"
    },
    {
        "slug": "huzzle",
        "company": "Huzzle"
    },
    {
        "slug": "gsstech-group",
        "company": "GSS Tech"
    },
    {
        "slug": "workana-premium",
        "company": "Workana"
    },
    {
        "slug": "robusta",
        "company": "Robusta"
    },
    {
        "slug": "flatgigs",
        "company": "FlatGigs"
    },
    {
        "slug": "european-dynamics",
        "company": "European Dynamics"
    },
    {
        "slug": "virtuhire",
        "company": "Virtuhire"
    },
    {
        "slug": "eupry-aps",
        "company": "Eupry"
    },
    {
        "slug": "seeq",
        "company": "Seeq"
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


def get_workable_jobs(slug):

    urls = [

        (
            "https://apply.workable.com/api/v1/widget/"
            f"accounts/{slug}?details=true"
        ),

        (
            "https://www.workable.com/api/accounts/"
            f"{slug}?details=true"
        )
    ]

    last_error = None

    for url in urls:

        try:

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
                    "jobs",
                    data.get(
                        "results",
                        []
                    )
                )

            if isinstance(
                data,
                list
            ):
                return data

        except requests.RequestException as error:

            last_error = error

    raise last_error


def normalize_job(
    job,
    company,
    slug
):

    title = job.get(
        "title",
        job.get(
            "name",
            ""
        )
    )

    description = clean_html(
        job.get(
            "description",
            job.get(
                "description_html",
                job.get(
                    "descriptionPlain",
                    ""
                )
            )
        )
    )

    city = job.get(
        "city",
        ""
    )

    state = job.get(
        "state",
        ""
    )

    country = job.get(
        "country",
        ""
    )

    location_parts = [
        value
        for value in [
            city,
            state,
            country
        ]
        if value
    ]

    location_name = ", ".join(
        location_parts
    )

    remote = bool(
        job.get(
            "telecommuting",
            False
        )
    )

    workplace_type = str(
        job.get(
            "workplace_type",
            ""
        )
    ).lower()

    if (
        remote
        or "remote" in workplace_type
    ):

        work_type = "Remote"
        remote = True

    elif "hybrid" in workplace_type:

        work_type = "Hybrid"

    else:

        work_type = "On-site"

    job_id = job.get(
        "shortcode",
        job.get(
            "id",
            job.get(
                "shortlink",
                ""
            )
        )
    )

    url = job.get(
        "url",
        job.get(
            "shortlink",
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

        "source": "workable",

        "published_at": job.get(
            "created_at",
            ""
        ),

        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "source_board": slug
    }


def get_all_workable_jobs():

    all_jobs = []

    for board in WORKABLE_BOARDS:

        company = board["company"]
        slug = board["slug"]

        print(
            f"\nFetching Workable board: "
            f"{company}"
        )

        try:

            jobs = get_workable_jobs(
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

    jobs = get_all_workable_jobs()

    print("\n==============================")
    print("WORKABLE TEST")
    print("==============================")

    print(
        f"\nTotal jobs: {len(jobs)}"
    )

    for job in jobs:

        print(
            f"\n{job['company']} | "
            f"{job['title']}"
        )
