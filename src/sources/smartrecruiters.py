import requests
import html
import re
from datetime import datetime, timezone


# ============================================================
# SMARTRECRUITERS BOARDS
# ============================================================

SMARTRECRUITERS_BOARDS = [
    {
        "identifier": "Xplor",
        "company": "Xplor"
    },
    {
        "identifier": "Cint",
        "company": "Cint"
    },
    {
        "identifier": "ServiceNow",
        "company": "ServiceNow"
    },
    {
        "identifier": "Wix2",
        "company": "Wix"
    },
    {
        "identifier": "HelloKindred",
        "company": "HelloKindred"
    }
]


# ============================================================
# HTML CLEANING
# ============================================================

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


# ============================================================
# SENIORITY
# ============================================================

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


# ============================================================
# SKILLS
# ============================================================

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


# ============================================================
# TOOLS
# ============================================================

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


# ============================================================
# GET JOB LIST
# ============================================================

def get_smartrecruiters_jobs(
    company_identifier
):

    jobs = []

    offset = 0
    limit = 100

    while True:

        url = (
            "https://api.smartrecruiters.com/v1/"
            "companies/"
            f"{company_identifier}/postings"
        )

        params = {
            "limit": limit,
            "offset": offset
        }

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        content = data.get(
            "content",
            []
        )

        jobs.extend(
            content
        )

        total_found = data.get(
            "totalFound",
            len(jobs)
        )

        if (
            not content
            or len(jobs) >= total_found
        ):
            break

        offset += limit

    return jobs


# ============================================================
# GET JOB DETAILS
# ============================================================

def get_job_details(
    company_identifier,
    posting_id
):

    url = (
        "https://api.smartrecruiters.com/v1/"
        "companies/"
        f"{company_identifier}/postings/"
        f"{posting_id}"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# DESCRIPTION EXTRACTION
# ============================================================

def extract_description(job):

    job_ad = job.get(
        "jobAd",
        {}
    )

    candidates = [
        job.get("description"),
        job_ad.get("description"),
        job_ad.get("jobDescription"),
        job_ad.get("sections")
    ]

    for candidate in candidates:

        if isinstance(
            candidate,
            str
        ):

            cleaned = clean_html(
                candidate
            )

            if cleaned:
                return cleaned

        if isinstance(
            candidate,
            dict
        ):

            parts = []

            for value in candidate.values():

                if isinstance(
                    value,
                    dict
                ):

                    text = (
                        value.get("text")
                        or value.get("content")
                        or value.get("description")
                        or ""
                    )

                    if text:
                        parts.append(
                            clean_html(text)
                        )

                elif isinstance(
                    value,
                    str
                ):

                    parts.append(
                        clean_html(value)
                    )

            if parts:
                return " ".join(parts)

        if isinstance(
            candidate,
            list
        ):

            parts = []

            for section in candidate:

                if not isinstance(
                    section,
                    dict
                ):
                    continue

                text = (
                    section.get("text")
                    or section.get("content")
                    or section.get("description")
                    or ""
                )

                if text:
                    parts.append(
                        clean_html(text)
                    )

            if parts:
                return " ".join(parts)

    return ""


# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(
    job,
    company,
    company_identifier
):

    posting_id = str(
        job.get(
            "id",
            ""
        )
    )

    title = job.get(
        "name",
        job.get(
            "title",
            ""
        )
    )

    description = extract_description(
        job
    )

    location = job.get(
        "location",
        {}
    )

    if not isinstance(
        location,
        dict
    ):
        location = {}

    city = location.get(
        "city",
        ""
    )

    country = location.get(
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

    location_text = location_name.lower()

    remote = bool(
        location.get(
            "remote",
            False
        )
    )

    hybrid = bool(
        location.get(
            "hybrid",
            False
        )
    )

    if (
        remote
        or "remote" in location_text
    ):

        remote = True
        work_type = "Remote"

    elif (
        hybrid
        or "hybrid" in location_text
    ):

        work_type = "Hybrid"

    else:

        work_type = "On-site"

    url = (
        job.get("postingUrl")
        or job.get("jobAdUrl")
        or job.get("applyUrl")
        or job.get("ref")
        or ""
    )

    published_at = (
        job.get("releasedDate")
        or job.get("postedDate")
        or ""
    )

    industry = job.get(
        "industry",
        {}
    )

    if isinstance(
        industry,
        dict
    ):

        industry = industry.get(
            "label",
            ""
        )

    else:

        industry = str(
            industry or ""
        )

    employment = job.get(
        "typeOfEmployment",
        {}
    )

    if isinstance(
        employment,
        dict
    ):

        employment = employment.get(
            "label",
            ""
        )

    else:

        employment = str(
            employment or ""
        )

    return {
        "id": posting_id,

        "title": title,

        "company": company,

        "location": {
            "country": country,
            "city": city,
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

        "industry": industry,

        "language_requirements": [],

        "employment_type": employment,

        "salary": {
            "min": None,
            "max": None,
            "currency": ""
        },

        "url": url,

        "source": "smartrecruiters",

        "published_at": published_at,

        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "source_board": company_identifier
    }


# ============================================================
# GET ALL SMARTRECRUITERS JOBS
# ============================================================

def get_all_smartrecruiters_jobs():

    all_jobs = []

    for board in SMARTRECRUITERS_BOARDS:

        company = board["company"]

        identifier = board["identifier"]

        print(
            f"\nFetching SmartRecruiters board: "
            f"{company}"
        )

        try:

            jobs = get_smartrecruiters_jobs(
                identifier
            )

            print(
                f"Jobs found at {company}: "
                f"{len(jobs)}"
            )

            for job in jobs:

                posting_id = job.get(
                    "id",
                    ""
                )

                try:

                    detailed_job = (
                        get_job_details(
                            identifier,
                            posting_id
                        )
                    )

                except Exception:

                    detailed_job = job

                normalized_job = (
                    normalize_job(
                        detailed_job,
                        company,
                        identifier
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


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    jobs = (
        get_all_smartrecruiters_jobs()
    )

    print(
        "\n=============================="
    )

    print(
        "SMARTRECRUITERS TEST"
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
