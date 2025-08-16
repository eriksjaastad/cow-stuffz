#!/usr/bin/env python3
"""
Fort Bend County Brand Scraper
Simple script to scrape brand records from Fort Bend County website.
"""

import asyncio
import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Union, Tuple

from playwright.async_api import async_playwright, Page, TimeoutError as PwTimeoutError

# Configuration
SEARCH_ENTRY_URL = "https://ccweb.co.fort-bend.tx.us/RealEstate/SearchEntry.aspx"
SEARCH_RESULTS_URL = "https://ccweb.co.fort-bend.tx.us/RealEstate/SearchResults.aspx"
BRAND_CHECKBOX_ID = "#cphNoMargin_f_dclDocType_14"
OUTPUT_CSV = "fort_bend_brands.csv"
OUTPUT_JSONL = "fort_bend_brands.jsonl"

# Timeouts
CHECKBOX_TIMEOUT = 10000
SEARCH_MODAL_TIMEOUT = 60000
TABLE_WAIT_TIMEOUT = 10000


async def select_brand_document_type(page: Page) -> None:
    """Select BRAND from the Document Type checkbox."""
    print("  -> Selecting BRAND document type...")
    
    try:
        # Find and click the BRAND checkbox
        brand_checkbox = await page.wait_for_selector(BRAND_CHECKBOX_ID, timeout=CHECKBOX_TIMEOUT)
        if not brand_checkbox:
            raise RuntimeError("BRAND checkbox not found")
        
        # Check if already selected
        if await brand_checkbox.is_checked():
            print("  -> BRAND already selected")
            return
        
        # Click to select
        await brand_checkbox.click()
        print("  -> BRAND selected")
        
        # Wait for selection to register
        await page.wait_for_timeout(2000)
        
        # Verify selection
        if not await brand_checkbox.is_checked():
            print("  -> Warning: BRAND selection may not have registered")
        
    except Exception as e:
        print(f"  -> Error selecting BRAND: {e}")
        raise


async def click_search_button(page: Page) -> None:
    """Click the search button to submit the form."""
    print("  -> Submitting search form...")
    
    try:
        # Try common search button selectors
        search_selectors = [
            "input[type='submit'][value*='Search']",
            "button:has-text('Search')",
            "input[type='button'][value*='Search']",
            "input[value='Search']"
        ]
        
        for selector in search_selectors:
            if await page.locator(selector).count() > 0:
                await page.click(selector)
                print("  -> Search submitted")
                return
        
        # Fallback to Enter key
        await page.keyboard.press("Enter")
        print("  -> Search submitted (Enter key)")
        
    except Exception as e:
        print(f"  -> Error submitting search: {e}")
        raise


async def wait_for_search_results(page: Page) -> bool:
    """Wait for search to complete and results to load."""
    print("  -> Waiting for search results...")
    
    try:
        # Wait for search modal to appear and disappear
        await page.wait_for_selector("text=Searching for records", timeout=5000)
        await page.wait_for_selector("text=Searching for records", state="hidden", timeout=SEARCH_MODAL_TIMEOUT)
        
        # Wait for page to fully load
        await page.wait_for_timeout(3000)
        
        # Check if we're on results page
        current_url = page.url
        if "SearchResults.aspx" in current_url:
            print("  -> Successfully reached results page")
            return True
        
        # Try additional wait if needed
        await page.wait_for_timeout(5000)
        current_url = page.url
        if "SearchResults.aspx" in current_url:
            print("  -> Reached results page after additional wait")
            return True
        
        print("  -> Failed to reach results page")
        return False
        
    except Exception as e:
        print(f"  -> Error waiting for results: {e}")
        # Check URL anyway
        return "SearchResults.aspx" in page.url


async def find_results_table(tables: List[Any]) -> Union[Tuple[Any, int, int, int], Tuple[None, None, None, None]]:
    """Find the table containing actual results data."""
    for i, table in enumerate(tables):
        try:
            rows = await table.query_selector_all("tr")
            if len(rows) <= 1:
                continue
                
            # Check if table has meaningful data
            first_row_cells = await rows[0].query_selector_all("td, th")
            if len(first_row_cells) < 3:
                continue
            
            # Verify table contains actual data
            for row in rows[1:3]:
                row_cells = await row.query_selector_all("td")
                for cell in row_cells:
                    cell_text = await cell.inner_text()
                    if cell_text.strip() and cell_text.strip() != '&nbsp;':
                        return table, i, len(rows), len(first_row_cells)
                        
        except Exception:
            continue
    
    return None, None, None, None


