from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from supabase import create_client
import os
from typing import Optional
import json
import yfinance as yf
from datetime import datetime, timedelta

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
    return {"status": "ok", "message": "Trading Scanner API running"}

@app.post("/api/fundamentals")
async def load_fundamentals():
    try:
        # Get stocks from database or use default list
        try:
            stocks_result = supabase.table('screened_stocks').select('symbol').limit(10).execute()
            symbols = [stock['symbol'] for stock in stocks_result.data]
        except:
            # Fallback to popular Indian and US stocks
            symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'AAPL', 'GOOGL', 'MSFT', 'TSLA']
        
        fundamentals_data = []
        failed_symbols = []
        
        for symbol in symbols:
            try:
                fixed_symbol = fix_symbol(symbol)
                ticker = yf.Ticker(fixed_symbol)
                info = ticker.info
                
                # Check if we got valid data
                if not info or info.get('regularMarketPrice') is None:
                    failed_symbols.append(symbol)
                    continue
                
                fundamentals_data.append({
                    "symbol": symbol,
                    "company_name": info.get('longName', info.get('shortName', f"{symbol} Ltd")),
                    "market_cap": info.get('marketCap', 0),
                    "pe_ratio": info.get('trailingPE', info.get('forwardPE', 0)),
                    "pb_ratio": info.get('priceToBook', 0),
                    "roe": info.get('returnOnEquity', 0),
                    "eps": info.get('trailingEps', info.get('forwardEps', 0)),
                    "sector": info.get('sector', 'Unknown'),
                    "industry": info.get('industry', 'Unknown'),
                    "current_price": info.get('regularMarketPrice', info.get('currentPrice', 0))
                })
                
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                failed_symbols.append(symbol)
                continue
        
        # Store successful data in database
        if fundamentals_data:
            try:
                supabase.table('fundamentals').upsert(fundamentals_data).execute()
            except Exception as e:
                print(f"Database insert error: {e}")
        
        return {
            "message": f"Loaded fundamentals for {len(fundamentals_data)} stocks",
            "count": len(fundamentals_data),
            "data": fundamentals_data,
            "failed_symbols": failed_symbols,
            "success_rate": f"{len(fundamentals_data)}/{len(symbols)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def fix_symbol(symbol: str) -> str:
    """Fix symbol format for different exchanges"""
    # Indian stocks - add .NS for NSE
    indian_stocks = [
        'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK', 'SBIN', 'ITC', 'LT', 
        'KOTAKBANK', 'BHARTIARTL', 'ASIANPAINT', 'MARUTI', 'TITAN', 'NESTLEIND',
        'ULTRACEMCO', 'BAJFINANCE', 'HCLTECH', 'WIPRO', 'TECHM', 'POWERGRID',
        '360ONE', 'ADANIENT', 'ADANIPORTS', 'APOLLOHOSP', 'AXISBANK'
    ]
    
    # Clean symbol first
    clean_symbol = symbol.upper().strip()
    
    if clean_symbol in indian_stocks and not clean_symbol.endswith(('.NS', '.BO')):
        return f"{clean_symbol}.NS"
    return clean_symbol

@app.get("/api/ohlc")
async def get_ohlc(symbol: str, days: int = 30):
    try:
        fixed_symbol = fix_symbol(symbol)
        ticker = yf.Ticker(fixed_symbol)
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        hist = ticker.history(start=start_date, end=end_date)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail=f"No data found for symbol {symbol}")
        
        # Format for lightweight charts
        data = []
        for date, row in hist.iterrows():
            data.append({
                'time': date.strftime('%Y-%m-%d'),
                'open': round(float(row['Open']), 2),
                'high': round(float(row['High']), 2),
                'low': round(float(row['Low']), 2),
                'close': round(float(row['Close']), 2),
                'volume': int(row['Volume'])
            })
        
        return data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/quote/{symbol}")
async def get_quote(symbol: str):
    try:
        fixed_symbol = fix_symbol(symbol)
        ticker = yf.Ticker(fixed_symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "price": info.get('currentPrice', 0),
            "change": info.get('regularMarketChange', 0),
            "change_percent": info.get('regularMarketChangePercent', 0),
            "volume": info.get('regularMarketVolume', 0),
            "market_cap": info.get('marketCap', 0)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test")
async def test_supabase():
    try:
        # Test yfinance
        ticker = yf.Ticker("AAPL")
        info = ticker.info
        
        return {
            "status": "success",
            "message": "YFinance working",
            "sample_data": {
                "symbol": "AAPL",
                "price": info.get('currentPrice', 0),
                "name": info.get('longName', 'Apple Inc.')
            },
            "env_check": {
                "has_url": bool(os.getenv("SUPABASE_URL")),
                "has_key": bool(os.getenv("SUPABASE_SERVICE_ROLE_KEY"))
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
