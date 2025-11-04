import subprocess
import sys

# Test row 46: 60 x 110 cm + Green Cream - Greekey (should be OUT_OF_STOCK)
cmd = [
    sys.executable,
    "ebay_stock_scraper.py",
    "--excel", "ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx",
    "--engine", "chromium",
    "--chromium-profile", "./chromium_profile",
    "--limit", "47",  # Process up to row 47
    "--verbose",
    "--delay", "3",
    "--output", "test_row46.xlsx"
]

print("Testing row 46 (60 x 110 cm + Green Cream - Greekey)")
print("This should detect OUT_OF_STOCK")
print("=" * 80)

subprocess.run(cmd)
