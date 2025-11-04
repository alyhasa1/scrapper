# eBay Scraper Analysis and Fixes

## Analysis Date: 2025-11-04

---

## FINDINGS FROM BROWSER INSPECTION

### Actual DOM Structure (eBay Listing: 363486576357)

#### Main Container:
```html
<div class="vim x-msku-evo" data-testid="x-msku-evo">
```

#### Size Dropdown (First Variation):
```html
<div class="vim x-sku">
  <span class="listbox-button mar-t-16 listbox-button--fluid">
    <button class="listbox-button__control btn btn--form btn--truncated" 
            aria-haspopup="listbox" 
            aria-controls="nid-h64-40">
      <span class="btn__cell">
        <span class="btn__label">Size:</span>
        <span class="btn__text">Select</span>
      </span>
    </button>
    <div role="listbox" class="listbox__options listbox-button__listbox" id="nid-h64-40">
      <!-- Options here -->
    </div>
  </span>
</div>
```

#### Colour Dropdown (Second Variation):
```html
<div class="vim x-sku">
  <span class="listbox-button mar-t-16 listbox-button--fluid">
    <button class="listbox-button__control btn btn--form btn--truncated" 
            aria-haspopup="listbox" 
            aria-controls="nid-h64-27">
      <span class="btn__cell">
        <span class="btn__label">Colour:</span>
        <span class="btn__text">Select</span>
      </span>
    </button>
    <div role="listbox" class="listbox__options listbox-button__listbox" id="nid-h64-27">
      <!-- Options here -->
    </div>
  </span>
</div>
```

#### Individual Option Structure:
```html
<!-- Available option -->
<div class="listbox__option" 
     role="option" 
     data-sku-value-name="40 x 60 cm">
  <span class="listbox__value">40 x 60 cm </span>
  <span class="listbox__description">
    <div class="x-sku-description"></div>
  </span>
  <svg class="icon icon--16">...</svg>
</div>

<!-- Out of stock option (when it occurs) -->
<div class="listbox__option listbox__option--disabled" 
     role="option" 
     aria-disabled="true"
     data-sku-value-name="Silver Black - Greekey">
  <span class="listbox__value">Silver Black - Greekey (Out of stock)</span>
  <span class="listbox__description">
    <div class="x-sku-description"></div>
  </span>
</div>
```

---

## CURRENT SCRAPER CODE ISSUES

### Issue 1: Incorrect Group Detection
**Location:** `collect_variant_groups()` function (lines 442-490)

**Problem:**
The scraper looks for three different patterns:
1. `div.vim.x-sku` - ✅ CORRECT (this is what eBay uses)
2. `[data-testid='x-msku__group']` - ❌ NOT FOUND in actual DOM
3. `select[name^='variation']` - ❌ LEGACY, not used in modern eBay

**Current Code:**
```python
def collect_variant_groups(page) -> List[Dict[str, Any]]:
    groups: List[Dict[str, Any]] = []

    # Primary SKU widgets - THIS WORKS
    containers = page.locator("div.vim.x-sku")
    for idx in range(containers.count()):
        container = containers.nth(idx)
        try:
            label = container.locator(".btn__label").inner_text(timeout=1000).strip()
        except PlaywrightTimeoutError:
            label = None
        # ... rest of code
```

**Analysis:**
- The first method (`div.vim.x-sku`) is correct and should work
- However, it's looking for `.btn__label` which is CORRECT
- The issue might be in subsequent option selection logic

### Issue 2: Incorrect Options Selector
**Location:** `select_option_from_group()` function (lines 514-594)

**Problem:**
The scraper looks for options in the wrong container structure.

**Current Code (lines 569-572):**
```python
options = options_container.locator("li[role='option']")
if options.count() == 0:
    options = options_container.locator("div.listbox__option")
```

**Analysis:**
- eBay uses `<div class="listbox__option" role="option">`, NOT `<li>`
- The fallback to `div.listbox__option` should work, but might be delayed
- Should prioritize `div.listbox__option` first

### Issue 3: Incorrect Button Selector
**Location:** `select_option_from_group()` function (lines 540-548)

**Current Code:**
```python
button_locators = [
    locator.locator("span.listbox-button__control"),  # ❌ WRONG - should be button.listbox-button__control
    locator.locator("button[aria-haspopup='listbox']"),  # ✅ CORRECT
]
```

**Analysis:**
- First selector looks for `<span class="listbox-button__control">` which doesn't exist
- Second selector is correct but might not be specific enough
- Should be: `button.listbox-button__control`

### Issue 4: Dropdown Opening Logic
**Location:** `select_option_from_group()` function (lines 556-567)

**Current Code:**
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

**Analysis:**
- The `aria-controls` approach is correct
- However, the options div might already be in the DOM but hidden
- The actual structure shows `div.listbox__options` is a sibling inside the same `span.listbox-button`
- Should look for `.listbox__options` within the parent `span.listbox-button` container

### Issue 5: Option Matching Logic
**Location:** `option_matches()` and `normalize_label()` (lines 418-423)

**Current Code:**
```python
def normalize_label(text: str) -> str:
    return " ".join(text.lower().split())

def option_matches(option_text: str, target: str) -> bool:
    return normalize_label(target) in normalize_label(option_text)
```

