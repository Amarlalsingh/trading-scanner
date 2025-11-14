import pandas as pd
import json

# Read EQUITY_L.csv
df = pd.read_csv('backend-python/EQUITY_L.csv')

print('-- Load all NSE stocks from EQUITY_L.csv')
print('INSERT INTO screened_stocks (symbol, exchange, meta) VALUES')

for i, row in df.iterrows():
    symbol = row['SYMBOL'].replace("'", "''")
    company = row['NAME OF COMPANY'].replace("'", "''")
    series = row[' SERIES'].strip()
    
    meta = json.dumps({
        "company_name": company,
        "series": series,
        "isin": row['ISIN NUMBER']
    })
    
    comma = ',' if i < len(df) - 1 else ';'
    print(f"('{symbol}', 'NSE', '{meta}'::jsonb){comma}")

print(f'\n-- Total stocks: {len(df)}')
