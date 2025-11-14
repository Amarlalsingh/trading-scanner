#!/usr/bin/env python3
"""
Simple local trading scanner test for 1 stock without external dependencies
"""
import json
from datetime import datetime, timedelta
import random

def generate_mock_stock_data(symbol="AAPL"):
    """Generate mock stock data for testing"""
    
    # Generate fundamental data
    fundamentals = {
        "symbol": symbol,
        "company_name": f"{symbol} Inc.",
        "market_cap": random.randint(50000000000, 500000000000),
        "pe_ratio": round(random.uniform(10.0, 30.0), 2),
        "pb_ratio": round(random.uniform(1.0, 5.0), 2),
        "roe": round(random.uniform(0.05, 0.25), 3),
        "eps": round(random.uniform(5.0, 50.0), 2),
        "sector": random.choice(["Technology", "Finance", "Healthcare", "Energy", "Consumer Goods"]),
        "industry": random.choice(["Software", "Banking", "Pharmaceuticals", "Oil & Gas", "Retail"])
    }
    
    # Generate OHLC data for last 30 days
    ohlc_data = []
    base_price = random.uniform(100, 300)
    
    for i in range(30):
        date = datetime.now() - timedelta(days=29-i)
        
        # Generate realistic OHLC data
        open_price = base_price + random.uniform(-5, 5)
        close_price = open_price + random.uniform(-10, 10)
        high_price = max(open_price, close_price) + random.uniform(0, 5)
        low_price = min(open_price, close_price) - random.uniform(0, 5)
        volume = random.randint(1000000, 10000000)
        
        ohlc_data.append({
            "date": date.strftime("%Y-%m-%d"),
            "open": round(open_price, 2),
            "high": round(high_price, 2),
            "low": round(low_price, 2),
            "close": round(close_price, 2),
            "volume": volume
        })
        
        base_price = close_price  # Use previous close as base for next day
    
    return fundamentals, ohlc_data

def analyze_stock(fundamentals, ohlc_data):
    """Perform basic stock analysis"""
    
    # Calculate some basic metrics
    latest_price = ohlc_data[-1]["close"]
    price_30_days_ago = ohlc_data[0]["close"]
    price_change = latest_price - price_30_days_ago
    price_change_pct = (price_change / price_30_days_ago) * 100
    
    # Calculate average volume
    avg_volume = sum(day["volume"] for day in ohlc_data) / len(ohlc_data)
    
    # Simple moving averages
    prices = [day["close"] for day in ohlc_data]
    sma_5 = sum(prices[-5:]) / 5
    sma_10 = sum(prices[-10:]) / 10
    sma_20 = sum(prices[-20:]) / 20
    
    analysis = {
        "current_price": latest_price,
        "30_day_change": round(price_change, 2),
        "30_day_change_pct": round(price_change_pct, 2),
        "avg_volume": int(avg_volume),
        "sma_5": round(sma_5, 2),
        "sma_10": round(sma_10, 2),
        "sma_20": round(sma_20, 2),
        "trend": "Bullish" if sma_5 > sma_10 > sma_20 else "Bearish" if sma_5 < sma_10 < sma_20 else "Neutral"
    }
    
    return analysis

def print_stock_report(symbol, fundamentals, ohlc_data, analysis):
    """Print a comprehensive stock report"""
    
    print(f"📈 TRADING SCANNER REPORT - {symbol}")
    print("=" * 60)
    
    print(f"\n🏢 COMPANY INFORMATION")
    print(f"   Company Name: {fundamentals['company_name']}")
    print(f"   Sector: {fundamentals['sector']}")
    print(f"   Industry: {fundamentals['industry']}")
    
    print(f"\n💰 FUNDAMENTAL DATA")
    print(f"   Market Cap: ${fundamentals['market_cap']:,}")
    print(f"   P/E Ratio: {fundamentals['pe_ratio']}")
    print(f"   P/B Ratio: {fundamentals['pb_ratio']}")
    print(f"   ROE: {fundamentals['roe']}")
    print(f"   EPS: ${fundamentals['eps']}")
    
    print(f"\n📊 PRICE ANALYSIS")
    print(f"   Current Price: ${analysis['current_price']}")
    print(f"   30-Day Change: ${analysis['30_day_change']} ({analysis['30_day_change_pct']:+.2f}%)")
    print(f"   Average Volume: {analysis['avg_volume']:,}")
    
    print(f"\n📈 TECHNICAL INDICATORS")
    print(f"   5-Day SMA: ${analysis['sma_5']}")
    print(f"   10-Day SMA: ${analysis['sma_10']}")
    print(f"   20-Day SMA: ${analysis['sma_20']}")
    print(f"   Trend: {analysis['trend']}")
    
    print(f"\n📋 RECENT PRICE ACTION (Last 5 Days)")
    for day in ohlc_data[-5:]:
        print(f"   {day['date']}: ${day['close']} (Vol: {day['volume']:,})")
    
    print(f"\n✅ ANALYSIS COMPLETE FOR {symbol}")

def main():
    print("🚀 LOCAL TRADING SCANNER - SINGLE STOCK TEST")
    print("=" * 60)
    
    # You can change this to any stock symbol
    stock_symbol = "AAPL"
    
    print(f"🎯 Analyzing stock: {stock_symbol}")
    print("⏳ Generating mock data...")
    
    # Generate mock data
    fundamentals, ohlc_data = generate_mock_stock_data(stock_symbol)
    
    print("📊 Performing analysis...")
    
    # Analyze the stock
    analysis = analyze_stock(fundamentals, ohlc_data)
    
    # Print comprehensive report
    print_stock_report(stock_symbol, fundamentals, ohlc_data, analysis)
    
    # Save data to files for inspection
    with open(f"{stock_symbol}_fundamentals.json", "w") as f:
        json.dump(fundamentals, f, indent=2)
    
    with open(f"{stock_symbol}_ohlc.json", "w") as f:
        json.dump(ohlc_data, f, indent=2)
    
    with open(f"{stock_symbol}_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    print(f"\n💾 Data saved to:")
    print(f"   - {stock_symbol}_fundamentals.json")
    print(f"   - {stock_symbol}_ohlc.json")
    print(f"   - {stock_symbol}_analysis.json")

if __name__ == "__main__":
    main()
