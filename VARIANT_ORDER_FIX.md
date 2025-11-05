# Critical Fix: Variant Selector Order Independence

## Problem Discovered (2025-11-05)

After fixing the cross-seller naming convention issue, discovered a second critical bug: the scraper assumed all eBay listings present variant selectors in the same order (Size first, Colour second).

### The Issue

Different eBay listings present their variant selectors in different orders:

**Listing 363486576357 (Size first, Colour second):**
```json
{
  "groups": [
    {"type": "vim", "label": "Size:", "order": 0},
    {"type": "vim", "label": "Colour:", "order": 1}
  ]
}
```

**Listing 364946395670 (Colour first, Size second):**
```json
{
  "groups": [
    {"type": "vim", "label": "Colour:", "order": 0},
    {"type": "vim", "label": "Size:", "order": 1}
  ]
}
```

### Previous Broken Logic

The original code at lines 882-890 hardcoded the selection order:

```python
# BROKEN: Always tries colour first, then size
dimensions: List[Tuple[str, str]] = []
if record.variation:
    dimensions.append(("variation", str(record.variation)))  # Always first
if record.size:
    dimensions.append(("size", str(record.size)))  # Always second
```

**Problem:**
- For listing 363486576357: Tried to select colour first (group 1 = Size) → MISMATCH → ERROR
- For listing 364946395670: Tried to select colour first (group 0 = Colour) → MATCH → SUCCESS

Only listings where colour happened to be group 0 would work correctly.

## The Solution

### New Order-Agnostic Algorithm

The fix implements a three-step process:

1. **Discover group indices**: For each dimension (size, colour), find which group index it corresponds to on the page
2. **Sort by page order**: Sort dimensions by their actual group index
3. **Process in page order**: Select variants in the order they appear on the page

### Implementation

```python
# Step 1: Build list of (group_idx, dim_type, dim_value)
dimensions_with_group: List[Tuple[int, str, str]] = []

if record.variation:
    group_idx = find_group_for_dimension(groups, "variation", set())
    if group_idx is not None:
        dimensions_with_group.append((group_idx, "variation", str(record.variation)))

if record.size:
    group_idx = find_group_for_dimension(groups, "size", set())
    if group_idx is not None:
        dimensions_with_group.append((group_idx, "size", str(record.size)))

# Step 2: Sort by group index (page order)
dimensions_with_group.sort(key=lambda x: x[0])

# Step 3: Process in sorted order
for group_idx, dim_type, dim_value in dimensions_with_group:
    # Select variant...
```

### How It Works

**For listing 363486576357 (Size=0, Colour=1):**
```python
dimensions_with_group = [
    (0, "size", "40 x 60 cm"),     # Size is group 0
    (1, "variation", "Silver Black")  # Colour is group 1
]
# After sort: [(0, size), (1, variation)] → Process size first, then colour ✅
```

**For listing 364946395670 (Colour=0, Size=1):**
```python
dimensions_with_group = [
    (0, "variation", "Red - Rome"),  # Colour is group 0
    (1, "size", "60 x 110 cm")       # Size is group 1
]
# After sort: [(0, variation), (1, size)] → Process colour first, then size ✅
```

## Testing the Fix

### Before Fix
```
Listing 363486576357: ❌ Tried colour first → Failed to match size group
Listing 364946395670: ✅ Tried colour first → Matched correctly
```

### After Fix
```
Listing 363486576357: ✅ Processes size (group 0) → colour (group 1)
Listing 364946395670: ✅ Processes colour (group 0) → size (group 1)
```

## Benefits

1. **Universal compatibility**: Works regardless of variant selector order
2. **Robust**: Adapts to any future eBay layout changes that reorder groups
3. **Clear logging**: Debug logs now show: `"Processing dimensions in page order: [('size', '40 x 60 cm'), ('variation', 'Silver Black')]"`

## How to Update

```cmd
cd C:\Users\yasir\Downloads\scrapper-master\scrapper-master
git pull origin master
.venv\Scripts\activate
python ebay_stock_scraper.py --excel "ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx" --engine chromium --delay 3 --retries 2 --output "results_run.xlsx" --copy-sheet "sheet_run.xlsx"
```

## Combined with Previous Fix

This fix works in conjunction with the cross-seller naming convention fix. Together they enable the scraper to:

1. ✅ Handle different seller naming conventions (e.g., "Silver - Gel Back 59" vs "Silver Black - Greekey")
2. ✅ Handle different variant selector orders (Colour-Size vs Size-Colour)
3. ✅ Extract base sizes stripping imperial measurements
4. ✅ Process all eBay listings regardless of seller or layout

---
_Diagnosed using Chrome DevTools MCP to inspect variant group ordering across multiple listings._
