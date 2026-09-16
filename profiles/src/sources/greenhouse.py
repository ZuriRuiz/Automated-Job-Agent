import requests
import html
import re
from datetime import datetime, timezone


# ============================================================
# GREENHOUSE BOARDS
# ============================================================

GREENHOUSE_BOARDS = [
    {
        "token": "newsela",
        "company": "Newsela"
    },
    {
        "token": "nortal",
        "company": "Nortal"
    }
]


# ============================================================
# TEXT UTILITIES
# ============================================================

def clean_html(text):

    text = html.unescape(text or "")

    text = re.sub(r"<[^>]+>", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ============================================================
# SENIORITY DETECTION
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
# SKILL EXTRACTION
# ============================================================

def extract_skills(description):

    skill_keywords = [
        "IT Support",
        "IT Operations",
        "Troubleshooting",
        "Technical Support",
        "Customer Support",
        "Automation",
        "Scripting",
        "Security",
        "Compliance",
        "Problem Solving",
        "Communication",
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
# TOOL EXTRACTION
# ============================================================

def extract_tools(description):

    tool_keywords = [
        "Apple",
        "macOS",
        "Google Workspace",
        "Slack",
        "Atlassian",
        "1Password",
        "Kandji",
        "GAM",
        "Figma",
        "FigJam",
        "Jira",
        "Notion",
        "Miro"
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
# GET JOBS FROM ONE GREENHOUSE BOARD
# ============================================================

def get_greenhouse_jobs(board_token):

    url = (
        f"https://boards-api.greenhouse.io/v1/boards/"
        f"{board_token}/jobs?content=true"
    )

    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    return data["jobs"]


# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(job, company, board_token):

    location_name = (
        job.get("location", {})
        .get("name", "")
    )

    location_lower = location_name.lower()


    # --------------------------------------------------------
    # Detect work type
    # --------------------------------------------------------

    if "remote" in location_lower:

        work_type = "Remote"
        remote = True

    elif "hybrid" in location_lower:

        work_type = "Hybrid"
        remote = False

    else:

        work_type = "On-site"
        remote = False


    # --------------------------------------------------------
    # Clean description
    # --------------------------------------------------------

    description = clean_html(
        job.get("content", "")
    )


    # --------------------------------------------------------
    # Detect seniority
    # --------------------------------------------------------

    seniority = detect_seniority(
        job["title"],
        description
    )


    # --------------------------------------------------------
    # Extract skills and tools
    # --------------------------------------------------------

    skills = extract_skills(
        description
    )

    tools = extract_tools(
        description
    )


    # --------------------------------------------------------
    # Return normalized job
    # --------------------------------------------------------

    return {

        "id": str(job["id"]),

        "title": job["title"],

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

        "url": job["absolute_url"],

        "source": "greenhouse",

        "published_at": job.get(
            "updated_at",
            ""
        ),

        "scraped_at": datetime.now(
            timezone.utc
        ).isoformat(),

        # Extra metadata used internally
        "source_board": board_token
    }


# ============================================================
# GET JOBS FROM ALL GREENHOUSE BOARDS
# ============================================================

def get_all_greenhouse_jobs():

    all_jobs = []

    for board in GREENHOUSE_BOARDS:

        token = board["token"]
        company = board["company"]

        print(
            f"\nFetching Greenhouse board: "
            f"{company}"
        )

        jobs = get_greenhouse_jobs(
            token
        )

        print(
            f"Jobs found at {company}: "
            f"{len(jobs)}"
        )

        for job in jobs:

            normalized_job = normalize_job(
                job,
                company,
                token
            )

            all_jobs.append(
                normalized_job
            )

    return all_jobs


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    jobs = get_all_greenhouse_jobs()

    print(
        "\n=============================="
    )

    print(
        "GREENHOUSE MULTI-BOARD TEST"
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
