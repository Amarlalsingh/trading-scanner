import pandas as pd
import yfinance as yf
import time
from typing import List, Dict, Optional
from .supabase_client import get_supabase_client

def fetch_fundamentals(symbol: str) -> Dict:
    """Fetch fundamental data for a symbol using yfinance"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info

        return {
            "symbol": symbol,
            "company_name": info.get("longName"),
            "market_cap": info.get("marketCap"),
            "roe": info.get("returnOnEquity"),
            "pe_ratio": info.get("trailingPE"),
            "pb_ratio": info.get("priceToBook"),
            "eps": info.get("trailingEps"),
            "industry": info.get("industry"),
            "sector": info.get("sector"),
            "meta": {
                "dividend_yield": info.get("dividendYield"),
                "book_value": info.get("bookValue"),
                "price_to_sales": info.get("priceToSalesTrailing12Months")
            }
        }
    except Exception as e:
        print(f"Error fetching {symbol}: {e}")
        return {"symbol": symbol, "error": str(e)}

def upsert_fundamentals(fundamentals_data: List[Dict]) -> Dict:
    """Upsert fundamentals data to database"""
    supabase = get_supabase_client()
    
    # Filter out error records
    valid_data = [f for f in fundamentals_data if "error" not in f]
    
    if valid_data:
        result = supabase.table('fundamentals').upsert(valid_data).execute()
        return result
    
    return {"data": []}

async def load_equity_list_and_fetch_fundamentals(csv_path: str = "EQUITY_L.csv"):
    """Load EQUITY_L.csv and fetch fundamentals for all symbols"""
    
    # Load CSV
    df = pd.read_csv(csv_path)
    symbols = df["SYMBOL"].tolist()
    
    print(f"Loading fundamentals for {len(symbols)} symbols...")
    
    # First, add all symbols to screened_stocks
    supabase = get_supabase_client()
    stocks_data = [{"symbol": sym, "exchange": "NSE"} for sym in symbols]
    supabase.table('screened_stocks').upsert(stocks_data).execute()
    
    # Fetch fundamentals in batches
    batch_size = 50
    all_fundamentals = []
    
    for i in range(0, len(symbols), batch_size):
        batch = symbols[i:i + batch_size]
        print(f"Processing batch {i//batch_size + 1}/{(len(symbols)-1)//batch_size + 1}")
        
        batch_fundamentals = []
        for symbol in batch:
            fundamentals = fetch_fundamentals(symbol)
            if "error" not in fundamentals:
                batch_fundamentals.append(fundamentals)
            time.sleep(0.1)  # Rate limiting
        
        # Upsert batch
        if batch_fundamentals:
            upsert_fundamentals(batch_fundamentals)
            all_fundamentals.extend(batch_fundamentals)
        
        time.sleep(1)  # Batch delay
    
    print(f"Completed: {len(all_fundamentals)} fundamentals stored")
    return all_fundamentals

if __name__ == "__main__":
    import asyncio
    asyncio.run(load_equity_list_and_fetch_fundamentals())
