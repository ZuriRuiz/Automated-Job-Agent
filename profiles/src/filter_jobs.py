# ============================================================
# ZURIBOT 2000™ - FINAL JOB FILTER
# ============================================================

import json
import os
from pathlib import Path

from sources.greenhouse import get_all_greenhouse_jobs
from sources.lever import get_all_lever_jobs
from sources.ashby import get_all_ashby_jobs
from sources.workable import get_all_workable_jobs
from sources.smartrecruiters import get_all_smartrecruiters_jobs
from sources.recruitee import get_all_recruitee_jobs
from sources.linkedin import get_all_linkedin_jobs

from matcher import match_job

from location_filter import (
    filter_jobs_by_location
)

from deduplicator import (
    load_seen_jobs,
    get_unique_jobs,
    get_new_jobs,
    mark_jobs_as_seen,
    save_seen_jobs,
    print_duplicate_diagnostics
)

from email_builder import build_jobs_email
from email_sender import send_email


PROFILE_PATH = "profiles/alvaro.json"


# ============================================================
# LOAD PROFILE
# ============================================================

def load_profile(path=PROFILE_PATH):

    path_obj = Path(path)

    with path_obj.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# GET EMAIL RECIPIENTS
# ============================================================

def get_email_recipients(profile):

    recipients = [

        profile.get(
            "email",
            ""
        ),

        os.environ.get(
            "EMAIL_MONITOR",
            ""
        )

    ]

    recipients = [

        email.strip()

        for email in recipients

        if email.strip()

    ]

    return recipients


# ============================================================
# SEND EMAIL TO ALL RECIPIENTS
# ============================================================

def send_email_to_recipients(
    recipients,
    subject,
    body
):

    for recipient in recipients:

        print(
            f"\nSending email to: {recipient}"
        )

        send_email(
            recipient,
            subject,
            body
        )


# ============================================================
# MAIN
# ============================================================

