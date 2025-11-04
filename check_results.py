import pandas as pd

try:
    df = pd.read_excel('test_row46.xlsx')
    print('Results for target rows 45-49:')
    print('='*80)
    target_rows = [45, 46, 47, 48, 49]  # Excel row numbers
    for row_num in target_rows:
        if row_num <= len(df):
            row = df.iloc[row_num-1]  # Convert to 0-based index
            print(f'Row {row_num}:')
            print(f'  Color: {row.get("variation", "N/A")}')
            print(f'  Detected Status: {row.get("detected_status", "N/A")}')
            print(f'  Size: {row.get("size", "N/A")}')
            print(f'  Error: {row.get("error", "None")}')
            print()
except Exception as e:
    print(f'Error reading results: {e}')