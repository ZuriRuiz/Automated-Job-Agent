# ============================================================
# ZURIBOT 2000™ - LINKEDIN PUBLIC JOB SOURCE
# ============================================================

import json
import re
from datetime import datetime
from html import unescape
from urllib.parse import (
    quote,
    unquote,
    unquote_plus,
    urljoin
)

import requests


# ============================================================
# CONFIGURATION
# ============================================================

SEARCH_TERMS = [
    "Senior Product Designer",
    "Senior UX Designer",
    "Senior UX Product Designer",
    "Product Designer",
    "Senior UX UI Designer",
    "UX Lead",
    "Product Design Lead"
]

LOCATION = "Argentina"

BASE_URL = "https://www.linkedin.com"

SEARCH_URL = (
    "https://www.linkedin.com/jobs/search/"
    "?keywords={keyword}"
    "&location={location}"
)

DETAIL_TIMEOUT = 20

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/153.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": (
        "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,*/*;q=0.8"
    ),
}


# ============================================================
# TEXT UTILITIES
# ============================================================

def clean_text(text):

    if not text:
        return ""

    text = unescape(str(text))

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


def decode_url_text(text):

    if not text:
        return ""

    try:
        text = unquote_plus(
            unquote(
                str(text)
            )
        )
    except Exception:
        pass

    return clean_text(text)


# ============================================================
# SENIORITY
# ============================================================

def detect_seniority(title):

    title = clean_text(
        title
    ).lower()

    if not title:
        return ""

    if re.search(
        r"\bprincipal\b",
        title
    ):
        return "Principal"

    if re.search(
        r"\bstaff\b",
        title
    ):
        return "Staff"

    if re.search(
        r"\blead\b",
        title
    ):
        return "Lead"

    if re.search(
        r"\bsenior\b|\bsr\.?\b",
        title
    ):
        return "Senior"

    if re.search(
        r"\bmid[- ]senior\b",
        title
    ):
        return "Senior"

    if re.search(
        r"\bsemi[- ]senior\b",
        title
    ):
        return "Semi-Senior"

    if re.search(
        r"\bjunior\b|\bjr\.?\b",
        title
    ):
        return "Junior"

    if re.search(
        r"\bintern\b|\binternship\b",
        title
    ):
        return "Intern"

    return ""


# ============================================================
# SKILLS
# ============================================================

def extract_skills(text):

    text = clean_text(
        text
    ).lower()

    skill_map = {
        "UX Strategy": [
            "ux strategy"
        ],
        "Product Design": [
            "product design",
            "product designer"
        ],
        "User Research": [
            "user research",
            "user interviews"
        ],
        "Usability Testing": [
            "usability testing",
            "usability test"
        ],
        "Wireframing": [
            "wireframing",
            "wireframes"
        ],
        "Prototyping": [
            "prototyping",
            "prototypes"
        ],
        "Design Systems": [
            "design system",
            "design systems"
        ],
        "Information Architecture": [
            "information architecture"
        ],
        "Journey Mapping": [
            "journey mapping",
            "customer journey"
        ],
        "Accessibility": [
            "accessibility",
            "accessible design"
        ],
        "A/B Testing": [
            "a/b testing",
            "ab testing",
            "a/b test"
        ],
        "Data Analysis": [
            "data analysis",
            "product analytics"
        ],
        "Interaction Design": [
            "interaction design"
        ],
        "Agile": [
            "agile"
        ],
        "Scrum": [
            "scrum"
        ],
        "Cross-functional Collaboration": [
            "cross-functional",
            "cross functional"
        ],
        "AI in Design": [
            "ai in design",
            "ai design",
            "artificial intelligence"
        ]
    }

    found = []

    for skill, keywords in skill_map.items():

        for keyword in keywords:

            if keyword in text:

                found.append(
                    skill
                )

                break

    return found


# ============================================================
# TOOLS
# ============================================================

