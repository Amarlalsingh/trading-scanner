from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
import pandas as pd
from datetime import date, datetime
import os
from dotenv import load_dotenv

from .supabase_client import get_supabase_client
from .models import StockScore, Insight, Signal
from .ingest import ingest_daily_data
from .scanner import run_insights_for_symbol
from .fundamentals import load_equity_list_and_fetch_fundamentals

load_dotenv()

app = FastAPI(title="Trading Scanner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/api/ohlc")
async def get_ohlc(symbol: str, from_date: Optional[str] = None, to_date: Optional[str] = None):
    """Get OHLC data for lightweight charts"""
    supabase = get_supabase_client()
    
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

@app.get("/api/insights")
async def get_insights(symbol: str, date: Optional[str] = None):
    """Get insights for a symbol"""
    supabase = get_supabase_client()
    
    query = supabase.table('insights').select('''
        *,
        insight_types(code, name, category),
        insight_images(img_url, meta)
    ''').eq('symbol', symbol)
    
    if date:
        query = query.eq('detected_on', date)
    
    result = query.order('detected_on', desc=True).execute()
    return result.data

@app.get("/api/signals")
async def get_signals(since: Optional[str] = None, limit: int = 50):
    """Get recent trade signals"""
    supabase = get_supabase_client()
    
    query = supabase.table('detected_signals').select('''
        *,
        chart_images(img_url, meta)
    ''')
    
    if since:
        query = query.gte('detected_on', since)
    
    result = query.order('detected_on', desc=True).limit(limit).execute()
    return result.data

@app.get("/api/stock_score")
async def get_stock_score(symbol: str, date: Optional[str] = None):
    """Get combined score for a stock"""
    if not date:
        date = datetime.now().date().isoformat()
    
    supabase = get_supabase_client()
    result = supabase.table('stock_daily_scores').select('*').eq('symbol', symbol).eq('date', date).execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Score not found")
    
    return result.data[0]

@app.post("/api/upload-screened")
async def upload_screened_stocks(file: UploadFile = File(...)):
    """Upload screened stocks CSV"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV")
    
    content = await file.read()
    df = pd.read_csv(pd.io.common.StringIO(content.decode('utf-8')))
    
    # Expect columns: Symbol, Exchange (optional)
    if 'Symbol' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV must have 'Symbol' column")
    
    supabase = get_supabase_client()
    
    stocks = []
    for _, row in df.iterrows():
        stocks.append({
            'symbol': row['Symbol'],
            'exchange': row.get('Exchange', 'NSE'),
            'meta': {}
        })
    
    result = supabase.table('screened_stocks').upsert(stocks).execute()
    return {"message": f"Uploaded {len(stocks)} stocks", "count": len(stocks)}

@app.post("/api/trigger_backfill")
async def trigger_backfill(symbol: Optional[str] = None):
    """Trigger data backfill for symbol(s)"""
    try:
        if symbol:
            await ingest_daily_data([symbol])
            return {"message": f"Backfill triggered for {symbol}"}
        else:
            # Get all screened stocks
            supabase = get_supabase_client()
            result = supabase.table('screened_stocks').select('symbol').execute()
            symbols = [row['symbol'] for row in result.data]
            
            await ingest_daily_data(symbols)
            return {"message": f"Backfill triggered for {len(symbols)} symbols"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/fundamentals")
async def get_fundamentals(symbol: Optional[str] = None, sector: Optional[str] = None):
    """Get fundamental data"""
    supabase = get_supabase_client()
    
    query = supabase.table('fundamentals').select('*')
    
    if symbol:
        query = query.eq('symbol', symbol)
    if sector:
        query = query.eq('sector', sector)
    
    result = query.order('market_cap', desc=True).execute()
    return result.data

@app.post("/api/load_fundamentals")
async def load_fundamentals():
    """Load EQUITY_L.csv and fetch fundamentals"""
    try:
        await load_equity_list_and_fetch_fundamentals("/Users/singhxss/Desktop/Amar Personal/EQUITY_L.csv")
        return {"message": "Fundamentals loading completed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/run_scanner")
async def run_scanner(symbol: Optional[str] = None):
    """Run insight scanner for symbol(s)"""
    try:
        if symbol:
            await run_insights_for_symbol(symbol)
            return {"message": f"Scanner completed for {symbol}"}
        else:
            # Run for all screened stocks
            supabase = get_supabase_client()
            result = supabase.table('screened_stocks').select('symbol').execute()
            
            for row in result.data:
                await run_insights_for_symbol(row['symbol'])
            
            return {"message": f"Scanner completed for {len(result.data)} symbols"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
