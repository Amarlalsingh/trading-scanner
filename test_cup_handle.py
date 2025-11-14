#!/usr/bin/env python3
"""
Test cup and handle with synthetic data that contains the pattern
"""
import json
from datetime import datetime, timedelta

def generate_cup_handle_data():
    """Generate price data with a clear cup and handle pattern"""
    prices = []
    dates = []
    
    # Pre-cup uptrend
    base = 100
    for i in range(5):
        prices.append(base + i * 2)
        dates.append((datetime.now() - timedelta(days=50-i)).strftime("%Y-%m-%d"))
    
    # Cup formation (U-shape)
    cup_high = 110
    for i in range(25):  # 25-day cup
        if i < 12:  # Decline phase
            price = cup_high - (i * 3)  # Decline to ~74
        else:  # Recovery phase
            price = 74 + ((i - 12) * 2.8)  # Recover to ~110
        prices.append(round(price, 2))
        dates.append((datetime.now() - timedelta(days=45-i)).strftime("%Y-%m-%d"))
    
    # Handle formation (small pullback)
    handle_start = 110
    for i in range(8):  # 8-day handle
        price = handle_start - (i * 1.5) + (i * 0.5)  # Small pullback to ~105
        prices.append(round(price, 2))
        dates.append((datetime.now() - timedelta(days=20-i)).strftime("%Y-%m-%d"))
    
    # Recent breakout
    for i in range(5):
        price = 108 + (i * 2)  # Breakout above handle
        prices.append(round(price, 2))
        dates.append((datetime.now() - timedelta(days=12-i)).strftime("%Y-%m-%d"))
    
    return prices, dates

def detect_cup_and_handle(prices, min_cup_length=20, handle_ratio=0.3):
    """Detect cup and handle pattern"""
    if len(prices) < min_cup_length + 5:
        return None
    
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
        if cup_depth < 0.1 * cup_high_start:
            continue
            
        if abs(cup_high_start - cup_high_end) > 0.05 * cup_high_start:
            continue
            
        # Handle detection
        handle_start = cup_end
        handle_length = min(10, len(prices) - handle_start)
        
        if handle_length < 3:
            continue
            
        handle_prices = prices[handle_start:handle_start + handle_length]
        handle_high = max(handle_prices)
        handle_low = min(handle_prices)
        handle_depth = handle_high - handle_low
        
        if handle_depth > handle_ratio * cup_depth:
            continue
            
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

def main():
    print("🧪 TESTING CUP AND HANDLE DETECTION")
    print("=" * 50)
    
    # Generate synthetic data with pattern
    prices, dates = generate_cup_handle_data()
    
    print(f"📊 Generated {len(prices)} days of synthetic price data")
    print(f"💰 Price range: ${min(prices)} - ${max(prices)}")
    
    # Detect pattern
    pattern = detect_cup_and_handle(prices)
    
    if pattern:
        print(f"\n✅ PATTERN DETECTED: {pattern['pattern']}")
        print(f"   Cup: Days {pattern['cup_start']}-{pattern['cup_end']} (Depth: ${pattern['cup_depth']})")
        print(f"   Handle: Days {pattern['handle_start']}-{pattern['handle_end']} (Depth: ${pattern['handle_depth']})")
        print(f"   Cup Low: ${pattern['cup_low']}")
        print(f"   Breakout Level: ${pattern['breakout_level']}")
        print(f"   Confidence: {pattern['confidence']}")
        
        current_price = prices[-1]
        if current_price > pattern['breakout_level']:
            print(f"\n🚀 BREAKOUT CONFIRMED! Current: ${current_price}")
        else:
            print(f"\n⏳ No breakout yet. Current: ${current_price}")
            
        # Show key price points
        print(f"\n📈 KEY LEVELS:")
        print(f"   Cup Start: ${prices[pattern['cup_start']]}")
        print(f"   Cup Low: ${pattern['cup_low']}")
        print(f"   Cup End: ${prices[pattern['cup_end']-1]}")
        print(f"   Handle Low: ${min(prices[pattern['handle_start']:pattern['handle_end']])}")
        print(f"   Current: ${prices[-1]}")
        
    else:
        print("\n❌ No pattern detected")

if __name__ == "__main__":
    main()