def extract_tools(text):

    text = clean_text(
        text
    ).lower()

    tool_map = {
        "Figma": [
            "figma"
        ],
        "FigJam": [
            "figjam"
        ],
        "Whimsical": [
            "whimsical"
        ],
        "Framer": [
            "framer"
        ],
        "Hotjar": [
            "hotjar"
        ],
        "Maze": [
            "maze"
        ],
        "Useberry": [
            "useberry"
        ],
        "Miro": [
            "miro"
        ],
        "Jira": [
            "jira"
        ],
        "Notion": [
            "notion"
        ],
        "Claude": [
            "claude"
        ]
    }

    found = []

    for tool, keywords in tool_map.items():

        for keyword in keywords:

            if keyword in text:

                found.append(
                    tool
                )

                break

    return found


# ============================================================
# WORK TYPE
# ============================================================

def detect_work_type(text):

    text = clean_text(
        text
    ).lower()

    remote_patterns = [
        "remote",
        "work from home",
        "work remotely",
        "fully remote",
        "remote position",
        "remote role"
    ]

    hybrid_patterns = [
        "hybrid",
        "flexible hybrid",
        "hybrid work"
    ]

    onsite_patterns = [
        "on-site",
        "onsite",
        "on site",
        "in-office",
        "in office"
    ]

    for pattern in remote_patterns:

        if pattern in text:

            return "Remote", True

    for pattern in hybrid_patterns:

        if pattern in text:

            return "Hybrid", False

    for pattern in onsite_patterns:

        if pattern in text:

            return "On-site", False

    return "", False


# ============================================================
# LINKEDIN URL
# ============================================================

def normalize_linkedin_url(url):

    if not url:
        return ""

    url = url.strip()

    if url.startswith("/"):

        url = urljoin(
            BASE_URL,
            url
        )

    url = url.split("?")[0]

    return url


def extract_job_id(url):

    if not url:
        return ""

    match = re.search(
        r"/jobs/view/[^/?]+-(\d{7,})",
        url
    )

    if match:

        return match.group(1)

    match = re.search(
        r"currentJobId=(\d+)",
        url
    )

    if match:

        return match.group(1)

    return ""


# ============================================================
# URL TITLE / COMPANY EXTRACTION
# ============================================================

def extract_title_from_url(url):

    if not url:
        return ""

    match = re.search(
        r"/jobs/view/([^/?]+)-\d{7,}",
        url
    )

    if not match:
        return ""

    raw_slug = match.group(1)

    raw_slug = decode_url_text(
        raw_slug
    )

    parts = re.split(
        r"-at-",
        raw_slug,
        flags=re.IGNORECASE
    )

    raw_title = parts[0]

    raw_title = raw_title.replace(
        "-",
        " "
    )

    return clean_text(
        raw_title
    )


def extract_company_from_url(url):

    if not url:
        return ""

    match = re.search(
        r"/jobs/view/([^/?]+)-\d{7,}",
        url
    )

    if not match:
        return ""

    raw_slug = match.group(1)

    raw_slug = decode_url_text(
        raw_slug
    )

    parts = re.split(
        r"-at-",
        raw_slug,
        flags=re.IGNORECASE
    )

    if len(parts) < 2:
        return ""

    company = parts[-1]

    company = company.replace(
        "-",
        " "
    )

    return clean_text(
        company
    )


# ============================================================
# SEARCH LINKEDIN
# ============================================================

def search_linkedin_jobs(
    keyword,
    location=LOCATION
):

    encoded_keyword = quote(
        keyword
    )

    encoded_location = quote(
        location
    )

    url = SEARCH_URL.format(
        keyword=encoded_keyword,
        location=encoded_location
    )

    print(
        f"\nSearching LinkedIn: "
        f"{keyword} | {location}"
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=20
        )

        response.raise_for_status()

        return response.text

    except Exception as error:

        print(
            f"LinkedIn search failed: "
            f"{keyword} | {error}"
        )

        return ""


# ============================================================
# LINK EXTRACTION
# ============================================================

def extract_linkedin_links(html_text):

    if not html_text:
        return []

    patterns = [
        r'href="([^"]*?/jobs/view/[^"]+)"',
        r'href="([^"]*?linkedin\.com/jobs/view/[^"]+)"',
        r'"url":"([^"]*?/jobs/view/[^"]+)"'
    ]

    links = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            html_text,
            flags=re.IGNORECASE
        )

        for link in matches:

            link = unescape(
                link
            )

            link = normalize_linkedin_url(
                link
            )

            if (
                "/jobs/view/"
                in link
            ):

                links.append(
                    link
                )

    return list(
        dict.fromkeys(
            links
        )
    )


