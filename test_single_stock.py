#!/usr/bin/env python3
"""
Simple script to test the trading scanner for a single stock
"""
import os
import sys
import requests
from supabase import create_client
import json

# Add the backend directory to path
sys.path.append('/Users/singhxss/Desktop/Personal/trading-scanner/backend-python')

def load_env():
    """Load environment variables from .env file"""
    env_path = '/Users/singhxss/Desktop/Personal/trading-scanner/backend-python/.env'
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def test_supabase_connection():
    """Test connection to Supabase"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
        
        # Get one stock from the database
        result = supabase.table('screened_stocks').select('symbol').limit(1).execute()
        
        if result.data:
            stock_symbol = result.data[0]['symbol']
            print(f"✅ Connected to Supabase successfully!")
            print(f"📈 Found stock: {stock_symbol}")
            return stock_symbol
        else:
            print("❌ No stocks found in database")
            return None
            
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        return None

def get_stock_fundamentals(symbol):
    """Get fundamental data for a stock"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
        
        # Generate mock fundamental data for the stock
        market_cap = 50000000000 + (hash(symbol) % 100000000000)
        pe_ratio = 12.5 + (hash(symbol) % 20)
        
        fundamental_data = {
            "symbol": symbol,
            "company_name": f"{symbol} Limited",
            "market_cap": market_cap,
            "pe_ratio": round(pe_ratio, 2),
            "pb_ratio": round(1.5 + (hash(symbol) % 5), 2),
            "roe": round(0.12 + (hash(symbol) % 20) / 100, 3),
            "eps": round(15.0 + (hash(symbol) % 50), 2),
            "sector": "Technology",
            "industry": "Software"
        }
        
        # Insert into database
        supabase.table('fundamentals').upsert([fundamental_data]).execute()
        
        print(f"📊 Generated fundamental data for {symbol}:")
        print(f"   Company: {fundamental_data['company_name']}")
        print(f"   Market Cap: ${fundamental_data['market_cap']:,}")
        print(f"   P/E Ratio: {fundamental_data['pe_ratio']}")
        print(f"   P/B Ratio: {fundamental_data['pb_ratio']}")
        print(f"   ROE: {fundamental_data['roe']}")
        print(f"   EPS: ${fundamental_data['eps']}")
        print(f"   Sector: {fundamental_data['sector']}")
        print(f"   Industry: {fundamental_data['industry']}")
        
        return fundamental_data
        
    except Exception as e:
        print(f"❌ Error getting fundamentals: {e}")
        return None

def get_stock_ohlc(symbol):
    """Get OHLC data for a stock"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL", ""),
            os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
        )
        
        # Get OHLC data from database
        result = supabase.table('daily_candles').select('*').eq('symbol', symbol).limit(5).execute()
        
        if result.data:
            print(f"📈 OHLC data for {symbol} (last 5 records):")
            for row in result.data:
                print(f"   {row['ts']}: O:{row['open']} H:{row['high']} L:{row['low']} C:{row['close']} V:{row['volume']}")
            return result.data
        else:
            print(f"❌ No OHLC data found for {symbol}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting OHLC data: {e}")
        return None

def main():
    print("🚀 Trading Scanner - Single Stock Test")
    print("=" * 50)
    
    # Load environment variables
    load_env()
    
    # Test Supabase connection and get a stock
    stock_symbol = test_supabase_connection()
    
    if not stock_symbol:
        print("❌ Cannot proceed without a valid stock symbol")
        return
    
    print(f"\n🎯 Testing with stock: {stock_symbol}")
    print("-" * 30)
    
    # Get fundamental data
    fundamentals = get_stock_fundamentals(stock_symbol)
    
    # Get OHLC data
    ohlc_data = get_stock_ohlc(stock_symbol)
    
    print("\n✅ Single stock test completed!")
    print(f"📊 Processed data for: {stock_symbol}")

if __name__ == "__main__":
    main()
