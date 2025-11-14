import os
from supabase import create_client, Client
from typing import Optional

_supabase_client: Optional[Client] = None

def get_supabase_client() -> Client:
    """Get Supabase client singleton"""
    global _supabase_client
    
    if _supabase_client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        
        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        
        _supabase_client = create_client(url, key)
    
    return _supabase_client

def upsert_daily_candles(symbol: str, candles_data: list) -> dict:
    """Upsert daily candles data"""
    supabase = get_supabase_client()
    
    # Prepare data for upsert
    rows = []
    for candle in candles_data:
        rows.append({
            'symbol': symbol,
            'ts': candle['date'],
            'open': candle['open'],
            'high': candle['high'],
            'low': candle['low'],
            'close': candle['close'],
            'volume': candle['volume']
        })
    
    result = supabase.table('daily_candles').upsert(rows).execute()
    return result

def get_last_candle_date(symbol: str) -> Optional[str]:
    """Get the last candle date for a symbol"""
    supabase = get_supabase_client()
    
    result = supabase.table('daily_candles')\
        .select('ts')\
        .eq('symbol', symbol)\
        .order('ts', desc=True)\
        .limit(1)\
        .execute()
    
    if result.data:
        return result.data[0]['ts']
    return None

def get_candles_for_symbol(symbol: str, days: int = 100) -> list:
    """Get recent candles for a symbol"""
    supabase = get_supabase_client()
    
    result = supabase.table('daily_candles')\
        .select('*')\
        .eq('symbol', symbol)\
        .order('ts', desc=True)\
        .limit(days)\
        .execute()
    
    # Return in chronological order
    return list(reversed(result.data))

def insert_insight(insight_data: dict) -> dict:
    """Insert or update an insight"""
    supabase = get_supabase_client()
    result = supabase.table('insights').upsert(insight_data).execute()
    return result

def insert_signal(signal_data: dict) -> dict:
    """Insert a detected signal"""
    supabase = get_supabase_client()
    result = supabase.table('detected_signals').insert(signal_data).execute()
    return result

def upsert_stock_score(score_data: dict) -> dict:
    """Upsert stock daily score"""
    supabase = get_supabase_client()
    result = supabase.table('stock_daily_scores').upsert(score_data).execute()
    return result
