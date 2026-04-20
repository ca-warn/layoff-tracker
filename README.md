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

## Notes

- If the county map fails to load, verify network access to the GeoJSON source.
- If data does not appear, confirm the workbook exists at `data/warn_report.xlsx` and includes the expected columns.
