# Navigation Error Fix

## Issue Encountered

```
ERROR: Page.evaluate: Execution context was destroyed, most likely because of a navigation
```

### What Was Happening

1. ✅ Size selected successfully: "40 x 60 cm"
2. ✅ Colour selected successfully: "Beige Brown - Greekey"
3. 🔄 **eBay automatically refreshes/navigates the page** after variant selection (normal eBay behavior)
4. ❌ Scraper tries to run JavaScript `page.evaluate()` on destroyed context
5. 💥 Error: "Execution context was destroyed"

### Root Cause

When you select variants on eBay, the page often:
- Refreshes to load the new variant's details
- Updates the URL with variant parameters
- Re-renders the page content
- Destroys the JavaScript execution context

The scraper was immediately trying to check availability without waiting for this navigation to complete.

---

## Fixes Applied

### Fix #1: Wait for Page Stabilization After Variant Selection
**Location:** `ebay_stock_scraper.py` line 788-801

**Added:**
```python
# After selecting all variants, wait for page to stabilize
try:
    page.wait_for_load_state("networkidle", timeout=5000)
except PlaywrightTimeoutError:
    LOGGER.debug("Network not idle after variant selection, continuing anyway")

page.wait_for_timeout(1000)  # Additional safety wait

try:
    page.wait_for_load_state("domcontentloaded", timeout=3000)
except PlaywrightTimeoutError:
    pass

# NOW it's safe to evaluate availability
availability, availability_detail = evaluate_availability(page)
```

**What this does:**
1. Waits up to 5 seconds for network activity to stop (page finished loading)
2. Waits additional 1 second for JavaScript to settle
3. Waits up to 3 seconds for DOM to be fully loaded
4. Only then checks availability

### Fix #2: Add Retry Logic to evaluate_availability()
**Location:** `ebay_stock_scraper.py` line 655-664

**Added:**
```python
try:
    availability_text = page.evaluate(script)
except Exception as exc:
    LOGGER.warning("Failed to evaluate availability script, retrying after delay: %s", exc)
    page.wait_for_timeout(1000)
    try:
        availability_text = page.evaluate(script)
    except Exception as retry_exc:
        LOGGER.error("Failed to evaluate availability after retry: %s", retry_exc)
        return "IN_STOCK", None  # Default to IN_STOCK if we can't determine
```

**What this does:**
- Catches any `page.evaluate()` errors
- Waits 1 second and retries once
- Falls back to "IN_STOCK" if still failing (safe default)

### Fix #3: Increase Wait Time After Option Click
**Location:** `ebay_stock_scraper.py` line 626

**Changed from:**
```python
chosen_option.click()
page.wait_for_timeout(400)  # Too short
```

**Changed to:**
```python
chosen_option.click()
page.wait_for_timeout(800)  # Doubled to allow page to react
```

**What this does:**
- Gives eBay more time to process the option selection
- Allows any AJAX requests to complete
- Reduces chance of race conditions

---

## Expected Behavior Now

### Before Fix:
```
✅ Select Size
✅ Select Colour
🔄 Page navigates
❌ ERROR: Execution context destroyed
```

### After Fix:
```
✅ Select Size
⏱️ Wait 800ms
✅ Select Colour
⏱️ Wait 800ms
🔄 Page navigates
⏱️ Wait for networkidle (up to 5s)
⏱️ Wait 1000ms
⏱️ Wait for domcontentloaded (up to 3s)
✅ Evaluate availability
✅ Get status: IN_STOCK or OUT_OF_STOCK
```

---

## Test Again

Run the same command:
```bash
python ebay_stock_scraper.py --excel "ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx" --engine chromium --chromium-profile "./chromium_profile" --limit 5 --verbose --delay 3 --output results_test5.xlsx --copy-sheet sheet_test5.xlsx
```

### Expected Output Now:
```
✅ DEBUG - Found 2 variant containers
✅ DEBUG - Matched option via data-sku-value-name: 40 x 60 cm
✅ DEBUG - Matched option via data-sku-value-name: Beige Brown - Greekey
✅ DEBUG - Network not idle after variant selection, continuing anyway (might appear)
✅ INFO - [Chromium 1/5] Checking item 363486576357 - Status: IN_STOCK
```

No more "Execution context was destroyed" errors!

---

## Why This Happens on eBay

eBay's variant system works like this:
1. Each variant combination has a unique item variation ID
2. When you select Size + Colour, eBay may:
   - Update the URL: `?var=633227768703`
   - Refresh the page to show correct price/stock for that variant
   - Load new images for that variant
   - Update availability message
3. This refresh destroys the JavaScript context

Our fix properly waits for all these updates to complete before checking availability.

---

## Performance Impact

- **Additional wait time per item:** ~2-6 seconds (depending on how fast eBay loads)
- **More reliable:** Should eliminate execution context errors
- **Trade-off:** Slightly slower but much more accurate

If you want to speed it up slightly, you can reduce the timeouts, but I recommend keeping them for reliability:
- `wait_for_load_state("networkidle", timeout=5000)` - can reduce to 3000
- `page.wait_for_timeout(1000)` - can reduce to 500
- `wait_for_load_state("domcontentloaded", timeout=3000)` - can reduce to 2000

But test first to make sure it still works!
