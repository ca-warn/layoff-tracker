# California Layoff Tracker

California Layoff Tracker is a lightweight, static dashboard for exploring layoff notices published by the State of California under the WARN Act.

The app renders:

- Summary KPI cards (next event, total layoffs, counties impacted)
- A top-company leaderboard
- A county choropleth map of layoffs
- A searchable, sortable, paginated data table

Data is sourced from the workbook at `data/warn_report.xlsx` and loaded client-side in the browser.

## Project Structure

```text
.
├── .github/workflows/       # Scheduled GitHub automation
├── scripts/                 # Deterministic social-post generator
├── social/linkedin-posts/   # Dated LinkedIn post archives
├── tests/                   # Automation tests
├── index.html              # Full dashboard app (HTML, CSS, JS)
└── data/
    ├── warn_report.xlsx    # WARN source data consumed by the app
    └── README.md           # Data notes
```

## How It Works

- The page fetches `./data/warn_report.xlsx`.
- XLSX parsing is performed in-browser with SheetJS (`xlsx.full.min.js`).
- County boundaries are pulled from a public GeoJSON endpoint and rendered with Leaflet.
- All filtering/sorting/search/pagination is done client-side.

## Run Locally

Because browsers restrict local file access for fetch requests, run a local web server from the repository root.

### Option 1: Python

```bash
python3 -m http.server 8000
```

Then open: <http://localhost:8000>

### Option 2: Node (if you use `npx`)

```bash
npx serve .
```

## Updating the Data

1. Replace `data/warn_report.xlsx` with a newer workbook.
2. Keep the same filename/path (or update the `WARN_URL` constant in `index.html`).
3. Refresh the app in your browser.

## Deployment

This project is static and can be deployed to any static host (GitHub Pages, Netlify, Vercel static output, S3 + CloudFront, etc.).

## GitHub Social Workflow

This repo includes a scheduled GitHub Actions workflow at `.github/workflows/generate-linkedin-post.yml`.

It runs daily and:

- parses `data/warn_report.xlsx` directly with Python standard-library code
- uses deterministic copy templates only; no Codex or LLM calls are involved
- prefers the earliest unseen upcoming WARN event for the next LinkedIn post
- falls back to summary posts only when all upcoming event candidates have already been archived
- suppresses duplicates by fingerprinting the underlying data, including company, county, address, effective date, and employee count
- commits each new post to `social/linkedin-posts/YYYY-MM-DD`
- can publish the archived post to LinkedIn when `LINKEDIN_ACCESS_TOKEN` is configured in GitHub Actions secrets

Each archive contains:

- `post.json` with structured metadata and the LinkedIn copy
- `post-copy.txt` with a plain-text version of the generated post
- `linkedin-publication.json` after successful publication

### Run Locally

```bash
python3 scripts/generate_linkedin_post.py
CLIENT_ID=... python3 scripts/linkedin_oauth_helper.py authorize-url
CLIENT_ID=... PRIMARY_CLIENT_SECRET=... python3 scripts/linkedin_oauth_helper.py exchange-code --code YOUR_CODE
LINKEDIN_ACCESS_TOKEN=... python3 scripts/resolve_linkedin_member.py
LINKEDIN_ACCESS_TOKEN=... python3 scripts/publish_linkedin_post.py --date YYYY-MM-DD
python3 -m unittest discover -s tests -p 'test_*.py'
```

### GitHub Secrets

To let GitHub Actions publish automatically, add:

- `LINKEDIN_ACCESS_TOKEN` required
- `LINKEDIN_AUTHOR_URN` optional; if omitted, the publisher derives it from LinkedIn `userinfo`
- `LINKEDIN_API_VERSION` optional; if omitted, the publisher tries the current `YYYYMM` version and then the previous month

Your existing `CLIENT_ID` and `PRIMARY_CLIENT_SECRET` secrets are useful for generating a member access token, but they do not let GitHub Actions publish by themselves. The publish step uses a member token, not just the app credentials.

## Notes

- If the county map fails to load, verify network access to the GeoJSON source.
- If data does not appear, confirm the workbook exists at `data/warn_report.xlsx` and includes the expected columns.
