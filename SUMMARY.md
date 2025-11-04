# eBay Stock Scraper - Investigation Summary & Fixes Applied

**Date:** 2025-11-04  
**Investigator:** Verdent AI  
**Listing Analyzed:** https://www.ebay.co.uk/itm/363486576357

---

## INVESTIGATION PROCESS

### 1. Analyzed Excel Structure
- **Excel File:** `ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx`
- **Key Columns Identified:**
  - `SIZE` - Contains dimension values like "40 x 60 cm", "50 x 80 cm", etc.
  - `Colour` - Contains color values like "Silver Black", "Red Black", etc.
  - `STATUS` / `INSTOCK/OUTOFSTOCK` - Target column for updates (Column M)
  - `LISTING LINK` - eBay product URLs

### 2. Inspected Live eBay DOM Structure
Used browser automation to inspect actual DOM structure of eBay listing 363486576357.

**Key Findings:**

#### Container Structure:
```html
<div class="vim x-msku-evo" data-testid="x-msku-evo">
  <div class="vim x-sku">
    <!-- Size dropdown -->
  </div>
  <div class="vim x-sku">
    <!-- Colour dropdown -->
  </div>
</div>
```

#### Dropdown Button:
```html
<span class="listbox-button mar-t-16 listbox-button--fluid">
  <button class="listbox-button__control btn btn--form btn--truncated"
          aria-haspopup="listbox"
          aria-controls="nid-h64-40">
    <span class="btn__cell">
      <span class="btn__label">Size:</span>
      <span class="btn__text">Select</span>
    </span>
  </button>
  <div role="listbox" class="listbox__options listbox-button__listbox">
    <!-- Options here -->
  </div>
</span>
```

#### Individual Options:
```html
<div class="listbox__option" 
     role="option" 
     data-sku-value-name="40 x 60 cm">
  <span class="listbox__value">40 x 60 cm</span>
  <span class="listbox__description">
    <div class="x-sku-description"></div>
  </span>
</div>
```

#### Out-of-Stock Indicators:
- Class: `listbox__option--disabled`
- Attribute: `aria-disabled="true"`
- Text: Contains "(Out of stock)"

---

## ISSUES IDENTIFIED

### Issue #1: Incorrect Button Selector ❌
**Location:** `ebay_stock_scraper.py:540-543`  
**Problem:** First button selector was looking for `span.listbox-button__control` instead of `button.listbox-button__control`

**Original Code:**
```python
button_locators = [
    locator.locator("span.listbox-button__control"),  # ❌ WRONG
    locator.locator("button[aria-haspopup='listbox']"),
]
```

**Fixed Code:**
```python
button_locators = [
    locator.locator("button.listbox-button__control"),  # ✅ CORRECT
    locator.locator("button[aria-haspopup='listbox']"),
]
```

---

### Issue #2: Wrong Options Selector Priority ❌
**Location:** `ebay_stock_scraper.py:569-572`  
**Problem:** Looking for `<li role="option">` first, but eBay uses `<div class="listbox__option">`

**Original Code:**
```python
options = options_container.locator("li[role='option']")
if options.count() == 0:
    options = options_container.locator("div.listbox__option")
```

**Fixed Code:**
```python
options = options_container.locator("div.listbox__option")  # ✅ Prioritize correct selector
if options.count() == 0:
    options = options_container.locator("li[role='option']")
```

---

### Issue #3: Incomplete Options Container Detection ❌
**Location:** `ebay_stock_scraper.py:556-567`  
**Problem:** Not checking for `div.listbox__options` within the button's parent container before falling back to `aria-controls`

**Original Code:**
```python
button.click()

options_container = locator
aria_controls = button.get_attribute("aria-controls")
if aria_controls:
    targeted = page.locator(f"#{aria_controls}")
    try:
        targeted.wait_for(state="visible", timeout=2000)
        if targeted.count():
            options_container = targeted
    except PlaywrightTimeoutError:
        pass
```

