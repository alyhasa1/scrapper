import pandas as pd
from pathlib import Path

path = Path("ECOMWITH YASIR STOCK PRODUCTS SHEET (1).xlsx")

raw = pd.read_excel(path)
header = raw.iloc[0]
data = raw.iloc[1:].reset_index(drop=True)
data.columns = [header.iloc[i].strip() if isinstance(header.iloc[i], str) and header.iloc[i].strip() else raw.columns[i] for i in range(len(raw.columns))]

cols = [
    "Sr No",
    "STOCK NAME",
    "VARIATION",
    "Size / Pack/TYPE",
    "DIMENSIONS",
    "INSTOCK/OUTOFSTOCK",
    "ITEM NUMBER",
    "LISTING LINK",
]
print(data[cols].head(10))
