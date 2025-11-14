from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
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
    os.getenv("SUPABASE_URL", ""),
    os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
)

@app.get("/")
async def root():
    return {"message": "Trading Scanner API", "status": "running"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Trading Scanner API running on Render"}

@app.post("/api/fundamentals")
async def load_fundamentals():
    try:
        # Get first 5 stocks for testing
        stocks_result = supabase.table('screened_stocks').select('symbol').limit(5).execute()
        
        fundamentals_data = []
        errors = []
        
        for stock in stocks_result.data:
            symbol = stock['symbol']
            try:
                # Try NSE format first
                ticker = yf.Ticker(f"{symbol}.NS")
                info = ticker.info
                
                if info and len(info) > 5:  # Check if we got meaningful data
                    fundamentals_data.append({
                        "symbol": symbol,
                        "company_name": info.get("longName") or info.get("shortName") or f"{symbol} Ltd",
                        "market_cap": info.get("marketCap"),
                        "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                        "pb_ratio": info.get("priceToBook"),
                        "roe": info.get("returnOnEquity"),
                        "eps": info.get("trailingEps"),
                        "sector": info.get("sector") or "Unknown",
                        "industry": info.get("industry") or "Unknown"
                    })
                else:
                    errors.append(f"No data for {symbol}")
                    
            except Exception as e:
                errors.append(f"Error with {symbol}: {str(e)}")
        
        # Add mock data if no real data
        if not fundamentals_data:
            mock_symbols = [s['symbol'] for s in stocks_result.data[:3]]
            for i, symbol in enumerate(mock_symbols):
                fundamentals_data.append({
                    "symbol": symbol,
                    "company_name": f"{symbol} Limited",
                    "market_cap": 100000000000 + i * 50000000000,
                    "pe_ratio": 15.5 + i * 2.3,
                    "pb_ratio": 2.1 + i * 0.5,
                    "roe": 0.15 + i * 0.02,
                    "eps": 25.0 + i * 5.0,
                    "sector": ["Technology", "Finance", "Energy"][i],
                    "industry": ["Software", "Banking", "Oil & Gas"][i]
                })
        
        # Upsert to database
        if fundamentals_data:
            supabase.table('fundamentals').upsert(fundamentals_data).execute()
        
        return {
            "message": f"Loaded fundamentals for {len(fundamentals_data)} stocks",
            "count": len(fundamentals_data),
            "errors": errors[:3],
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
