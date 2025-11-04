#!/usr/bin/env python3

"""Test script to verify color extraction for rows 45-49."""

import sys
sys.path.append('.')

from ebay_stock_scraper import load_variants_from_excel
from pathlib import Path

def test_color_extraction():
    # Load records for rows 45-49 (indices 44-48)
    print("Loading Excel data...")
    records = load_variants_from_excel(
        Path("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx"),
        limit=50
    )
    
    print(f"\nLoaded {len(records)} records total")
    print("=" * 80)
    
    # Check rows 45-49 (indices 44-48)
    target_rows = [44, 45, 46, 47, 48]  # Excel rows 45-49
    problem_rows = []
    
    for idx in target_rows:
        if idx < len(records):
            record = records[idx]
            excel_row = record.excel_row
            print(f"\nExcel Row {excel_row} (DataFrame index {idx}):")
            print(f"  Listing URL: {record.listing_url}")
            print(f"  Product Name: {record.stock_name}")
            print(f"  Size: {record.size}")
            print(f"  Extracted Color: {record.variation}")
            print(f"  Sheet Status: {record.sheet_stock_status}")
            
            if not record.variation:
                problem_rows.append(excel_row)
                print(f"  PROBLEM: No color extracted!")
            else:
                print(f"  SUCCESS: Color extracted: {record.variation}")
    
    print(f"\n{'=' * 80}")
    if problem_rows:
        print(f"PROBLEM ROWS: {problem_rows}")
        print("Color extraction failed for these rows")
    else:
        print("ALL SUCCESS: Color extraction worked for all target rows")
    
    return len(problem_rows) == 0

if __name__ == "__main__":
    success = test_color_extraction()
    sys.exit(0 if success else 1)