# ============================================================
# TITLE FROM URL
# ============================================================

def extract_title_from_url_fallback(url):

    title = extract_title_from_url(
        url
    )

    if title:
        return title

    return ""


# ============================================================
# JOB CARDS
# ============================================================

def extract_job_cards(html_text):

    if not html_text:
        return []

    cards = []

    pattern = re.compile(
        r'<div[^>]+class="[^"]*base-search-card[^"]*"[^>]*>'
        r'(.*?)'
        r'</div>\s*</div>',
        flags=re.IGNORECASE | re.DOTALL
    )

    matches = pattern.findall(
        html_text
    )

    for card_html in matches:

        link_match = re.search(
            r'href="([^"]*?/jobs/view/[^"]+)"',
            card_html,
            flags=re.IGNORECASE
        )

        if not link_match:
            continue

        url = normalize_linkedin_url(
            unescape(
                link_match.group(1)
            )
        )

        title = ""

        title_match = re.search(
            r'class="[^"]*base-search-card__title[^"]*"[^>]*>'
            r'(.*?)'
            r'</',
            card_html,
            flags=re.IGNORECASE | re.DOTALL
        )

        if title_match:

            title = clean_text(
                title_match.group(1)
            )

        company = ""

        company_match = re.search(
            r'class="[^"]*base-search-card__subtitle[^"]*"[^>]*>'
            r'(.*?)'
            r'</',
            card_html,
            flags=re.IGNORECASE | re.DOTALL
        )

        if company_match:

            company = clean_text(
                company_match.group(1)
            )

        location = ""

        location_match = re.search(
            r'class="[^"]*job-search-card__location[^"]*"[^>]*>'
            r'(.*?)'
            r'</',
            card_html,
            flags=re.IGNORECASE | re.DOTALL
        )

        if location_match:

            location = clean_text(
                location_match.group(1)
            )

        cards.append(
            {
                "url": url,
                "title": title,
                "company": company,
                "location_text": location
            }
        )

    return cards


# ============================================================
# TEXT EXTRACTION FALLBACKS
# ============================================================

