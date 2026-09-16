import json
import re


MINIMUM_SCORE = 70


# ============================================================
# TEXT UTILITIES
# ============================================================

def normalize_text(text):

    if not text:
        return ""

    text = str(text).lower()

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def keyword_in_text(text, keyword):

    text = normalize_text(text)
    keyword = normalize_text(keyword)

    if not keyword:
        return False

    return re.search(
        rf"\b{re.escape(keyword)}\b",
        text
    ) is not None


# ============================================================
# EXCLUSIONS
# ============================================================

def check_exclusions(job, profile):

    title = normalize_text(
        job.get("title", "")
    )

    description = normalize_text(
        job.get("description", "")
    )

    excluded_items = []

    # Excluded roles
    for role in profile.get(
        "excluded_roles",
        []
    ):

        if keyword_in_text(
            title,
            role
        ):

            excluded_items.append(role)

    # Excluded keywords
    for keyword in profile.get(
        "excluded_keywords",
        []
    ):

        # Strongest check: title
        if keyword_in_text(
            title,
            keyword
        ):

            excluded_items.append(keyword)

        # Also check description
        elif keyword_in_text(
            description,
            keyword
        ):

            excluded_items.append(keyword)

    return excluded_items


# ============================================================
# ROLE MATCH
# ============================================================

def calculate_role_match(job, profile):

    title = normalize_text(
        job.get("title", "")
    )

    seniority_words = {
        "senior",
        "sr",
        "sr.",
        "semi-senior",
        "lead",
        "principal",
        "junior",
        "jr",
        "jr."
    }

    def role_core(text):

        words = [
            word
            for word in text.split()
            if word not in seniority_words
        ]

        return " ".join(words)

    title_core = role_core(title)

    best_match = None
    best_score = 0

    for role in profile.get(
        "target_roles",
        []
    ):

        role_normalized = normalize_text(
            role
        )

        role_core_text = role_core(
            role_normalized
        )

        if not role_core_text:
            continue

        # Exact role
        if title_core == role_core_text:

            return 35, role

        # Target role contained in title
        if role_core_text in title_core:

            if 30 > best_score:

                best_score = 30
                best_match = role

            continue

        # Partial word overlap
        role_words = set(
            role_core_text.split()
        )

        title_words = set(
            title_core.split()
        )

        if role_words:

            overlap = (
                len(
                    role_words &
                    title_words
                )
                /
                len(role_words)
            )

            if overlap >= 0.5:

                score = round(
                    overlap * 25
                )

                if score > best_score:

                    best_score = score
                    best_match = role

    return best_score, best_match


# ============================================================
# SENIORITY MATCH
# ============================================================

def calculate_seniority_match(
    job,
    profile
):

    job_seniority = normalize_text(
        job.get(
            "seniority",
            ""
        )
    )

    profile_seniorities = [
        normalize_text(level)
        for level in profile.get(
            "seniority",
            []
        )
    ]

    if not job_seniority:

        return 10, "Unknown"

    if job_seniority in profile_seniorities:

        return 15, "Match"

    return 0, "Mismatch"


# ============================================================
# SKILL MATCH
# ============================================================

def calculate_skill_match(
    job,
    profile
):

    description = normalize_text(
        job.get(
            "description",
            ""
        )
    )

    profile_skills = profile.get(
        "skills",
        []
    )

    if not profile_skills:

        return 0, []

    generic_skills = {
        "agile",
        "scrum",
        "communication",
        "problem solving",
        "data analysis",
        "cross-functional collaboration"
    }

    specific_matches = []
    generic_matches = []

    for skill in profile_skills:

        if keyword_in_text(
            description,
            skill
        ):

            if normalize_text(skill) in generic_skills:

                generic_matches.append(skill)

            else:

                specific_matches.append(skill)

    total_matches = (
        specific_matches
        +
        generic_matches
    )

    match_count = len(
        total_matches
    )

    if match_count == 0:

        score = 0

    elif len(specific_matches) == 1:

        score = 7

    elif len(specific_matches) == 2:

        score = 12

    elif len(specific_matches) >= 3:

        score = 20

    elif len(generic_matches) == 1:

        score = 2

    else:

        score = 4

    return score, total_matches


# ============================================================
# TOOL MATCH
# ============================================================

def calculate_tool_match(
    job,
    profile
):

    description = normalize_text(
        job.get(
            "description",
            ""
        )
    )

    profile_tools = profile.get(
        "tools",
        []
    )

    if not profile_tools:

        return 0, []

    matches = []

    for tool in profile_tools:

        if keyword_in_text(
            description,
            tool
        ):

            matches.append(tool)

    match_count = len(
        matches
    )

    if match_count == 0:

        score = 0

    elif match_count == 1:

        score = 5

    elif match_count == 2:

        score = 9

    else:

        score = 15

    return score, matches


# ============================================================
# WORK TYPE MATCH
# ============================================================

def calculate_work_type_match(
    job,
    profile
):

    job_work_type = normalize_text(
        job.get(
            "work_type",
            ""
        )
    )

    preferred_work_types = [
        normalize_text(work_type)
        for work_type in profile.get(
            "preferred_work_type",
            []
        )
    ]

    if not job_work_type:

        return 0, "Unknown"

    if job_work_type in preferred_work_types:

        return 5, "Match"

    return 0, "Not preferred"


# ============================================================
# LOCATION MATCH
# ============================================================

