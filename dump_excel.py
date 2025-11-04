import pandas as pd

df = pd.read_excel("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx")

print("First 50 rows, all columns:")
print("="*120)
print(df.iloc[0:50].to_string())
