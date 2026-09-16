from sources.greenhouse import (
    get_greenhouse_jobs,
    normalize_job
)

from matcher import (
    match_job,
    load_profile
)


BOARD_TOKEN = "newsela"
COMPANY = "Newsela"
PROFILE_PATH = "profiles/alvaro.json"


profile = load_profile(
    PROFILE_PATH
)

jobs = get_greenhouse_jobs(
    BOARD_TOKEN
)


print(
    "\n=============================="
)

print(
    "GREENHOUSE JOB MATCHING TEST"
)

print(
    "=============================="
)


for job in jobs:

    normalized_job = normalize_job(
        job,
        COMPANY,
        BOARD_TOKEN
    )

    result = match_job(
        normalized_job,
        profile
    )

    print(
        "\n------------------------------"
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

    if result["excluded"]:

        print(
            "Excluded: "
            + ", ".join(
                result["excluded_items"]
            )
        )

    print(
        "\nReasons:"
    )

    for reason in result["reasons"]:

        print(
            f"- {reason}"
        )
