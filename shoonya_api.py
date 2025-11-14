#!/usr/bin/env python3
"""
Shoonya API integration for real market data
"""
import requests
import hashlib
import os
import json
from datetime import datetime

def load_env():
    """Load Shoonya credentials from .env"""
    env_path = '/Users/singhxss/Desktop/Personal/trading-scanner/backend-python/.env'
    with open(env_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ[key] = value

def shoonya_login():
    """Login to Shoonya API"""
    userid = os.getenv('SHOONYA_USERID')
    password = os.getenv('SHOONYA_PASSWORD')
    twofa = os.getenv('SHOONYA_2FA')
    vendor_code = os.getenv('SHOONYA_VENDOR_CODE')
    api_secret = os.getenv('SHOONYA_API_SECRET')
    imei = os.getenv('SHOONYA_IMEI')
    
    if not all([userid, password, vendor_code, api_secret]):
        print("❌ Missing Shoonya credentials in .env file")
        return None
    
    # Create app key hash
    app_key = f"{userid}|{api_secret}"
    app_key_hash = hashlib.sha256(app_key.encode()).hexdigest()
    
    login_data = {
        "apkversion": "1.0.0",
        "uid": userid,
        "pwd": password,
        "factor2": twofa,
        "vc": vendor_code,
        "appkey": app_key_hash,
        "imei": imei
    }
    
    try:
        response = requests.post("https://api.shoonya.com/NorenWClientTP/QuickAuth", data=login_data)
        result = response.json()
        
        if result.get('stat') == 'Ok':
            print(f"✅ Shoonya login successful")
            return result.get('susertoken')
        else:
            print(f"❌ Login failed: {result.get('emsg', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def get_stock_data(token, symbol="RELIANCE-EQ"):
    """Get real-time stock data"""
    if not token:
        return None
        
    data = {
        "uid": os.getenv('SHOONYA_USERID'),
        "token": symbol,
        "exch": "NSE"
    }
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.post("https://api.shoonya.com/NorenWClientTP/GetQuotes", 
                               data=data, headers=headers)
        result = response.json()
        
        if result.get('stat') == 'Ok':
            return {
                "symbol": symbol,
                "ltp": float(result.get('lp', 0)),
                "open": float(result.get('o', 0)),
                "high": float(result.get('h', 0)),
                "low": float(result.get('l', 0)),
                "close": float(result.get('c', 0)),
                "volume": int(result.get('v', 0)),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        else:
            print(f"❌ Quote error: {result.get('emsg', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"❌ Quote fetch error: {e}")
        return None

def main():
    print("📡 SHOONYA API - REAL MARKET DATA")
    print("=" * 40)
    
    load_env()
    
    # Login
    token = shoonya_login()
    if not token:
        return
    
    # Get data for popular stocks
    stocks = ["RELIANCE-EQ", "TCS-EQ", "INFY-EQ"]
    
    print(f"\n📈 LIVE STOCK QUOTES:")
    print("-" * 40)
    
    for stock in stocks:
        data = get_stock_data(token, stock)
        if data:
            print(f"{data['symbol']:<12} LTP: ₹{data['ltp']:<8} O: ₹{data['open']:<8} H: ₹{data['high']:<8} L: ₹{data['low']}")
        else:
            print(f"{stock:<12} ❌ Failed to fetch")

if __name__ == "__main__":
    main()