async def scrape_results_table(page: Page) -> List[Dict[str, Any]]:
    """Scrape the results table from the current page."""
    print("  -> Locating results table...")
    
    try:
        # Wait for tables to load
        await page.wait_for_selector("table", timeout=TABLE_WAIT_TIMEOUT)
        tables = await page.query_selector_all("table")
        
        # Find the results table
        results_table, table_index, num_rows, num_cols = await find_results_table(tables)
        
        if not results_table:
            print("  -> No results table found")
            return []
        
        print(f"  -> Found results table {table_index} with {num_rows} rows and {num_cols} columns")
        
        # Parse table data
        rows = await results_table.query_selector_all("tr")
        data = []
        
        # Determine start row (skip header if present)
        start_row = 0
        if rows and await rows[0].inner_text():
            first_row_text = await rows[0].inner_text()
            if any(header in first_row_text for header in ["Instrument", "Date", "Doc Type"]):
                start_row = 1
        
        print(f"  -> Parsing {len(rows) - start_row} data rows")
        
        for i in range(start_row, len(rows)):
            try:
                row = rows[i]
                cells = await row.query_selector_all("td")
                
                if len(cells) >= 3:
                    # Extract cell contents
                    cell_texts = []
                    for cell in cells:
                        try:
                            text = await cell.inner_text()
                            text = text.replace('&nbsp;', ' ').strip()
                            cell_texts.append(text)
                        except Exception:
                            cell_texts.append("")
                    
                    # Create record with meaningful field names
                    record = {
                        "row_number": i + 1,
                        "instrument_number": cell_texts[0] if len(cell_texts) > 0 else "",
                        "date": cell_texts[1] if len(cell_texts) > 1 else "",
                        "doc_type": cell_texts[2] if len(cell_texts) > 2 else "",
                        "grantor": cell_texts[3] if len(cell_texts) > 3 else "",
                        "grantee": cell_texts[4] if len(cell_texts) > 4 else "",
                        "legal_description": cell_texts[5] if len(cell_texts) > 5 else "",
                        "raw_data": cell_texts
                    }
                    data.append(record)
                    
            except Exception as e:
                print(f"  -> Error parsing row {i}: {e}")
                continue
        
        print(f"  -> Successfully parsed {len(data)} records")
        return data
        
    except Exception as e:
        print(f"  -> Error scraping results table: {e}")
        return []


async def save_results(data: List[Dict[str, Any]]) -> None:
    """Save the scraped data to CSV and JSONL files."""
    if not data:
        print("  -> No data to save")
        return
    
    print(f"  -> Saving {len(data)} records...")
    
    # Save to CSV
    try:
        with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data)
        print(f"  -> Saved CSV: {OUTPUT_CSV}")
    except Exception as e:
        print(f"  -> Error saving CSV: {e}")
    
    # Save to JSONL
    try:
        with open(OUTPUT_JSONL, 'w', encoding='utf-8') as jsonlfile:
            for record in data:
                jsonlfile.write(json.dumps(record) + '\n')
        print(f"  -> Saved JSONL: {OUTPUT_JSONL}")
    except Exception as e:
        print(f"  -> Error saving JSONL: {e}")


async def main() -> None:
    """Main scraping function."""
    print("Starting Fort Bend County Brand Scraper...")
    
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate and search
            print("Step 1: Navigating to search page...")
            await page.goto(SEARCH_ENTRY_URL, wait_until="domcontentloaded")
            
            print("Step 2: Selecting BRAND document type...")
            await select_brand_document_type(page)
            
            print("Step 3: Submitting search...")
            await click_search_button(page)
            
            print("Step 4: Waiting for results...")
            if not await wait_for_search_results(page):
                print("  -> Warning: May not have reached results page")
            
            # Scrape and save
            print("Step 5: Scraping results...")
            data = await scrape_results_table(page)
            
            print("Step 6: Saving results...")
            await save_results(data)
            
            print(f"Scraping complete! Found {len(data)} records.")
            
        except Exception as e:
            print(f"Error during scraping: {e}")
            raise
        finally:
            await browser.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)