import pandas as pd

df = pd.read_excel("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx")
header = df.iloc[0]
df.columns = [str(header.iloc[i]).strip() if isinstance(header.iloc[i], str) and header.iloc[i].strip() else col for i, col in enumerate(df.columns)]
df = df.iloc[1:].reset_index(drop=True)

print("Checking rows 44-47 (Excel rows 45-48):")
print("="*100)

for idx in [43, 44, 45, 46]:  # Zero-based, so 43 = Excel row 45
    row = df.iloc[idx]
    print(f"\nRow {idx+2} (Excel row {idx+3}):")
    print(f"  Product Name: {row.get('Product Name', 'N/A')}")
    print(f"  Colour: {row.get('Colour', 'N/A')}")
    print(f"  SIZE: {row.get('SIZE', 'N/A')}")
    print(f"  STATUS: {row.get('STATUS', row.get('INSTOCK/OUTOFSTOCK', 'N/A'))}")
    print(f"  LISTING LINK: {row.get('LISTING LINK', 'N/A')}")
