# Critical Fix: Cross-Seller Variant Matching

## Problem Discovered (2025-11-05)

After 40+ hours of development, identified the root cause of variant matching failures when scraping listings from different eBay sellers.

### The Issue

Different eBay sellers use completely different naming conventions for their colour and size variants:

**Listing 363486576357 (timstex seller):**
- Colours: `"Silver Black - Greekey"`, `"Black Grey - Greekey"`, `"Red Black - Greekey"`
- Sizes: `"40 x 60 cm"`, `"50 x 80 cm"`, `"60 x 110 cm"`

**Listing 363338958236 (Bedding World seller):**
- Colours: `"Silver - Gel Back 59"`, `"Grey - Gel Back 59"`, `"Red - Gel Back 59"`, `"Beige - Gel Back 59"`
- Sizes: `"40 x 60 cm (1 ft 4 in x 2 ft)"`, `"50 x 80 cm (1 ft 8 in x 2 ft 4 in)"`

When your Excel sheet contains colour names from one seller format (e.g., `"Silver Black - Greekey"`), the scraper would fail to match these against a different seller's naming convention (e.g., `"Silver - Gel Back 59"`).

## The Solution

Enhanced the `option_matches()` function with two new helpers:

### 1. `extract_base_colour(colour_text)`
Extracts the base colour name by removing seller-specific suffixes:
- `"Silver Black - Greekey"` → `"silver black"`
- `"Silver - Gel Back 59"` → `"silver"`
- `"Beige - MR (41)"` → `"beige"`

### 2. `extract_base_size(size_text)`
Removes imperial measurements and extra text from sizes:
- `"40 x 60 cm (1 ft 4 in x 2 ft)"` → `"40 x 60 cm"`
- `"50 x 80 cm (1 ft 8 in x 2 ft 4 in) Most popular"` → `"50 x 80 cm"`

### Matching Strategy
The improved `option_matches()` now:
1. First tries exact substring matching (fast path)
2. For colour-like options (contains " - "), extracts and compares base colour names
3. For size-like options (contains "cm" or "x"), strips imperial measurements and compares
4. Uses flexible partial matching to handle variations

## Testing the Fix

### Before Fix
```
Row 1 (listing 363486576357): ✅ Silver Black - Greekey matched
Row 2 (listing 363338958236): ❌ Silver Black - Greekey NOT found (only has "Silver - Gel Back 59")
```

### After Fix
```
Row 1 (listing 363486576357): ✅ Silver Black - Greekey matched
Row 2 (listing 363338958236): ✅ Silver Black → Silver (base match)
```

## How to Update

Your friend should:
1. Pull the latest code: `git pull origin master`
2. Reactivate venv: `.venv\Scripts\activate`
3. Rerun the scraper on the full sheet

The scraper will now intelligently match colour names across different seller conventions.

## Important Note

This fix handles the **technical** matching problem. If your Excel sheet uses completely unrelated colour names to what's on eBay (e.g., sheet says "Blue" but eBay only has "Silver" and "Grey"), the match will still fail—which is correct behavior.

For best results, ensure the base colour names in your sheet roughly match what's available on each listing, even if the full suffix differs.

---
_Diagnosed using Chrome DevTools MCP to compare DOM structure between working and failing listings._
