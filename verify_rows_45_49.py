#!/usr/bin/env python3

"""Quick test to verify rows 45-49 work with color extraction fix."""

import sys
sys.path.append('.')

from ebay_stock_scraper import load_variants_from_excel
from pathlib import Path

def test_specific_rows():
    # Load records for rows 45-49 (indices 44-48)
    print("Loading Excel data...")
    records = load_variants_from_excel(
        Path("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx"),
        limit=50
    )
    
    print(f"\nLoaded {len(records)} records total")
    print("=" * 80)
    
    # Check rows 45-49 specifically
    target_rows = [44, 45, 46, 47, 48]  # DataFrame indices for Excel rows 45-49
    all_success = True
    
    for idx in target_rows:
        if idx < len(records):
            record = records[idx]
            excel_row = record.excel_row
            print(f"\nExcel Row {excel_row} (DataFrame index {idx}):")
            print(f"  Size: {record.size}")
            print(f"  Extracted Color: {record.variation}")
            print(f"  Product Name: {record.stock_name}")
            
            if not record.variation:
                print(f"  FAIL: No color extracted!")
                all_success = False
            else:
                print(f"  SUCCESS: Color extracted: {record.variation}")
    
    print(f"\n{'=' * 80}")
    if all_success:
        print("FIX VERIFIED: All target rows (45-49) now successfully extract colors!")
        print("The color extraction issue has been resolved.")
    else:
        print("FIX FAILED: Some rows still missing color data.")
    
    return all_success

if __name__ == "__main__":
    success = test_specific_rows()
    print(f"\nTest result: {'PASS' if success else 'FAIL'}")
    sys.exit(0 if success else 1)