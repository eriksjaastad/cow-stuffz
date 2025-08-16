# Texas Brand Registry Scraper (Playwright)

This is a ready-to-run Python scraper that targets the **Texas Department of Agriculture** brand registry search and extracts basic fields by **county**.

> Note: The site uses dynamic/ASP.NET postbacks, so we use **Playwright** to drive a real browser. You may need to tweak the CSS selectors if the site updates.

## Quick start

```bash
# 1) Create a virtual environment (optional but recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2) Install dependencies
pip install playwright pandas sqlalchemy

# 3) Install browser
playwright install

# 4) Run (example: Travis County)
python scrape_texas_brands.py --county "Travis" --out data/brands_travis.csv --sqlite data/brands.db --download-images
```

Outputs:
- CSV at `data/brands_travis.csv`
- SQLite DB at `data/brands.db` (table: `brands`)
- Brand images in `data/brand_images/`

## Tweaking selectors

Open the site in a browser and Inspect the results table. If the script fails to find elements, update the `SELECTORS` and `COLUMN_MAP` dictionaries near the top of `scrape_texas_brands.py` to match the live DOM.

## Polite scraping

- The script waits between pages (`PAGE_DELAY = 1.0`). Increase this if needed.
- Consider limiting pages via `--max-pages` while testing.
- Cache results locally and avoid hitting the site repeatedly.

## Common issues

- **County not found**: Use the exact label from the dropdown (case-insensitive match is implemented).
- **Table structure different**: Adjust `COLUMN_MAP` to point to correct column indices.
- **Images blocked**: Some sites gate image requests; keeping downloads via `page.request.get()` helps.