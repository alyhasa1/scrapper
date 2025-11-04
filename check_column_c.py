import pandas as pd
import numpy as np

df = pd.read_excel("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx")

print("Raw data for rows 44-48 (Excel rows 45-49), Column C:")
print("="*80)
for i in range(44, 49):
    val = df.iloc[i, 2]  # Column C is index 2
    print(f"Row {i+1} (Excel {i+2}): {val if not pd.isna(val) else '(empty)'}")
