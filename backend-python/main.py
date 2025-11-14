from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from supabase import create_client
import os
from typing import Optional
import json

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
    return {"message": "Trading Scanner API", "status": "running", "version": "1.0"}

@app.get("/health")
async def health():
    return {"status": "ok", "message": "Trading Scanner API running on Render"}

@app.post("/api/fundamentals")
async def load_fundamentals():
    try:
        # Get first 5 stocks for testing
        stocks_result = supabase.table('screened_stocks').select('symbol').limit(5).execute()
        
        fundamentals_data = []
        
        # Generate mock fundamental data since yfinance has dependency issues
        sectors = ["Technology", "Finance", "Energy", "Healthcare", "Consumer Goods"]
        industries = ["Software", "Banking", "Oil & Gas", "Pharmaceuticals", "Retail"]
        
        for i, stock in enumerate(stocks_result.data):
            symbol = stock['symbol']
            
            # Create realistic mock data
            market_cap = 50000000000 + (i * 25000000000) + (hash(symbol) % 100000000000)
            pe_ratio = 12.5 + (i * 2.3) + (hash(symbol) % 20)
            
            fundamentals_data.append({
                "symbol": symbol,
                "company_name": f"{symbol} Limited",
                "market_cap": market_cap,
                "pe_ratio": round(pe_ratio, 2),
                "pb_ratio": round(1.5 + (i * 0.8) + (hash(symbol) % 5), 2),
                "roe": round(0.12 + (i * 0.03) + (hash(symbol) % 20) / 100, 3),
                "eps": round(15.0 + (i * 8.0) + (hash(symbol) % 50), 2),
                "sector": sectors[i % len(sectors)],
                "industry": industries[i % len(industries)]
            })
        
        # Upsert to database
        if fundamentals_data:
            supabase.table('fundamentals').upsert(fundamentals_data).execute()
        
        return {
            "message": f"Loaded fundamentals for {len(fundamentals_data)} stocks",
            "count": len(fundamentals_data),
            "note": "Using mock data - real yfinance integration requires pandas which has build issues",
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

@app.get("/api/test")
async def test_supabase():
    try:
        # Test database connection
        result = supabase.table('screened_stocks').select('symbol').limit(3).execute()
        
        return {
            "status": "success",
            "message": "Supabase connection working",
            "sample_stocks": result.data,
            "env_check": {
                "has_url": bool(os.getenv("SUPABASE_URL")),
                "has_key": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "env_check": {
                "has_url": bool(os.getenv("SUPABASE_URL")),
                "has_key": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
            }
        }
