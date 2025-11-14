#!/usr/bin/env python3
"""
Cup and Handle pattern detector
"""
import json

def detect_cup_and_handle(prices, min_cup_length=20, handle_ratio=0.3):
    """
    Detect cup and handle pattern in price data
    
    Cup and Handle criteria:
    1. Cup: U-shaped decline and recovery (20+ periods)
    2. Handle: Small pullback after cup (10-30% of cup depth)
    3. Breakout: Price breaks above handle high
    """
    if len(prices) < min_cup_length + 5:
        return None
    
    # Find potential cup formation
    for i in range(len(prices) - min_cup_length):
        cup_start = i
        cup_end = i + min_cup_length
        
        if cup_end >= len(prices):
            break
            
        cup_prices = prices[cup_start:cup_end]
        cup_high_start = cup_prices[0]
        cup_high_end = cup_prices[-1]
        cup_low = min(cup_prices)
        
        # Cup criteria
        cup_depth = max(cup_high_start, cup_high_end) - cup_low
        if cup_depth < 0.1 * cup_high_start:  # At least 10% decline
            continue
            
        # Both ends should be near highs
        if abs(cup_high_start - cup_high_end) > 0.05 * cup_high_start:
            continue
            
        # Look for handle after cup
        handle_start = cup_end
        handle_length = min(10, len(prices) - handle_start)
        
        if handle_length < 3:
            continue
            
        handle_prices = prices[handle_start:handle_start + handle_length]
        handle_high = max(handle_prices)
        handle_low = min(handle_prices)
        handle_depth = handle_high - handle_low
        
        # Handle should be shallow (less than 30% of cup depth)
        if handle_depth > handle_ratio * cup_depth:
            continue
            
        # Pattern found
        return {
            "pattern": "Cup and Handle",
            "cup_start": cup_start,
            "cup_end": cup_end,
            "handle_start": handle_start,
            "handle_end": handle_start + handle_length,
            "cup_depth": round(cup_depth, 2),
            "handle_depth": round(handle_depth, 2),
            "cup_low": round(cup_low, 2),
            "breakout_level": round(handle_high, 2),
            "confidence": "High" if handle_depth < 0.15 * cup_depth else "Medium"
        }
    
    return None

def run_pattern_detection():
    """Run cup and handle detection on AAPL data"""
    
    # Load the OHLC data
    with open('AAPL_ohlc.json', 'r') as f:
        ohlc_data = json.load(f)
    
    # Extract closing prices
    prices = [day['close'] for day in ohlc_data]
    
    print("🔍 CUP AND HANDLE PATTERN DETECTION")
    print("=" * 50)
    print(f"📊 Analyzing {len(prices)} days of AAPL price data")
    
    # Detect pattern
    pattern = detect_cup_and_handle(prices)
    
    if pattern:
        print(f"\n✅ PATTERN FOUND: {pattern['pattern']}")
        print(f"   Cup Period: Day {pattern['cup_start']} to {pattern['cup_end']}")
        print(f"   Handle Period: Day {pattern['handle_start']} to {pattern['handle_end']}")
        print(f"   Cup Depth: ${pattern['cup_depth']}")
        print(f"   Handle Depth: ${pattern['handle_depth']}")
        print(f"   Cup Low: ${pattern['cup_low']}")
        print(f"   Breakout Level: ${pattern['breakout_level']}")
        print(f"   Confidence: {pattern['confidence']}")
        
        # Show the actual dates and prices
        print(f"\n📅 PATTERN TIMELINE:")
        cup_start_date = ohlc_data[pattern['cup_start']]['date']
        cup_end_date = ohlc_data[pattern['cup_end']-1]['date']
        handle_end_date = ohlc_data[min(pattern['handle_end']-1, len(ohlc_data)-1)]['date']
        
        print(f"   Cup: {cup_start_date} to {cup_end_date}")
        print(f"   Handle: {cup_end_date} to {handle_end_date}")
        
        current_price = prices[-1]
        if current_price > pattern['breakout_level']:
            print(f"\n🚀 BREAKOUT CONFIRMED! Current: ${current_price}")
        else:
            print(f"\n⏳ Waiting for breakout above ${pattern['breakout_level']}")
            print(f"   Current price: ${current_price}")
    else:
        print("\n❌ No Cup and Handle pattern detected")
        print("   Pattern requires:")
        print("   - 20+ day cup formation")
        print("   - 10%+ price decline in cup")
        print("   - Shallow handle (< 30% of cup depth)")

if __name__ == "__main__":
    run_pattern_detection()
