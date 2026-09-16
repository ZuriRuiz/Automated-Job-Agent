# ============================================================
# ZURIBOT 2000™ - EMAIL BUILDER
# ============================================================


# ============================================================
# WORK TYPE
# ============================================================

def get_work_type(job):

    work_type = job.get(
        "work_type",
        ""
    )

    if work_type:
        return work_type

    location = job.get(
        "location",
        {}
    )

    if isinstance(location, dict):

        remote = location.get(
            "remote",
            False
        )

        if remote:
            return "Remote"

        return "On-site"

    return "No especificada"


# ============================================================
# LOCATION
# ============================================================

def get_location(job):

    location = job.get(
        "location",
        {}
    )

    if isinstance(location, dict):

        city = location.get(
            "city",
            ""
        )

        if city:
            return city

        country = location.get(
            "country",
            ""
        )

        if country:
            return country

    elif location:

        return str(location)

    return "No especificada"


# ============================================================
# JOB SECTION
# ============================================================

def build_job_section(
    job,
    number
):

    title = job.get(
        "title",
        "Puesto no especificado"
    )

    company = job.get(
        "company",
        "Empresa no especificada"
    )

    score = job.get(
        "score",
        0
    )

    match_level = job.get(
        "match_level",
        "❌ Low"
    )

    url = job.get(
        "url",
        ""
    )

    work_type = get_work_type(
        job
    )

    location = get_location(
        job
    )

    reasons = job.get(
        "reasons",
        []
    )

    section = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#{number} — {match_level} — {score}/100
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Puesto:
{title}

Empresa:
{company}

Modalidad:
{work_type}

Ubicación:
{location}
"""

    if reasons:

        section += """
¿Por qué coincide?
"""

        for reason in reasons:

            section += (
                f"\n• {reason}"
            )

    section += """

Postulación:
"""

    if url:

        section += (
            f"{url}\n"
        )

    else:

        section += (
            "URL no disponible.\n"
        )

    return section


# ============================================================
# BUILD EMAIL
# ============================================================

def build_jobs_email(jobs):

    # ========================================================
    # NO NEW OPPORTUNITIES
    # ========================================================

    if not jobs:

        return {

            "subject":
                "🤖 ZuriBot 2000™ — "
                "No hay nuevas oportunidades",

            "body":
                """Hola Menors <3,

ZuriBot revisó las oportunidades disponibles en esta ejecución y no encontró nuevas ofertas que coincidan con tu perfil desde la última búsqueda.

No hay nuevas oportunidades para enviar en este momento.

ZuriBot volverá a revisar automáticamente en la próxima ejecución. 
Vamos que se puede. 💪❤️"""
        }


    # ========================================================
    # SORT JOBS BY SCORE
    # ========================================================

    sorted_jobs = sorted(
        jobs,
        key=lambda job: job.get(
            "score",
            0
        ),
        reverse=True
    )


    # ========================================================
    # CLASSIFY MATCHES
    # ========================================================

    excellent_jobs = [

        job

        for job in sorted_jobs

        if job.get(
            "score",
            0
        ) >= 85

    ]


    good_jobs = [

        job

        for job in sorted_jobs

        if 70 <= job.get(
            "score",
            0
        ) < 85

    ]


    # ========================================================
    # SUMMARY
    # ========================================================

    total_jobs = len(
        sorted_jobs
    )


    subject = (

        "🤖 ZuriBot 2000™ — "

        f"{total_jobs} nuevas oportunidades"

    )


    body = f"""
Hola Menors,

ZuriBot 2000™ encontró nuevas oportunidades
laborales que coinciden con tu perfil.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 RESUMEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Total de oportunidades nuevas:
{total_jobs}

🔥 Excellent matches:
{len(excellent_jobs)}

🟡 Good matches:
{len(good_jobs)}

Las oportunidades están ordenadas
por nivel de coincidencia.

"""


    # ========================================================
    # EXCELLENT MATCHES
    # ========================================================

    if excellent_jobs:

        body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔥 EXCELLENT MATCHES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        for index, job in enumerate(
            excellent_jobs,
            start=1
        ):

            body += build_job_section(
                job,
                index
            )


    # ========================================================
    # GOOD MATCHES
    # ========================================================

    if good_jobs:

        body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🟡 GOOD MATCHES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        start_number = (
            len(excellent_jobs) + 1
        )

        for index, job in enumerate(
            good_jobs,
            start=start_number
        ):

            body += build_job_section(
                job,
                index
            )


    # ========================================================
    # FOOTER
    # ========================================================

    body += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Este aviso fue generado automáticamente
por ZuriBot 2000™ 🤖

No es necesario esperar otro correo:
todas las oportunidades encontradas
en esta ejecución están incluidas arriba.

Vamos que se puede. 💪❤️

Atentamente,
Zuri ❤️
"""


    return {

        "subject": subject,

        "body": body.strip()

    }


# ============================================================
# LOCAL TEST
# ============================================================

if __name__ == "__main__":

    test_jobs = [

        {
            "title":
                "Senior Product Designer",

            "company":
                "Yuno",

            "score":
                94,

            "match_level":
                "🔥 Excellent",

            "work_type":
                "Remote",

            "location": {
                "city":
                    "Buenos Aires",

                "remote":
                    True
            },

            "url":
                "https://example.com/yuno",

            "reasons": [

                "Role match: Senior Product Designer",

                "Seniority match: Senior",

                "Matching skills: Product Design, User Research",

                "Matching tools: Figma"

            ]
        },


        {

            "title":
                "Product Designer",

            "company":
                "Pavago",

            "score":
                82,

            "match_level":
                "🟡 Good",

            "work_type":
                "Remote",

            "location": {
                "city":
                    "Argentina",

                "remote":
                    True
            },

            "url":
                "https://example.com/pavago",

            "reasons": [

                "Role match: Product Designer",

                "Matching skills: Product Design",

                "Matching tools: Figma"

            ]
        }

    ]


    email = build_jobs_email(
        test_jobs
    )


    print(
        "\n=============================="
    )

    print(
        "EMAIL BUILDER TEST"
    )

    print(
        "=============================="
    )


    print(
        "\nSubject:"
    )

    print(
        email["subject"]
    )


    print(
        "\nBody:"
    )

    print(
        email["body"]
    )
