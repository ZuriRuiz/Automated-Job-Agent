# 🤖 ZuriBot 2000™ — Automated Job Discovery & Matching Agent
### Python · GitHub Actions · SMTP · JSON · REST APIs

> A Python-based autonomous agent that scrapes multiple job platforms, scores opportunities against a structured candidate profile, and delivers personalized email alerts — fully automated via GitHub Actions.

---

## 🧩 Why I Built This

Job hunting is a job in itself.

I built this tool for my brother, who was going through a job search and spending hours every day manually checking multiple platforms — only to find listings he'd already seen, roles that didn't match his profile, or opportunities in the wrong location.

ZuriBot 2000™ automates that entire process. It runs twice a day, aggregates hundreds of listings across 7 platforms, scores each one against a detailed candidate profile, and delivers only the relevant matches directly to his inbox — so he can focus on applying, not searching.

---

## 🏗️ How It Works

GitHub Actions (cron: 2x/day)
│
▼
filter_jobs.py ◄─── profiles/your_profile.json
│
├── 7 job sources (LinkedIn, Greenhouse, Lever, Ashby, Workable, SmartRecruiters, Recruitee)
├── matcher.py → scoring 0–100 against profile
├── location_filter.py → remote / hybrid / on-site policy
├── deduplicator.py → cross-source deduplication
└── email_sender.py → SMTP delivery via Gmail
│
▼
📧 Email alert with matched jobs


- **Scoring** — each job is evaluated against target roles, seniority, skills, tools, industry and language
- **Location filtering** — configurable policy per work type (remote anywhere, hybrid/on-site by country)
- **Deduplication** — no repeated jobs across sources or runs, using a persistent seen-jobs log
- **Email digest** — structured alert with score, company, location and direct link per job

---

## 🛠️ Tech Stack

| | |
|---|---|
| Language | Python 3.12 |
| Automation | GitHub Actions |
| Email | Gmail SMTP |
| Data | JSON |
| Secrets | GitHub Secrets |

---

## 🚀 Setup

1. Clone the repo and install dependencies: `pip install requests`
2. Copy `profiles/example.json` → `profiles/your_name.json` and fill in your details
3. Update `PROFILE_PATH` in `src/filter_jobs.py`
4. Add GitHub Secrets: `EMAIL_USERNAME`, `EMAIL_APP_PASSWORD`, `EMAIL_MONITOR`
5. Create `data/seen_jobs.json` with `{}`
6. Trigger from **Actions → ZuriBot 2000™ → Run workflow**

---

## 🔒 Privacy

Real profiles and job history are not included. The `.gitignore` excludes `profiles/alvaro.json` and `data/seen_jobs.json`. Only `profiles/example.json` (fictional data) is committed as reference.

---

## 👤 Author

Built by [Zuri Ruiz](https://github.com/ZuriRuiz) — made with ❤️ for my brother.