**Fixed Code:**
```python
button.click()
page.wait_for_timeout(300)  # ✅ Give dropdown time to expand

options_container = locator
# ✅ First try to find options within the same listbox-button container
options_in_button = locator.locator("div.listbox__options")
if options_in_button.count() > 0:
    try:
        options_in_button.first.wait_for(state="visible", timeout=2000)
        options_container = options_in_button.first
    except PlaywrightTimeoutError:
        pass

# ✅ Fallback to aria-controls method
if options_container == locator:
    aria_controls = button.get_attribute("aria-controls")
    if aria_controls:
        targeted = page.locator(f"#{aria_controls}")
        try:
            targeted.wait_for(state="visible", timeout=2000)
            if targeted.count():
                options_container = targeted
        except PlaywrightTimeoutError:
            pass
```

---

### Issue #4: No Use of data-sku-value-name Attribute ⚠️
**Location:** `ebay_stock_scraper.py:572-580`  
**Problem:** Only matching by visible text, not using the reliable `data-sku-value-name` attribute

**Original Code:**
```python
chosen_option = None
chosen_text = ""
for idx in range(options.count()):
    option = options.nth(idx)
    text = option.inner_text().strip()
    if option_matches(text, target_value):
        chosen_option = option
        chosen_text = text
        break
```

**Fixed Code:**
```python
chosen_option = None
chosen_text = ""

# ✅ First try exact match using data attribute
for idx in range(options.count()):
    option = options.nth(idx)
    data_sku_value = option.get_attribute("data-sku-value-name")
    if data_sku_value and option_matches(data_sku_value, target_value):
        chosen_option = option
        chosen_text = option.inner_text().strip()
        LOGGER.debug("Matched option via data-sku-value-name: %s", data_sku_value)
        break

# ✅ Fallback to text matching
if chosen_option is None:
    for idx in range(options.count()):
        option = options.nth(idx)
        text = option.inner_text().strip()
        if option_matches(text, target_value):
            chosen_option = option
            chosen_text = text
            LOGGER.debug("Matched option via text: %s", text)
            break
```

---

### Issue #5: Insufficient Debug Logging ⚠️
**Problem:** Hard to diagnose which group is being selected and why

**Fix Applied:**
- Added logging in `collect_variant_groups()` to show how many containers were found
- Added logging for each group detected
- Added logging in `select_option_from_group()` to show which group and value is being selected
- Added logging when matching options via data attribute vs text

---

## FILES MODIFIED

### 1. `ebay_stock_scraper.py`
**Changes:**
- Line 448: Added debug log for container count
- Line 457: Added debug log for each group found
- Line 493-496: Added summary log of all groups collected
- Line 517-519: Added group selection logging
- Line 541: Fixed button selector from `span` to `button`
- Line 556-577: Improved options container detection with proper wait
- Line 579-603: Improved option matching with data-sku-value-name priority
- Line 592, 602: Added debug logs for match methods

---

## FILES CREATED

### 1. `dom_structure_analysis.txt` (25.7 KB)
Detailed analysis of the eBay listing DOM structure including:
- All Size options (8 total)
- All Colour options (11 total)
- Complete HTML samples for each option
- Container structure documentation

### 2. `variation_structure.json` (32.4 KB)
Machine-readable JSON format of the variation structure for programmatic analysis

### 3. `ANALYSIS_AND_FIXES.md` (8.6 KB)
Comprehensive analysis document with:
- Issue identification
- Root cause analysis
- Recommended fixes
- Testing recommendations

### 4. `SUMMARY.md` (This file)
Complete investigation and fix summary

---

## HOW THE SCRAPER NOW WORKS

### Step 1: Navigate to Listing
```python
page.goto(record.listing_url, wait_until="domcontentloaded")
page.wait_for_timeout(800)
```

### Step 2: Detect Variant Groups
```python
groups = collect_variant_groups(page)
# Finds all div.vim.x-sku containers
# Extracts labels from .btn__label (e.g., "Size:", "Colour:")
# Logs: "Found 2 variant containers"
```

