# North Macedonia vs Netherlands — State Site Evaluation

A monthly automated audit of North Macedonia and Netherlands government, agency, and municipality websites. Results are published as a static dashboard on GitHub Pages.

**Live report:** `https://YOUR_USERNAME.github.io/YOUR_REPO`

## What it checks

| Check | Description |
|---|---|
| **Uptime** | HTTP status — is the site reachable? |
| **Load time** | Average response time over 2 requests |
| **SSL certificate** | Valid cert, expiry date, issuer |
| **CMS** | Detects WordPress / Drupal / Joomla / TYPO3 and flags outdated versions |
| **robots.txt** | Present at `/robots.txt` |
| **sitemap.xml** | Present at `/sitemap.xml` |
| **llms.txt** | Present at `/llms.txt` |
| **RSS feed** | Detected via HTML `<link>` tag or common feed paths |

Each site is scored out of **8** based on the above checks.

## Scope

- 🇲🇰 **233 North Macedonia sites** — all ministries, courts, independent bodies, regulatory agencies, state-backed enterprises, and all 80 municipalities
- 🇳🇱 **26 Netherlands sites** — all 15 ministries, Parliament, Senate, Royal House, and key agencies

## Project structure

```
.
├── evaluate.py          # Runs all checks, writes results.json
├── generate_report.py   # Reads results.json, writes docs/index.html
├── results.json         # Latest results (committed by CI)
├── docs/
│   └── index.html       # Generated dashboard (served by GitHub Pages)
└── .github/
    └── workflows/
        └── evaluate.yml # GitHub Actions — runs monthly, deploys to Pages
```

## Setup

1. Fork or create a new repo and push these files
2. Go to **Settings → Pages** and set source to the `gh-pages` branch
3. The first run will trigger automatically on the 1st of next month, or run it manually from the **Actions** tab

No dependencies — pure Python stdlib, no `pip install` needed.

## Running locally

```bash
python evaluate.py          # runs checks, writes results.json (~2 min with 10 workers)
python generate_report.py   # generates docs/index.html from results.json
```

## Configuration

Edit the top of `evaluate.py` to adjust:

```python
WORKERS = 10    # concurrent site checks (increase to go faster)
TIMEOUT = 12    # seconds per HTTP request
REPEAT  = 2     # requests per site for load time averaging
```

To add or remove sites, edit the `WEBSITES_MK` or `WEBSITES_NL` lists.

## CMS version references

Outdated detection compares the **major version** detected against:

| CMS | Latest tracked |
|---|---|
| WordPress | 6.9 |
| Drupal | 11 |
| Joomla | 5.3 |
| TYPO3 | 13 |

Update `CMS_LATEST` in `evaluate.py` as new major versions release.
