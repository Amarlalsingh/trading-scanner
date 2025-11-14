import csv
import json

print('-- Load all NSE stocks from EQUITY_L.csv')
print('INSERT INTO screened_stocks (symbol, exchange, meta) VALUES')

with open('backend-python/EQUITY_L.csv', 'r') as file:
    reader = csv.DictReader(file)
    rows = list(reader)
    
    for i, row in enumerate(rows):
        symbol = row['SYMBOL'].replace("'", "''")
        company = row['NAME OF COMPANY'].replace("'", "''")
        series = row[' SERIES'].strip()
        
        meta = json.dumps({
            "company_name": company,
            "series": series,
            "isin": row[' ISIN NUMBER']
        })
        
        comma = ',' if i < len(rows) - 1 else ';'
        print(f"('{symbol}', 'NSE', '{meta}'::jsonb){comma}")

print(f'\n-- Total stocks: {len(rows)}')
