
# ============================================================
# ZURIBOT 2000™ - LOCATION FILTER
# ============================================================

import re


def normalize_text(value):
    """
    Normaliza texto para comparar ubicaciones.
    """

    if value is None:
        return ""

    value = str(value).lower().strip()

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value


def get_location_data(job):
    """
    Extrae ubicación y modalidad del puesto.
    """

    location = job.get(
        "location",
        {}
    )

    work_type = normalize_text(
        job.get(
            "work_type",
            ""
        )
    )

    city = ""
    country = ""
    remote = False
    hybrid = False

    if isinstance(location, dict):

        city = normalize_text(
            location.get(
                "city",
                ""
            )
        )

        country = normalize_text(
            location.get(
                "country",
                ""
            )
        )

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

    else:

        city = normalize_text(
            location
        )

    # Detectar modalidad desde work_type
    if "remote" in work_type:
        remote = True

    if "hybrid" in work_type:
        hybrid = True

    # Detectar modalidad desde ciudad/location
    location_text = f"{city} {country}"

    if (
        "remote" in location_text
        or "work from home" in location_text
    ):
        remote = True

    if "hybrid" in location_text:
        hybrid = True

    if hybrid:
        work_mode = "hybrid"

    elif remote:
        work_mode = "remote"

    elif (
        "on-site" in work_type
        or "onsite" in work_type
        or "on site" in work_type
    ):
        work_mode = "on_site"

    else:
        work_mode = "on_site"

    return {
        "city": city,
        "country": country,
        "work_mode": work_mode
    }


def country_is_allowed(
    country,
    allowed_countries
):
    """
    Comprueba si el país está permitido.
    """

    country = normalize_text(
        country
    )

    allowed = [
        normalize_text(country_name)
        for country_name in allowed_countries
    ]

    if not country:
        return False

    for allowed_country in allowed:

        if (
            country == allowed_country
            or allowed_country in country
            or country in allowed_country
        ):
            return True

    return False


def is_location_allowed(
    job,
    profile
):
    """
    Aplica la política geográfica del perfil.

    Política actual de Álvaro:

    Remote:
        permitido en cualquier lugar.

    Hybrid:
        solamente países permitidos.

    On-site:
        solamente países permitidos.
    """

    policy = profile.get(
        "location_policy",
        {}
    )

    location_data = get_location_data(
        job
    )

    work_mode = location_data[
        "work_mode"
    ]

    country = location_data[
        "country"
    ]

    # ========================================================
    # REMOTE
    # ========================================================

    if work_mode == "remote":

        remote_policy = policy.get(
            "remote",
            "anywhere"
        )

        if remote_policy == "anywhere":
            return True, "Remote permitido"

        return (
            False,
            "Remote no permitido por la política del perfil"
        )

    # ========================================================
    # HYBRID
    # ========================================================

    if work_mode == "hybrid":

        allowed_countries = policy.get(
            "hybrid",
            []
        )

        if country_is_allowed(
            country,
            allowed_countries
        ):
            return (
                True,
                f"Hybrid permitido en {country}"
            )

        return (
            False,
            f"Hybrid fuera de países permitidos: {country or 'país no especificado'}"
        )

    # ========================================================
    # ON-SITE
    # ========================================================

    if work_mode == "on_site":

        allowed_countries = policy.get(
            "on_site",
            []
        )

        if country_is_allowed(
            country,
            allowed_countries
        ):
            return (
                True,
                f"On-site permitido en {country}"
            )

        return (
            False,
            f"On-site fuera de países permitidos: {country or 'país no especificado'}"
        )

    return (
        False,
        "Modalidad de trabajo no reconocida"
    )


def filter_jobs_by_location(
    jobs,
    profile
):
    """
    Devuelve únicamente los puestos
    compatibles geográficamente.
    """

    allowed_jobs = []
    rejected_jobs = []

    for job in jobs:

        allowed, reason = is_location_allowed(
            job,
            profile
        )

        if allowed:

            allowed_jobs.append(
                job
            )

        else:

            rejected_jobs.append(
                (
                    job,
                    reason
                )
            )

    return (
        allowed_jobs,
        rejected_jobs
    )


if __name__ == "__main__":

    test_profile = {
        "location_policy": {
            "remote": "anywhere",
            "hybrid": [
                "Argentina"
            ],
            "on_site": [
                "Argentina"
            ]
        }
    }

    test_jobs = [

        {
            "title": "Senior Product Designer Remote",
            "location": {
                "country": "United States",
                "city": "",
                "remote": True
            },
            "work_type": "Remote"
        },

        {
            "title": "Senior Product Designer Buenos Aires",
            "location": {
                "country": "Argentina",
                "city": "Buenos Aires",
                "remote": False
            },
            "work_type": "Hybrid"
        },

        {
            "title": "Senior Product Designer Mexico",
            "location": {
                "country": "Mexico",
                "city": "Mexico City",
                "remote": False
            },
            "work_type": "On-site"
        }
    ]

    allowed, rejected = filter_jobs_by_location(
        test_jobs,
        test_profile
    )

    print("\n==============================")
    print("LOCATION FILTER TEST")
    print("==============================")

    print(
        f"\nAllowed jobs: {len(allowed)}"
    )

    for job in allowed:

        print(
            f"  ✓ {job['title']}"
        )

    print(
        f"\nRejected jobs: {len(rejected)}"
    )

    for job, reason in rejected:

        print(
            f"  ✗ {job['title']}"
        )

        print(
            f"    Reason: {reason}"
        )

