import pandas as pd

results = pd.read_excel('results_top15.xlsx')
print(results[['row_index', 'listing_url', 'detected_status', 'error']])
print('\nSummary:')
print(results['detected_status'].value_counts())

copy_df = pd.read_excel('sheet_top15_updated.xlsx', header=None)
print('\nUpdated sheet preview:')
print(copy_df.head(10))
