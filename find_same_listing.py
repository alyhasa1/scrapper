import pandas as pd

df = pd.read_excel("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx")
header = df.iloc[0]
df.columns = [str(header.iloc[i]).strip() if isinstance(header.iloc[i], str) and header.iloc[i].strip() else col for i, col in enumerate(df.columns)]
df = df.iloc[1:].reset_index(drop=True)

# Find all rows with the same listing URL as rows 45-49
target_url = "https://www.ebay.co.uk/itm/363486576357?var=633227768703"

print("Looking for rows with the same listing URL:")
print("="*100)

same_listing_rows = df[df['LISTING LINK'] == target_url]

print(f"Found {len(same_listing_rows)} rows with the same listing URL:")
for idx, row in same_listing_rows.iterrows():
    excel_row = idx + 2  # Excel row number (1-based + header row)
    print(f"\nRow {excel_row} (DataFrame index {idx}):")
    print(f"  Product Name: {row.get('Product Name', 'N/A')}")
    print(f"  Colour: {row.get('Colour', 'N/A')}")
    print(f"  SIZE: {row.get('SIZE', 'N/A')}")
    print(f"  STATUS: {row.get('STATUS', 'N/A')}")