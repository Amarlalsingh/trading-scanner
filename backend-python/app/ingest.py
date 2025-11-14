import os
import pandas as pd
from datetime import datetime, date, timedelta
from typing import List, Optional
from ShoonyaApi import NorenApi
import time

from .supabase_client import get_supabase_client, upsert_daily_candles, get_last_candle_date

class ShoonyaClient:
    def __init__(self):
        self.api = NorenApi()
        self.logged_in = False
        
    def login(self):
        """Login to Shoonya API"""
        try:
            result = self.api.login(
                userid=os.getenv("SHOONYA_USERID"),
                password=os.getenv("SHOONYA_PASSWORD"),
                twoFA=os.getenv("SHOONYA_2FA"),
                vendor_code=os.getenv("SHOONYA_VENDOR_CODE"),
                api_secret=os.getenv("SHOONYA_API_SECRET"),
                imei=os.getenv("SHOONYA_IMEI")
            )
            
            if result and result.get('stat') == 'Ok':
                self.logged_in = True
                print("Shoonya login successful")
                return True
            else:
                print(f"Shoonya login failed: {result}")
                return False
                
        except Exception as e:
            print(f"Shoonya login error: {e}")
            return False
    
    def get_token_for_symbol(self, symbol: str, exchange: str = "NSE") -> Optional[str]:
        """Get Shoonya token for a symbol"""
        try:
            result = self.api.searchscrip(exchange=exchange, searchtext=symbol)
            
            if result and isinstance(result, list) and len(result) > 0:
                # Find exact match
                for item in result:
                    if item.get('tsym') == symbol:
                        return item.get('token')
                
                # If no exact match, return first result
                return result[0].get('token')
            
            return None
            
        except Exception as e:
            print(f"Error getting token for {symbol}: {e}")
            return None
    
    def fetch_daily_data(self, token: str, from_date: str, to_date: str) -> Optional[pd.DataFrame]:
        """Fetch daily OHLC data from Shoonya"""
        try:
            result = self.api.get_daily_price_series(
                exchange="NSE",
                token=token,
                fromdate=from_date,
                todate=to_date
            )
            
            if not result:
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(result)
            
            if df.empty:
                return None
            
            # Standardize column names
            df = df.rename(columns={
                'time': 'date',
                'into': 'open',
                'inth': 'high',
                'intl': 'low',
                'intc': 'close',
                'intv': 'volume'
            })
            
            # Convert date format
            df['date'] = pd.to_datetime(df['date']).dt.date
            
            # Convert numeric columns
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return df
            
        except Exception as e:
            print(f"Error fetching daily data: {e}")
            return None

async def ingest_daily_data(symbols: List[str]):
    """Ingest daily data for given symbols"""
    shoonya = ShoonyaClient()
    
    if not shoonya.login():
        raise Exception("Failed to login to Shoonya")
    
    supabase = get_supabase_client()
    
    for symbol in symbols:
        try:
            print(f"Processing {symbol}...")
            
            # Get token for symbol
            token = shoonya.get_token_for_symbol(symbol)
            if not token:
                print(f"Could not find token for {symbol}")
                continue
            
            # Update token in screened_stocks
            supabase.table('screened_stocks').update({
                'meta': {'token': token}
            }).eq('symbol', symbol).execute()
            
            # Get last candle date
            last_date = get_last_candle_date(symbol)
            
            if last_date:
                # Incremental update
                from_date = (datetime.strptime(last_date, '%Y-%m-%d').date() + timedelta(days=1)).strftime('%Y-%m-%d')
            else:
                # Full backfill (2 years)
                from_date = (date.today() - timedelta(days=730)).strftime('%Y-%m-%d')
            
            to_date = date.today().strftime('%Y-%m-%d')
            
            print(f"Fetching data for {symbol} from {from_date} to {to_date}")
            
            # Fetch data
            df = shoonya.fetch_daily_data(token, from_date, to_date)
            
            if df is not None and not df.empty:
                # Convert to list of dicts
                candles_data = df.to_dict('records')
                
                # Upsert to database
                result = upsert_daily_candles(symbol, candles_data)
                print(f"Upserted {len(candles_data)} candles for {symbol}")
            else:
                print(f"No data found for {symbol}")
            
            # Rate limiting
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

if __name__ == "__main__":
    import asyncio
    
    # Test with a single symbol
    asyncio.run(ingest_daily_data(["RELIANCE"]))