def extract_title_from_text(text):

    if not text:
        return ""

    patterns = [
        r'"title"\s*:\s*"([^"]+)"',
        r'"jobTitle"\s*:\s*"([^"]+)"',
        r'<title[^>]*>(.*?)</title>'
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:

            value = clean_text(
                match.group(1)
            )

            value = re.sub(
                r"\s*\|\s*LinkedIn.*$",
                "",
                value,
                flags=re.IGNORECASE
            )

            if value:

                return value

    return ""


def extract_company_from_text(text):

    if not text:
        return ""

    patterns = [
        r'"companyName"\s*:\s*"([^"]+)"',
        r'"name"\s*:\s*"([^"]+)"'
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for value in matches:

            value = clean_text(
                value
            )

            if value:

                return value

    return ""


def extract_location_from_text(text):

    if not text:
        return ""

    patterns = [
        r'"addressLocality"\s*:\s*"([^"]+)"',
        r'"addressRegion"\s*:\s*"([^"]+)"',
        r'"addressCountry"\s*:\s*"([^"]+)"',
        r'"location"\s*:\s*"([^"]+)"'
    ]

    values = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            flags=re.IGNORECASE
        )

        for value in matches:

            value = clean_text(
                value
            )

            if value:
                values.append(value)

    return ", ".join(
        list(
            dict.fromkeys(
                values
            )
        )
    )


def extract_meta_content(
    html_text,
    property_name=None,
    name=None
):

    if not html_text:
        return ""

    if property_name:

        pattern = (
            r'<meta[^>]+property=["\']'
            + re.escape(property_name)
            + r'["\'][^>]+content=["\']'
            r'(.*?)["\']'
        )

        match = re.search(
            pattern,
            html_text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:

            return clean_text(
                match.group(1)
            )

    if name:

        pattern = (
            r'<meta[^>]+name=["\']'
            + re.escape(name)
            + r'["\'][^>]+content=["\']'
            r'(.*?)["\']'
        )

        match = re.search(
            pattern,
            html_text,
            flags=re.IGNORECASE | re.DOTALL
        )

        if match:

            return clean_text(
                match.group(1)
            )

    return ""


# ============================================================
# JSON-LD
# ============================================================

def extract_json_ld(html_text):

    if not html_text:
        return []

    blocks = re.findall(
        r'<script[^>]+type=["\']application/ld\+json["\'][^>]*>'
        r'(.*?)'
        r'</script>',
        html_text,
        flags=re.IGNORECASE | re.DOTALL
    )

    results = []

    for block in blocks:

        block = block.strip()

        if not block:
            continue

        try:

            data = json.loads(
                block
            )

            if isinstance(
                data,
                list
            ):

                results.extend(
                    data
                )

            else:

                results.append(
                    data
                )

        except Exception:

            continue

    return results


def find_job_posting(
    json_ld_items
):

    for item in json_ld_items:

        if not isinstance(
            item,
            dict
        ):
            continue

        item_type = item.get(
            "@type",
            ""
        )

        if isinstance(
            item_type,
            list
        ):

            types = [
                str(value).lower()
                for value in item_type
            ]

        else:

            types = [
                str(item_type).lower()
            ]

        if "jobposting" in types:

            return item

    return {}


def extract_json_location(
    job_posting
):

    if not isinstance(
        job_posting,
        dict
    ):
        return ""

    location = job_posting.get(
        "jobLocation"
    )

    if isinstance(
        location,
        list
    ):

        values = []

        for item in location:

            if not isinstance(
                item,
                dict
            ):
                continue

            address = item.get(
                "address",
                {}
            )

            if isinstance(
                address,
                dict
            ):

                parts = [
                    address.get(
                        "addressLocality",
                        ""
                    ),
                    address.get(
                        "addressRegion",
                        ""
                    ),
                    address.get(
                        "addressCountry",
                        ""
                    )
                ]

                parts = [
                    clean_text(
                        value
                    )
                    for value in parts
                    if value
                ]

                if parts:

                    values.append(
                        ", ".join(
                            parts
                        )
                    )

        return ", ".join(
            list(
                dict.fromkeys(
                    values
                )
            )
        )

    if isinstance(
        location,
        dict
    ):

        address = location.get(
            "address",
            {}
        )

        if isinstance(
            address,
            dict
        ):

            parts = [
                address.get(
                    "addressLocality",
                    ""
                ),
                address.get(
                    "addressRegion",
                    ""
                ),
                address.get(
                    "addressCountry",
                    ""
                )
            ]

            parts = [
                clean_text(
                    value
                )
                for value in parts
                if value
            ]

            return ", ".join(
                parts
            )

    return ""


def extract_json_company(
    job_posting
):

    if not isinstance(
        job_posting,
        dict
    ):
        return ""

    company = job_posting.get(
        "hiringOrganization"
    )

    if isinstance(
        company,
        dict
    ):

        return clean_text(
            company.get(
                "name",
                ""
            )
        )

    if isinstance(
        company,
        str
    ):

        return clean_text(
            company
        )

    return ""


# ============================================================
# DETAIL PAGE ENRICHMENT
# ============================================================

def enrich_job_from_detail_page(
    job
):

    url = job.get(
        "url",
        ""
    )

    if not url:
        return job

    print(
        f"  Enriching LinkedIn job: "
        f"{url}"
    )

    try:

        response = requests.get(
            url,
            headers=HEADERS,
            timeout=DETAIL_TIMEOUT
        )

        if response.status_code == 429:

            print(
                "  LinkedIn detail returned "
                "429. Skipping enrichment."
            )

            return job

        response.raise_for_status()

        html_text = response.text

    except Exception as error:

        print(
            f"  Detail enrichment failed: "
            f"{error}"
        )

        return job

    json_ld_items = extract_json_ld(
        html_text
    )

    job_posting = find_job_posting(
        json_ld_items
    )

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    url_title = extract_title_from_url(
        url
    )

    if url_title:

        job["title"] = url_title

    else:

        detail_title = (
            job_posting.get(
                "title",
                ""
            )
            if job_posting
            else ""
        )

        if detail_title:

            job["title"] = clean_text(
                detail_title
            )

        else:

            meta_title = extract_meta_content(
                html_text,
                property_name="og:title"
            )

            if meta_title:

                meta_title = re.sub(
                    r"\s*\|\s*LinkedIn.*$",
                    "",
                    meta_title,
                    flags=re.IGNORECASE
                )

                job["title"] = clean_text(
                    meta_title
                )

    # --------------------------------------------------------
    # COMPANY
    # --------------------------------------------------------

    company = extract_json_company(
        job_posting
    )

    if not company:

        company = extract_company_from_url(
            url
        )

    if not company:

        company = extract_meta_content(
            html_text,
            property_name="og:site_name"
        )

    if company:

        job["company"] = clean_text(
            company
        )

    # --------------------------------------------------------
    # LOCATION
    # --------------------------------------------------------

    location = extract_json_location(
        job_posting
    )

    if not location:

        location = extract_location_from_text(
            html_text
        )

    if location:

        job["location_text"] = clean_text(
            location
        )

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    description = ""

    if job_posting:

        description = clean_text(
            job_posting.get(
                "description",
                ""
            )
        )

    if not description:

        description = extract_meta_content(
            html_text,
            property_name="og:description"
        )

    if not description:

        description = extract_meta_content(
            html_text,
            name="description"
        )

    if description:

        job["description"] = description

    # --------------------------------------------------------
    # WORK TYPE
    # --------------------------------------------------------

    combined_text = " ".join(
        [
            job.get(
                "title",
                ""
            ),
            job.get(
                "location_text",
                ""
            ),
            job.get(
                "description",
                ""
            )
        ]
    )

    work_type, remote = detect_work_type(
        combined_text
    )

    if work_type:

        job["work_type"] = work_type

    job["remote"] = remote

    # --------------------------------------------------------
    # SKILLS / TOOLS
    # --------------------------------------------------------

    combined_text = " ".join(
        [
            job.get(
                "title",
                ""
            ),
            job.get(
                "description",
                ""
            )
        ]
    )

    job["skills"] = extract_skills(
        combined_text
    )

    job["tools"] = extract_tools(
        combined_text
    )

    # --------------------------------------------------------
    # SENIORITY
    # --------------------------------------------------------

    job["seniority"] = detect_seniority(
        job.get(
            "title",
            ""
        )
    )

    return job


# ============================================================
# NORMALIZE JOB
# ============================================================

def normalize_job(
    job
):

    url = normalize_linkedin_url(
        job.get(
            "url",
            ""
        )
    )

    title = clean_text(
        job.get(
            "title",
            ""
        )
    )

    company = clean_text(
        job.get(
            "company",
            ""
        )
    )

    location_text = clean_text(
        job.get(
            "location_text",
            ""
        )
    )

    description = clean_text(
        job.get(
            "description",
            ""
        )
    )

    work_type = clean_text(
        job.get(
            "work_type",
            ""
        )
    )

    remote = bool(
        job.get(
            "remote",
            False
        )
    )

    seniority = clean_text(
        job.get(
            "seniority",
            ""
        )
    )

    if not title:

        title = extract_title_from_url(
            url
        )

    if not company:

        company = extract_company_from_url(
            url
        )

    if not seniority:

        seniority = detect_seniority(
            title
        )

    if not work_type:

        detected_work_type, detected_remote = (
            detect_work_type(
                " ".join(
                    [
                        title,
                        location_text,
                        description
                    ]
                )
            )
        )

        work_type = detected_work_type

        if detected_remote:

            remote = True

    return {
        "id": extract_job_id(
            url
        ),
        "source": "LinkedIn",
        "title": title,
        "company": company,
        "location": {
            "country": "Argentina"
        },
        "location_text": location_text,
        "work_type": work_type,
        "remote": remote,
        "seniority": seniority,
        "description": description,
        "skills": job.get(
            "skills",
            []
        ),
        "tools": job.get(
            "tools",
            []
        ),
        "url": url,
        "published_at": job.get(
            "published_at",
            ""
        ),
        "scraped_at": job.get(
            "scraped_at",
            datetime.utcnow().isoformat()
        )
    }


# ============================================================
# ENRICHMENT DECISION
# ============================================================

def should_enrich_job(
    job
):

    if not job:
        return False

    url = job.get(
        "url",
        ""
    )

    if not url:
        return False

    title = clean_text(
        job.get(
            "title",
            ""
        )
    )

    company = clean_text(
        job.get(
            "company",
            ""
        )
    )

    description = clean_text(
        job.get(
            "description",
            ""
        )
    )

    if not title:
        return True

    if not company:
        return True

    if not description:
        return True

    return False


# ============================================================
# DEDUPLICATE
# ============================================================

def deduplicate_jobs(
    jobs
):

    unique = {}

    for job in jobs:

        job_id = job.get(
            "id",
            ""
        )

        url = job.get(
            "url",
            ""
        )

        key = (
            job_id
            or url
        )

        if not key:
            continue

        if key not in unique:

            unique[key] = job

    return list(
        unique.values()
    )


# ============================================================
# MAIN LINKEDIN SOURCE
# ============================================================

def get_all_linkedin_jobs():

    print(
        "\n=============================="
    )

    print(
        "LINKEDIN PUBLIC SOURCE"
    )

    print(
        "=============================="
    )

    raw_jobs = []

    for keyword in SEARCH_TERMS:

        html_text = search_linkedin_jobs(
            keyword,
            LOCATION
        )

        if not html_text:

            continue

        links = extract_linkedin_links(
            html_text
        )

        print(
            f"LinkedIn links found: "
            f"{len(links)}"
        )

        cards = extract_job_cards(
            html_text
        )

        print(
            f"LinkedIn job cards found: "
            f"{len(cards)}"
        )

        card_by_url = {}

        for card in cards:

            card_url = normalize_linkedin_url(
                card.get(
                    "url",
                    ""
                )
            )

            if card_url:

                card_by_url[
                    card_url
                ] = card

        for link in links:

            card = card_by_url.get(
                link,
                {}
            )

            title = clean_text(
                card.get(
                    "title",
                    ""
                )
            )

            company = clean_text(
                card.get(
                    "company",
                    ""
                )
            )

            location_text = clean_text(
                card.get(
                    "location_text",
                    ""
                )
            )

            if not title:

                title = extract_title_from_url_fallback(
                    link
                )

            if not company:

                company = extract_company_from_url(
                    link
                )

            job = {
                "url": link,
                "title": title,
                "company": company,
                "location_text": location_text,
                "description": "",
                "work_type": "",
                "remote": False,
                "seniority": detect_seniority(
                    title
                ),
                "skills": [],
                "tools": [],
                "published_at": "",
                "scraped_at": datetime.utcnow().isoformat()
            }

            normalized = normalize_job(
                job
            )

            raw_jobs.append(
                normalized
            )

    print(
        f"\nRaw LinkedIn jobs: "
        f"{len(raw_jobs)}"
    )

    unique_jobs = deduplicate_jobs(
        raw_jobs
    )

    print(
        f"Unique LinkedIn jobs: "
        f"{len(unique_jobs)}"
    )

    # --------------------------------------------------------
    # ENRICH ONLY JOBS THAT NEED IT
    # --------------------------------------------------------

    enrichment_candidates = [
        job
        for job in unique_jobs
        if should_enrich_job(
            job
        )
    ]

    print(
        f"LinkedIn enrichment candidates: "
        f"{len(enrichment_candidates)}"
    )

    enriched_jobs = []

    for job in unique_jobs:

        if should_enrich_job(
            job
        ):

            job = enrich_job_from_detail_page(
                job
            )

            job = normalize_job(
                job
            )

        enriched_jobs.append(
            job
        )

    print(
        f"LinkedIn jobs enriched: "
        f"{len(enrichment_candidates)}"
    )

    # --------------------------------------------------------
    # FINAL DEDUPLICATION
    # --------------------------------------------------------

    final_jobs = deduplicate_jobs(
        enriched_jobs
    )

    print(
        f"Final LinkedIn jobs: "
        f"{len(final_jobs)}"
    )

    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    print(
        "\nLinkedIn preview:"
    )

    for job in final_jobs[:10]:

        print(
            f"- {job.get('title', '')} | "
            f"{job.get('company', '')} | "
            f"{job.get('location_text', '')} | "
            f"{job.get('work_type', '')}"
        )

    print(
        "\n=============================="
    )

    print(
        "LINKEDIN PUBLIC SOURCE FINISHED"
    )

    print(
        "=============================="
    )

    return final_jobs


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    jobs = get_all_linkedin_jobs()

    print(
        f"\nReturned LinkedIn jobs: "
        f"{len(jobs)}"
    )
