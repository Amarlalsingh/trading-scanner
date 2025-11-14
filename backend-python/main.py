from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
from supabase import create_client
import os
from typing import Optional

app = FastAPI(title="Trading Scanner API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase client
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY")
)

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Trading Scanner API running on Deta Space"}

@app.post("/api/fundamentals")
async def load_fundamentals():
    try:
        # Get first 10 stocks
        stocks_result = supabase.table('screened_stocks').select('symbol').limit(10).execute()
        
        fundamentals_data = []
        errors = []
        
        for stock in stocks_result.data:
            symbol = stock['symbol']
            try:
                # Try different ticker formats
                for suffix in ['.NS', '.BO', '']:
                    try:
                        ticker = yf.Ticker(f"{symbol}{suffix}")
                        info = ticker.info
                        
                        if info and info.get('symbol'):
                            fundamentals_data.append({
                                "symbol": symbol,
                                "company_name": info.get("longName") or info.get("shortName"),
                                "market_cap": info.get("marketCap"),
                                "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                                "pb_ratio": info.get("priceToBook"),
                                "roe": info.get("returnOnEquity"),
                                "eps": info.get("trailingEps"),
                                "sector": info.get("sector"),
                                "industry": info.get("industry")
                            })
                            break
                    except:
                        continue
                else:
                    errors.append(f"Failed to fetch {symbol}")
                    
            except Exception as e:
                errors.append(f"Error with {symbol}: {str(e)}")
        
        # Upsert to database
        if fundamentals_data:
            supabase.table('fundamentals').upsert(fundamentals_data).execute()
        
        return {
            "message": f"Loaded fundamentals for {len(fundamentals_data)} stocks",
            "count": len(fundamentals_data),
            "errors": errors[:5],
            "sample_data": fundamentals_data[:2]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ohlc")
async def get_ohlc(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None):
    try:
        query = supabase.table('daily_candles').select('*').eq('symbol', symbol)
        
        if from_date:
            query = query.gte('ts', from_date)
        if to_date:
            query = query.lte('ts', to_date)
        
        result = query.order('ts').execute()
        
        # Format for lightweight charts
        data = []
        for row in result.data:
            data.append({
                'time': row['ts'],
                'open': row['open'],
                'high': row['high'],
                'low': row['low'],
                'close': row['close'],
                'volume': row['volume']
            })
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