def calculate_location_match(
    job,
    profile
):

    job_location_data = job.get(
        "location",
        {}
    )

    if not isinstance(
        job_location_data,
        dict
    ):

        job_location_data = {}

    job_location = normalize_text(
        job_location_data.get(
            "city",
            ""
        )
    )

    job_remote = job_location_data.get(
        "remote",
        False
    )

    profile_location = profile.get(
        "location",
        {}
    )

    if not isinstance(
        profile_location,
        dict
    ):

        profile_location = {}

    profile_city = normalize_text(
        profile_location.get(
            "city",
            ""
        )
    )

    profile_country = normalize_text(
        profile_location.get(
            "country",
            ""
        )
    )

    if job_remote:

        return 10, "Remote"

    if (
        profile_city
        and profile_city in job_location
    ):

        return 10, "City match"

    if (
        profile_country
        and profile_country in job_location
    ):

        return 8, "Country match"

    return 0, "Location mismatch"


# ============================================================
# MAIN MATCH FUNCTION
# ============================================================

def match_job(
    job,
    profile
):

    reasons = []

    excluded_items = check_exclusions(
        job,
        profile
    )

    # ========================================================
    # EXCLUDED JOB
    # ========================================================

    if excluded_items:

        return {
            **job,

            "job_id": job.get(
                "id",
                ""
            ),

            "score": 0,

            "match_level":
                "Excluded",

            "excluded": True,

            "excluded_items":
                excluded_items,

            "reasons": [
                f"Excluded: {item}"
                for item in excluded_items
            ]
        }

    # ========================================================
    # CALCULATE COMPONENTS
    # ========================================================

    role_score, matched_role = (
        calculate_role_match(
            job,
            profile
        )
    )

    seniority_score, seniority_result = (
        calculate_seniority_match(
            job,
            profile
        )
    )

    skill_score, matched_skills = (
        calculate_skill_match(
            job,
            profile
        )
    )

    tool_score, matched_tools = (
        calculate_tool_match(
            job,
            profile
        )
    )

    work_type_score, work_type_result = (
        calculate_work_type_match(
            job,
            profile
        )
    )

    location_score, location_result = (
        calculate_location_match(
            job,
            profile
        )
    )

    # ========================================================
    # RELEVANCE GATE
    # ========================================================

    if role_score == 0:

        score = min(
            30,
            seniority_score
            + skill_score
            + tool_score
            + work_type_score
            + location_score
        )

        match_level = "❌ Low"

        reasons.append(
            "Role relevance: No target-role match"
        )

    else:

        score = (
            role_score
            + seniority_score
            + skill_score
            + tool_score
            + work_type_score
            + location_score
        )

        score = max(
            0,
            min(
                100,
                score
            )
        )

        if score >= 85:

            match_level = "🔥 Excellent"

        elif score >= 70:

            match_level = "🟡 Good"

        else:

            match_level = "❌ Low"

    # ========================================================
    # REASONS
    # ========================================================

    if matched_role:

        reasons.append(
            f"Role match: {matched_role}"
        )

    if seniority_result == "Match":

        reasons.append(
            "Seniority match: "
            + job.get(
                "seniority",
                ""
            )
        )

    elif seniority_result == "Unknown":

        reasons.append(
            "Seniority not specified"
        )

    if matched_skills:

        reasons.append(
            "Matching skills: "
            + ", ".join(
                matched_skills
            )
        )

    if matched_tools:

        reasons.append(
            "Matching tools: "
            + ", ".join(
                matched_tools
            )
        )

    if work_type_result == "Match":

        reasons.append(
            "Work type: "
            + job.get(
                "work_type",
                ""
            )
        )

    if location_result in [
        "Remote",
        "City match",
        "Country match"
    ]:

        reasons.append(
            "Location compatible: "
            + location_result
        )

    # ========================================================
    # RETURN ORIGINAL JOB + MATCH DATA
    # ========================================================
    #
    # IMPORTANT:
    # We preserve ALL original job fields:
    #
    # id
    # url
    # source
    # source_board
    # location
    # work_type
    # seniority
    # description
    # etc.
    #
    # Then we add/update the matcher information.
    #

    return {
        **job,

        "job_id": job.get(
            "id",
            ""
        ),

        "score": score,

        "match_level":
            match_level,

        "excluded": False,

        "excluded_items": [],

        "reasons": reasons
    }


# ============================================================
# LOAD PROFILE
# ============================================================

def load_profile(
    profile_path
):

    with open(
        profile_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    profile = load_profile(
        "profiles/alvaro.json"
    )

    test_job = {

        "id":
            "TEST001",

        "title":
            "Senior Product Designer",

        "company":
            "Example Company",

        "location": {

            "country":
                "Argentina",

            "city":
                "Buenos Aires",

            "remote":
                True
        },

        "work_type":
            "Remote",

        "seniority":
            "Senior",

        "description": (

            "We are looking for a "
            "Senior Product Designer "
            "with experience in UX Strategy, "
            "Product Design, User Research, "
            "Figma and Design Systems."
        ),

        "skills": [],

        "tools": [],

        "url":
            "https://example.com/test",

        "source":
            "test",

        "source_board":
            "test-board"
    }

    result = match_job(
        test_job,
        profile
    )

    print(
        "\n=============================="
    )

    print(
        "JOB MATCH RESULT"
    )

    print(
        "=============================="
    )

    print(
        f"Job: {result['title']}"
    )

    print(
        f"Company: {result['company']}"
    )

    print(
        f"Score: {result['score']}/100"
    )

    print(
        f"Match: {result['match_level']}"
    )

    print(
        "\nImportant preserved fields:"
    )

    print(
        f"ID: {result.get('id')}"
    )

    print(
        f"URL: {result.get('url')}"
    )

    print(
        f"Source: {result.get('source')}"
    )

    print(
        f"Source board: "
        f"{result.get('source_board')}"
    )

    print(
        f"Work type: "
        f"{result.get('work_type')}"
    )

    print(
        "\nReasons:"
    )

    for reason in result["reasons"]:

        print(
            f"- {reason}"
        )
