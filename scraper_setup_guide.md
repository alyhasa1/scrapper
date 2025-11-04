# eBay Variant Scraper – Setup & Usage Guide

## 1. Overview
This guide explains how to run `ebay_stock_scraper.py` on a fresh Windows machine. It covers dependency installation, Playwright setup, Excel expectations, runtime options, and troubleshooting. Share it with teammates who need to validate stock availability for eBay listings using size/colour variants.

## 2. Prerequisites
- **Operating System:** Windows 10/11 (PowerShell available). macOS/Linux also work with the same commands.
- **Python:** Version 3.10 or newer (confirm via `python --version`).
- **Excel workbook:** A sheet containing at least the following columns:
  - `LISTING LINK`
  - `Colour` (or `Color / Design`)
  - `SIZE` (or `Dimensions` / `Size / Pack/TYPE`)
  - `STATUS` (expected in column **I**; older sheets used column M)
- **Internet access** to reach `ebay.co.uk` while the scraper runs.

## 3. Initial setup
1. **Clone / copy the project**
   ```powershell
   git clone <repository-url>
   cd "stock check scrapper"
   ```
   Or unzip the provided directory into a working folder.

2. **Create an isolated environment (recommended)**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```powershell
   pip install --upgrade pip
   pip install pandas openpyxl beautifulsoup4 requests playwright
   ```
   > `requests` is optional but used when running the fast non-Chromium engine.

4. **Install Playwright browsers** (required for headful scraping)
   ```powershell
   playwright install chromium
   ```

## 4. Preparing the Excel workbook
- Place the source workbook in the project root (or supply an absolute path).
- Ensure row 1 is a header row. Row 2 can contain labels or metadata; the script auto-detects the real header text within the first two rows.
- `STATUS` can be named `STATUS` or `INSTOCK/OUTOFSTOCK`. If the header is renamed, the scraper falls back to column **I** automatically.
- Every listing row should have:
  - `LISTING LINK`: Full eBay URL (scraper strips query parameters).
  - `Colour`: The colour variant to target. Blank rows inherit the last colour used for the same listing.
  - `SIZE`: Size/dimension text exactly as shown in the eBay selector.

## 5. Running the scraper
Basic command (headful Chromium, first 50 rows):
```powershell
python .\ebay_stock_scraper.py \
  --excel "d:\stock check scrapper\ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx" \
  --engine chromium \
  --limit 50 \
  --delay 3 \
  --retries 2 \
  --output "d:\stock check scrapper\results_top50_postfix.xlsx" \
  --copy-sheet "d:\stock check scrapper\sheet_top50_postfix.xlsx"
```

### Optional flags
| Flag | Purpose |
| ---- | ------- |
| `--cookie` | Supply an eBay cookie header string to reduce bot challenges. |
| `--chromium-profile <dir>` | Use a persistent Chromium profile directory for sessions/cookies. |
| `--engine requests` | Use HTML-only scraping (faster, but limited accuracy). |
| `--verbose` | Enable DEBUG logging to trace selector decisions. |

## 6. Outputs
- **Console logs:** Progress entries like `[Chromium 12/50] Checking item 363486576357` and warnings when options are disabled.
- **Results workbook (`--output`):** A table with detected status per row plus diagnostics (`error` column).
- **Updated sheet (`--copy-sheet`):** Exact copy of the input workbook, but only the resolved STATUS column is rewritten (column I by default).
- **Backups:** Before writing, the script drops a timestamped copy of the original workbook under `backups/`.

## 7. Chromium interaction behaviour
- Selects colour **before** size to respect variant groupings.
- Marks a variant `OUT_OF_STOCK` when the option has `aria-disabled="true"`, contains `listbox__option--disabled`, or the label text includes "out of stock".
- When selections succeed, reads availability text from common eBay selectors and defaults to `IN_STOCK` if nothing indicates OOS.

## 8. Troubleshooting
| Symptom | Cause | Fix |
| --- | --- | --- |
| `Option is disabled: Label indicates out of stock` | Variant genuinely unavailable. | Confirm with live listing. |
| `Variant value 'Blue' not found` | Mismatch between sheet value and selector text. | Copy the exact label from eBay (case and spacing sensitive). |
| `Challenge detected` / CAPTCHA page | Bot protection triggered. | Relaunch with `--cookie`, add delay, or use persistent profile. |
| STATUS column not updating | Header text changed & column moved away from I. | Rename header to `STATUS` or edit `preferred_status_letter` in script. |

## 9. Quick test loop
1. Run with `--limit 5` after any sheet or code change.
2. Open the generated results workbook and verify `detected_status` against live listings.
3. Once satisfied, remove `--limit` (or raise it) for full runs.

## 10. Keeping environments in sync
- Share this document alongside the project folder.
- For repeatable installs, export dependencies: `pip freeze > requirements.txt` and have teammates run `pip install -r requirements.txt`.
- When the Excel layout changes (new columns, renames), update the mapping in `load_variants_from_excel` accordingly.

---
_Last updated: 2025-11-05_
