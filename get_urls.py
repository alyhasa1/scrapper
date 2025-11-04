import pandas as pd

df = pd.read_excel("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx")
print("Columns:", df.columns.tolist()[:10])
print("\nFirst row (headers):")
print(df.iloc[0].tolist()[:10])

header_row = df.iloc[0]
df.columns = [str(header_row.iloc[i]).strip() if isinstance(header_row.iloc[i], str) and header_row.iloc[i].strip() else col for i, col in enumerate(df.columns)]
df = df.iloc[1:]

print("\nNew columns:", df.columns.tolist()[:10])

link_col = [c for c in df.columns if "LINK" in str(c).upper()]
if link_col:
    print(f"\nFound link column: {link_col[0]}")
    urls = df[link_col[0]].dropna().head(3).tolist()
    for url in urls:
        print(url)