**Analysis:**
- This is too strict - it requires exact substring match
- Example: Excel has "Red Black" but eBay shows "Red Black - Greekey"
- The current logic WOULD work for this case (substring match)
- However, might fail on spacing differences like "60 x 110 cm" vs "60x110cm"

### Issue 6: Group Label Matching
**Location:** `find_group_for_dimension()` function (lines 499-511)

**Current Code:**
```python
GROUP_KEYWORDS = {
    "size": ["size", "length", "dimensions"],
    "variation": ["colour", "color", "design", "style", "pattern"],
}
```

**Analysis:**
- This is correct and should work for "Size:" and "Colour:"
- The label detection uses `btn__label` which is correct

---

## ROOT CAUSE ANALYSIS

After detailed inspection, the main issues are:

1. **Button selector priority**: The first button selector is wrong (`span.listbox-button__control` instead of `button.listbox-button__control`)

2. **Options container detection**: The scraper searches for `li[role='option']` first, which doesn't exist. It should search for `div.listbox__option` first.

3. **Dropdown visibility handling**: The options might already be in the DOM but hidden, and the scraper might not be waiting properly for them to become visible after clicking.

4. **Disabled option detection**: The current code checks for:
   - `aria-disabled="true"` ✅ CORRECT
   - `listbox__option--disabled` class ✅ CORRECT
   - "out of stock" in text ✅ CORRECT

---

## RECOMMENDED FIXES

### Fix 1: Correct Button Selector Priority
**File:** `ebay_stock_scraper.py`
**Lines:** 540-548

**Change from:**
```python
button_locators = [
    locator.locator("span.listbox-button__control"),
    locator.locator("button[aria-haspopup='listbox']"),
]
```

**Change to:**
```python
button_locators = [
    locator.locator("button.listbox-button__control"),
    locator.locator("button[aria-haspopup='listbox']"),
]
```

### Fix 2: Prioritize Correct Options Selector
**File:** `ebay_stock_scraper.py`
**Lines:** 569-572

**Change from:**
```python
options = options_container.locator("li[role='option']")
if options.count() == 0:
    options = options_container.locator("div.listbox__option")
```

**Change to:**
```python
options = options_container.locator("div.listbox__option")
if options.count() == 0:
    options = options_container.locator("li[role='option']")
```

### Fix 3: Improve Options Container Detection
**File:** `ebay_stock_scraper.py`
**Lines:** 556-567

**Change from:**
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

**Change to:**
```python
button.click()
page.wait_for_timeout(300)  # Give dropdown time to expand

options_container = locator
# First try to find options within the same listbox-button container
options_in_button = locator.locator("div.listbox__options")
if options_in_button.count() > 0:
    try:
        options_in_button.first.wait_for(state="visible", timeout=2000)
        options_container = options_in_button.first
    except PlaywrightTimeoutError:
        pass

# Fallback to aria-controls method
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

### Fix 4: Better Error Messages
Add more detailed logging to help diagnose issues:

```python
def select_option_from_group(page, group: Dict[str, Any], target_value: str) -> Tuple[bool, Optional[str]]:
    locator = group["locator"]
    group_type = group.get("type", "vim")
    group_label = group.get("label", "unknown")
    
    LOGGER.debug(f"Selecting '{target_value}' from group '{group_label}' (type: {group_type})")
    
    # ... rest of function
```

### Fix 5: Add Data Attribute Matching
Use the `data-sku-value-name` attribute for more reliable matching:

**Add after line 576:**
```python
chosen_option = None
chosen_text = ""

# First try exact match using data attribute
for idx in range(options.count()):
    option = options.nth(idx)
    data_sku_value = option.get_attribute("data-sku-value-name")
    if data_sku_value and option_matches(data_sku_value, target_value):
        chosen_option = option
        chosen_text = option.inner_text().strip()
        LOGGER.debug(f"Matched option via data-sku-value-name: {data_sku_value}")
        break

# Fallback to text matching
if chosen_option is None:
    for idx in range(options.count()):
        option = options.nth(idx)
        text = option.inner_text().strip()
        if option_matches(text, target_value):
            chosen_option = option
            chosen_text = text
            LOGGER.debug(f"Matched option via text: {text}")
            break
```

---

## TESTING RECOMMENDATIONS

1. **Test with --verbose flag** to see detailed logs
2. **Test with --limit 5** to test first 5 rows only
3. **Add screenshots** on failure to see what the scraper is seeing
4. **Test different listings** to ensure the fix works across various eBay layouts

## ADDITIONAL IMPROVEMENTS

1. **Add screenshot capture on error** for debugging
2. **Implement retry logic** for option selection failures
3. **Add validation** to ensure both size and colour are selected before checking availability
4. **Improve availability detection** by checking for "Add to basket" button state

---

## SUMMARY

The scraper is mostly correct in its approach, but has a few critical selector issues:
1. Wrong button selector (`span` instead of `button`)
2. Wrong options selector priority (`li` before `div`)
3. Insufficient wait time after clicking dropdown

These fixes should resolve most of the accuracy issues.