def main():

    print(
        "\n=============================="
    )

    print(
        "ZURIBOT 2000™"
    )

    print(
        "FINAL JOB FILTER"
    )

    print(
        "=============================="
    )


    # ========================================================
    # INITIAL SEND MODE
    # ========================================================

    initial_send = (

        os.environ.get(
            "INITIAL_SEND",
            "false"
        ).lower()

        == "true"

    )


    if initial_send:

        print(
            "\nMODE: INITIAL REAL SEND"
        )

    else:

        print(
            "\nMODE: NORMAL"
        )


    # ========================================================
    # LOAD PROFILE
    # ========================================================

    profile = load_profile()


    # ========================================================
    # EMAIL RECIPIENTS
    # ========================================================

    recipients = get_email_recipients(
        profile
    )


    if not recipients:

        print(
            "\nERROR: No email recipients configured."
        )

        return


    print(
        "\nEmail recipients:"
    )

    for recipient in recipients:

        print(
            f"- {recipient}"
        )


    # ========================================================
    # COLLECT ALL JOBS
    # ========================================================

    all_jobs = []


    # --------------------------------------------------------
    # GREENHOUSE
    # --------------------------------------------------------

    greenhouse_jobs = (
        get_all_greenhouse_jobs()
    )

    print(
        f"\nGreenhouse jobs: "
        f"{len(greenhouse_jobs)}"
    )

    all_jobs.extend(
        greenhouse_jobs
    )


    # --------------------------------------------------------
    # LEVER
    # --------------------------------------------------------

    lever_jobs = (
        get_all_lever_jobs()
    )

    print(
        f"Lever jobs: "
        f"{len(lever_jobs)}"
    )

    all_jobs.extend(
        lever_jobs
    )


    # --------------------------------------------------------
    # ASHBY
    # --------------------------------------------------------

    ashby_jobs = (
        get_all_ashby_jobs()
    )

    print(
        f"Ashby jobs: "
        f"{len(ashby_jobs)}"
    )

    all_jobs.extend(
        ashby_jobs
    )


    # --------------------------------------------------------
    # WORKABLE
    # --------------------------------------------------------

    workable_jobs = (
        get_all_workable_jobs()
    )

    print(
        f"Workable jobs: "
        f"{len(workable_jobs)}"
    )

    all_jobs.extend(
        workable_jobs
    )


    # --------------------------------------------------------
    # SMARTRECRUITERS
    # --------------------------------------------------------

    smartrecruiters_jobs = (
        get_all_smartrecruiters_jobs()
    )

    print(
        f"SmartRecruiters jobs: "
        f"{len(smartrecruiters_jobs)}"
    )

    all_jobs.extend(
        smartrecruiters_jobs
    )


    # --------------------------------------------------------
    # RECRUITEE
    # --------------------------------------------------------

    recruitee_jobs = (
        get_all_recruitee_jobs()
    )

    print(
        f"Recruitee jobs: "
        f"{len(recruitee_jobs)}"
    )

    all_jobs.extend(
        recruitee_jobs
    )


    # --------------------------------------------------------
    # LINKEDIN
    # --------------------------------------------------------

    linkedin_jobs = (
        get_all_linkedin_jobs()
    )

    print(
        f"LinkedIn jobs: "
        f"{len(linkedin_jobs)}"
    )

    all_jobs.extend(
        linkedin_jobs
    )


    # ========================================================
    # TOTAL JOBS
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        f"Total jobs: {len(all_jobs)}"
    )

    print(
        "=============================="
    )


    # ========================================================
    # MATCHING
    # ========================================================

    matching_jobs = []

    minimum_score = profile.get(
        "minimum_match_score",
        70
    )


    for job in all_jobs:

        result = match_job(
            job,
            profile
        )


        if result.get(
            "excluded",
            False
        ):

            continue


        if result.get(
            "score",
            0
        ) < minimum_score:

            continue


        matching_jobs.append(
            result
        )


    print(
        f"\nMatching jobs: "
        f"{len(matching_jobs)}"
    )


    # ========================================================
    # LOCATION FILTER
    # ========================================================

    (
        location_jobs,
        rejected_location_jobs
    ) = filter_jobs_by_location(
        matching_jobs,
        profile
    )


    print(
        f"Location-compatible jobs: "
        f"{len(location_jobs)}"
    )


    print(
        f"Rejected by location: "
        f"{len(rejected_location_jobs)}"
    )


    # ========================================================
    # DUPLICATE DIAGNOSTICS
    # ========================================================

    print_duplicate_diagnostics(
        location_jobs
    )


    # ========================================================
    # UNIQUE JOBS
    # ========================================================

    unique_jobs = get_unique_jobs(
        location_jobs
    )


    print(
        f"\nUnique matching jobs: "
        f"{len(unique_jobs)}"
    )


    # ========================================================
    # LOAD SEEN JOBS
    # ========================================================

    seen_jobs = load_seen_jobs()


    print(
        f"Previously seen: "
        f"{len(seen_jobs)}"
    )


    # ========================================================
    # DETERMINE JOBS TO EMAIL
    # ========================================================

    if initial_send:

        jobs_to_email = unique_jobs


        print(
            f"\nINITIAL SEND: "
            f"{len(jobs_to_email)} "
            f"opportunities will be emailed."
        )

    else:

        jobs_to_email = get_new_jobs(
            unique_jobs,
            seen_jobs
        )


        print(
            f"\nNew matching jobs: "
            f"{len(jobs_to_email)}"
        )


    # ========================================================
    # NO NEW OPPORTUNITIES
    # ========================================================

    if not jobs_to_email:

        print(
            "\nNo new opportunities."
        )


        email = build_jobs_email(
            []
        )


        try:

            send_email_to_recipients(
                recipients,
                email["subject"],
                email["body"]
            )


            print(
                "\nNo-new-opportunities "
                "emails sent successfully."
            )


        except Exception as error:

            print(
                "\nError sending email:"
            )

            print(
                error
            )


        print(
            "\n=============================="
        )

        print(
            "FINISHED"
        )

        print(
            "=============================="
        )

        return


    # ========================================================
    # BUILD REAL JOB EMAIL
    # ========================================================

    email = build_jobs_email(
        jobs_to_email
    )


    subject = email[
        "subject"
    ]

    body = email[
        "body"
    ]


    # ========================================================
    # SEND REAL EMAIL
    # ========================================================

    print(
        "\nSending real job email..."
    )


    print(
        f"Recipients: "
        f"{len(recipients)}"
    )


    print(
        f"Opportunities in email: "
        f"{len(jobs_to_email)}"
    )


    try:

        send_email_to_recipients(
            recipients,
            subject,
            body
        )


        print(
            "\nAll emails sent successfully."
        )


    except Exception as error:

        print(
            "\nError sending email:"
        )

        print(
            error
        )


        print(
            "\nJobs will NOT be marked as seen."
        )


        return


    # ========================================================
    # MARK AS SEEN
    # ========================================================

    mark_jobs_as_seen(
        jobs_to_email,
        seen_jobs
    )


    save_seen_jobs(
        seen_jobs
    )


    print(
        f"\nMarked as seen: "
        f"{len(jobs_to_email)}"
    )


    # ========================================================
    # FINISHED
    # ========================================================

    print(
        "\n=============================="
    )

    print(
        "FINISHED"
    )

    print(
        "=============================="
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    main()
