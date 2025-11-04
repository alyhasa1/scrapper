# Quick Test & Usage Guide

## Test the Fixed Scraper

### Test with 5 rows (recommended first test):
```bash
python ebay_stock_scraper.py --excel "ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx" --engine chromium --chromium-profile "./chromium_profile" --limit 5 --verbose --delay 3 --output results_test5.xlsx --copy-sheet sheet_test5.xlsx
```

### Test with 10 rows:
```bash
python ebay_stock_scraper.py --excel "ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx" --engine chromium --chromium-profile "./chromium_profile" --limit 10 --verbose --delay 3 --output results_test10.xlsx --copy-sheet sheet_test10.xlsx
```

### Full run (all rows):
```bash
python ebay_stock_scraper.py --excel "ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx" --engine chromium --chromium-profile "./chromium_profile" --verbose --delay 3 --output results_full.xlsx --copy-sheet sheet_full.xlsx
```

## Key Changes Made

1. **Fixed button selector**: `span.listbox-button__control` → `button.listbox-button__control`
2. **Fixed options priority**: Now looks for `div.listbox__option` first instead of `li[role='option']`
3. **Improved dropdown detection**: Checks for `div.listbox__options` within button container before using `aria-controls`
4. **Added wait time**: 300ms wait after clicking dropdown to ensure it expands
5. **Better option matching**: Uses `data-sku-value-name` attribute first, falls back to text
6. **Enhanced logging**: Shows which groups are found and how options are matched

## What to Look for in Logs

### Good Signs ✅:
```
DEBUG - Found 2 variant containers (div.vim.x-sku)
DEBUG - Found group 'Size' via div.vim.x-sku
DEBUG - Found group 'Colour' via div.vim.x-sku
DEBUG - Selecting '40 x 60 cm' from group 'Size' (type: vim)
DEBUG - Matched option via data-sku-value-name: 40 x 60 cm
INFO - [Chromium 1/5] Checking item 363486576357 - Status: IN_STOCK
```

### Warning Signs ⚠️:
```
ERROR - Variant value 'X' not found
ERROR - Variant selector button missing
ERROR - No variant group found for size
BLOCKED - Bot challenge detected
```

## Understanding Results

### Status Codes:
- **IN_STOCK** → Item is available for this size/color combination
- **OUT_OF_STOCK** → Item is not available (option disabled or marked out of stock)
- **ERROR** → Something went wrong (check error column for details)
- **BLOCKED** → eBay bot protection triggered (may need fresh cookies)

### Excel Output:
- Original file is backed up to `backups/` folder with timestamp
- STATUS column (Column M) is updated with detected status
- Copy is saved to the `--copy-sheet` path

## Troubleshooting

### If you see "Variant value not found":
1. Check the Excel file - make sure SIZE and Colour columns match exactly what's on eBay
2. Run with `--verbose` to see what options were found
3. Check if the listing has changed

### If you see "BLOCKED":
1. The scraper is using the chromium_profile which should have cookies
2. Try opening the browser manually first to verify you're logged in
3. May need to solve a captcha manually once

### If you see many "ERROR" status:
1. Check the error column in the results Excel for specific error messages
2. Run with `--verbose` for detailed logs
3. Check if eBay changed their DOM structure

## Files Generated

1. **results_*.xlsx** - Full results with all details
2. **sheet_*.xlsx** - Copy of original Excel with STATUS column updated
3. **backups/ECOMWITH YASIR_*.xlsx** - Timestamped backup of original before changes

## DOM Structure Reference

eBay uses this structure for variants:
```html
<div class="vim x-msku-evo">
  <div class="vim x-sku">
    <span class="listbox-button">
      <button class="listbox-button__control">
        <span class="btn__label">Size:</span>
      </button>
      <div class="listbox__options">
        <div class="listbox__option" data-sku-value-name="40 x 60 cm">
          ...
        </div>
      </div>
    </span>
  </div>
  <div class="vim x-sku">
    <!-- Colour dropdown, same structure -->
  </div>
</div>
```

Out-of-stock options have:
- `class="listbox__option--disabled"`
- `aria-disabled="true"`
- Text may contain "(Out of stock)"
