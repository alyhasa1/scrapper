# eBay Variant Stock Scraper

## 1. Purpose
This tool reads eBay listing variants from an Excel workbook and determines whether each requested size/colour combination is in stock. Results are surfaced in both a standalone results workbook and an updated copy of the original sheet where only the STATUS column is rewritten.

## 2. High-level workflow
1. **Input discovery** – The script opens the user-supplied workbook (`--excel`) and dynamically resolves the header row so it can tolerate column shifts. It expects the first worksheet to contain listing metadata.
2. **Variant records** – Each data row is converted into a `VariantRecord` capturing:
   - Listing URL (column `LISTING LINK`)
   - Size (column `SIZE` or `Size / Pack/TYPE`)
   - Colour (column `Colour` / `Color / Design`)
   - Existing sheet status (column `INSTOCK/OUTOFSTOCK`)
   - Optional identifiers (SR No, ITEM NUMBER, etc.)
3. **Engine selection** – Depending on `--engine`, records are processed via:
   - `requests` engine: Fast HTML download + BeautifulSoup parsing.
   - `chromium` engine (default for production runs): Headful Playwright session that interacts with eBay’s variant selectors.
4. **Variant availability check** – For each record Playwright:
   - Navigates to the base listing URL (query stripped) and waits for the DOM to stabilise.
   - Detects bot challenges before proceeding.
   - Locates variant selector groups (size + colour) by scanning shadcn-style `div.vim.x-sku`, `data-testid="x-msku__group"`, or legacy `<select>` elements.
   - Matches option text against the target value. A match is considered **out of stock** if any of the following is true:
     - `aria-disabled="true"`
     - Option includes `listbox__option--disabled`
     - The visible label contains “out of stock”.
   - When both size and colour are selectable, size is chosen first, then colour. If any selection fails, the record is marked `OUT_OF_STOCK` when the failure reason mentions disabled/out-of-stock hints; otherwise it is labelled `ERROR`.
   - If variants load successfully, the page is probed for availability banners (`data-testid="x-msku__availability-message"`, `#qtySubTxt`, etc.). Missing or generic text defaults to `IN_STOCK`.
5. **Result capture** – Each record emits a row including the detected status, the original sheet status, any error reason, and bookkeeping fields (row index, variation id, etc.).
6. **Workbook updates** – After processing:
   - A timestamped log of sample rows is printed to stdout.
   - `update_sheet_with_results` creates a timestamped backup of the input workbook (in `backups/`), rewrites only the resolved STATUS column, and overwrites the original file in place.
   - A copy of the updated workbook is written to the `--copy-sheet` path (e.g. `sheet_top100_postfix.xlsx`).
   - Optional results dataframe is exported to the path provided via `--output`.

## 3. Command-line options
| Flag | Description |
| --- | --- |
| `--excel PATH` | Required. Source workbook. |
| `--limit N` | Optional. Restricts processing to the first _N_ variant rows. |
| `--engine {requests,chromium}` | Variant detection backend (Chromium recommended). |
| `--delay SECONDS` | Waiting period between records (also used after challenges). |
| `--retries N` | Maximum retries per listing when errors/challenges occur. |
| `--cookie STRING` | Cookie header to prime the Chromium context. |
| `--output PATH` | Optional results dataframe export (xlsx/csv by extension). |
| `--copy-sheet PATH` | Required when you want a duplicate workbook with STATUS updates. |
| `--chromium-profile DIR` | Persistent Chromium profile to retain cookies/sessions. |
| `--verbose` | Enables DEBUG logging. |

## 4. Status codes & interpretation
| Code | Meaning | Source |
| --- | --- | --- |
| `IN_STOCK` | Variant selectable and availability text did not signal OOS. | DOM evaluation fallback. |
| `OUT_OF_STOCK` | Selector disabled (`aria-disabled="true"`, disabled class) or availability banner flagged OOS. | Variant selection or availability widgets. |
| `BLOCKED` | eBay challenge/captcha identified. Record not retried beyond configured limit. | Challenge detection. |
| `ERROR` | Unexpected exception, timeout, or selector mismatch. | Exception handling. |
| `UNKNOWN` | Only surfaced in requests engine when parsing fails. | Requests HTML parsing. |

Each result row includes the raw `error` text to help diagnose failures (e.g., “Option disabled”, “Variant value 'Blue' not found”).

## 5. Excel writing strategy
1. `resolve_status_column` scans the first 10 rows for `STATUS`/`INSTOCK/OUTOFSTOCK` headers and captures the column index.
2. The original workbook is opened via `openpyxl`, STATUS cells are updated using `status_normalization` (mapping `IN_STOCK` → `INSTOCK`, `OUT_OF_STOCK` → `OUT OF STOCK`, etc.).
3. A copy is saved to the path passed via `--copy-sheet`. No other columns/rows are modified, preserving formulas and formatting.

## 6. Logging & outputs
- Console logging (INFO by default) logs each Chromium iteration (`[Chromium x/y]`) and the detected status summary.
- Result exports follow the naming convention used by the run (e.g., `results_top100_postfix.xlsx`).
- Backups of the source workbook are stored beneath `backups/` with a timestamp prefix prior to in-place updates.

## 7. Known limitations & troubleshooting
- **Duplicate listings:** The sheet currently repeats the same item number for many rows. If the second dimension is missing or mislabelled, the scraper may repeatedly select the same variant and override availability. Validate column data for each row before rerunning.
- **Variant order assumption:** The script assumes size is the primary dimension and colour is secondary. Listings that reverse this order (colour first) require both columns to be correctly populated to avoid `Variant value not found` errors.
- **Post-70 row errors:** Several of the recent runs show `ERROR` after row ~70 due to the same listing failing variant selection. This typically means the target option text mismatches the on-page label (extra spacing, different spelling, or abbreviated SKU). Cross-check the sheet values with the live dropdown text.
- **Bot challenges:** Persistent captchas require a fresh cookie header or Chromium profile, as the script only retries; it does not auto-solve challenges.
- **Performance:** Headful Chromium introduces 3–4 seconds per entry (plus delays). Reduce `--delay` cautiously if you have stable cookies/bypass.

## 8. Suggested validation loop
1. Run with `--limit 5` after any code/config change to confirm statuses.
2. Inspect `results_*.xlsx` for `ERROR`/`BLOCKED` rows and review the `error` column.
3. Spot-check the updated workbook’s STATUS column against live listings.

## 9. Extending the scraper
- To add another variant dimension (e.g., material), populate the column in Excel and update `GROUP_KEYWORDS` so it maps to the correct selector group.
- Introduce custom normalisation rules in `option_matches` if listing options use consistent abbreviations.
- Add further availability selectors in `evaluate_availability` for edge layouts (international sites, bulk purchase widgets, etc.).

---
_Last updated: 2025-11-04_