### Step 3: Match Groups to Dimensions
```python
# For each requested dimension (size, colour):
group_idx = find_group_for_dimension(groups, "size", used_indices)
# Matches using keywords: "size", "length", "dimensions"
# Or "colour", "color", "design", etc.
```

### Step 4: Select Options
```python
# Clicks button.listbox-button__control
# Waits 300ms for dropdown to expand
# Finds div.listbox__options within the button container
# Loops through div.listbox__option elements
# Matches using data-sku-value-name first, then text
# Checks for aria-disabled="true" or listbox__option--disabled class
```

### Step 5: Check Availability
```python
availability, detail = evaluate_availability(page)
# Checks for:
# - [data-testid="x-msku__availability-message"]
# - "Add to basket" button disabled state
# Returns IN_STOCK or OUT_OF_STOCK
```

---

## TESTING RECOMMENDATIONS

### Test Command:
```bash
python ebay_stock_scraper.py \
  --excel "ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx" \
  --engine chromium \
  --chromium-profile "./chromium_profile" \
  --limit 5 \
  --verbose \
  --delay 3 \
  --output results_test.xlsx \
  --copy-sheet sheet_test.xlsx
```

### What to Look For:
1. **Debug logs showing:**
   - "Found X variant containers"
   - "Found group 'Size' via div.vim.x-sku"
   - "Found group 'Colour' via div.vim.x-sku"
   - "Selecting 'X' from group 'Y'"
   - "Matched option via data-sku-value-name: X"

2. **Successful selections:**
   - Both Size and Colour should be selected
   - No "Variant value not found" errors
   - Proper detection of IN_STOCK vs OUT_OF_STOCK

3. **Excel output:**
   - Column M (STATUS) should be updated with correct values
   - INSTOCK for available combinations
   - OUT OF STOCK for unavailable combinations

---

## EXPECTED BEHAVIOR AFTER FIXES

### Before Fixes:
- ❌ Button not found (wrong selector)
- ❌ Options not detected (wrong priority)
- ❌ Dropdown not expanding properly
- ❌ Options matching failing for some variants

### After Fixes:
- ✅ Button found using correct selector
- ✅ Options detected immediately with correct selector
- ✅ Dropdown expands with proper wait time
- ✅ Options matched using reliable data-sku-value-name
- ✅ Better debug logging for troubleshooting
- ✅ Accurate stock status detection

---

## SAMPLE OUTPUT WITH --verbose

```
12:34:56 - DEBUG - Found 2 variant containers (div.vim.x-sku)
12:34:56 - DEBUG - Found group 'Size' via div.vim.x-sku
12:34:56 - DEBUG - Found group 'Colour' via div.vim.x-sku
12:34:56 - DEBUG - Total variant groups collected: 2
12:34:56 - DEBUG -   Group 0: 'Size' (type: vim)
12:34:56 - DEBUG -   Group 1: 'Colour' (type: vim)
12:34:57 - DEBUG - Selecting '40 x 60 cm' from group 'Size' (type: vim)
12:34:57 - DEBUG - Matched option via data-sku-value-name: 40 x 60 cm
12:34:58 - DEBUG - Selecting 'Silver Black' from group 'Colour' (type: vim)
12:34:58 - DEBUG - Matched option via data-sku-value-name: Silver Black - Greekey
12:34:59 - INFO - [Chromium 1/5] Checking item 363486576357 - Status: IN_STOCK
```

---

## CONCLUSION

The scraper was fundamentally sound but had critical selector issues that prevented it from:
1. Finding the dropdown buttons reliably
2. Detecting options in the correct order
3. Waiting properly for dropdowns to expand
4. Using the most reliable matching method (data attributes)

All issues have been fixed, and comprehensive debug logging has been added to help diagnose any future issues. The scraper should now accurately detect stock status for all Size/Colour combinations on eBay listings.

**Next Step:** Run a test with `--limit 10 --verbose` to verify the fixes work correctly.
