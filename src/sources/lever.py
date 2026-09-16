import requests
import html
import re
from datetime import datetime, timezone


# ============================================================
# LEVER BOARDS
# ============================================================

LEVER_BOARDS = [
    {
        "slug": "RyzLabs",
        "company": "RYZ Labs"
    },
    {
        "slug": "yuno",
        "company": "Yuno"
    },
    {
        "slug": "tryjeeves",
        "company": "Jeeves"
    }
]

# ============================================================
# CLEAN HTML
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

    found_skills = []

    for skill in skill_keywords:

        if skill.lower() in description_lower:
            found_skills.append(
                skill
            )

    return found_skills


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

    found_tools = []

    for tool in tool_keywords:

        if tool.lower() in description_lower:
            found_tools.append(
                tool
            )

    return found_tools


# ============================================================
# GET LEVER JOBS
# ============================================================

def get_lever_jobs(company_slug):

    url = (
        f"https://api.lever.co/v0/postings/"
        f"{company_slug}?mode=json"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(
    job,
    company,
    company_slug
):

    description = clean_html(
        job.get(
            "descriptionPlain",
            job.get(
                "description",
                ""
            )
        )
    )

    title = job.get(
        "text",
        ""
    )

    categories = job.get(
        "categories",
        {}
    )

    location_name = categories.get(
        "location",
        ""
    )

    location_lower = location_name.lower()

    if "remote" in location_lower:

        work_type = "Remote"
        remote = True

    elif "hybrid" in location_lower:

        work_type = "Hybrid"
        remote = False

    else:

        work_type = "On-site"
        remote = False

    seniority = detect_seniority(
        title,
        description
    )

    skills = extract_skills(
        description
    )

    tools = extract_tools(
        description
    )

    return {
        "id": str(
            job.get(
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

        "seniority": seniority,

        "description": description,

        "requirements": [],

        "skills": skills,

        "tools": tools,

        "industry": "",

        "language_requirements": [],

        "employment_type": "",

        "salary": {
            "min": None,
            "max": None,
            "currency": ""
        },

        "url": job.get(
            "hostedUrl",
            ""
        ),

        "source": "lever",

        "published_at": "",

        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "source_board": company_slug
    }


# ============================================================
# GET ALL LEVER JOBS
# ============================================================

def get_all_lever_jobs():

    all_jobs = []

    for board in LEVER_BOARDS:

        company_slug = board["slug"]
        company = board["company"]

        print(
            f"\nFetching Lever board: {company}"
        )

        jobs = get_lever_jobs(
            company_slug
        )

        print(
            f"Jobs found at {company}: "
            f"{len(jobs)}"
        )

        for job in jobs:

            normalized_job = normalize_job(
                job,
                company,
                company_slug
            )

            all_jobs.append(
                normalized_job
            )

    return all_jobs


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    jobs = get_all_lever_jobs()

    print(
        "\n=============================="
    )

    print(
        "LEVER TEST"
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
