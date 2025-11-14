import pandas as pd
import numpy as np
from typing import Optional, Dict

def run(df: pd.DataFrame, symbol: str, meta: dict) -> Optional[Dict]:
    """
    Breakout pattern detection
    Identifies when price breaks above resistance with volume confirmation
    """
    if len(df) < 20:
        return None
    
    # Calculate 20-period high (resistance)
    df['resistance'] = df['high'].rolling(window=20).max()
    df['avg_volume'] = df['volume'].rolling(window=20).mean()
    
    latest = df.iloc[-1]
    prev = df.iloc[-2]
    
    if pd.isna(latest['resistance']) or pd.isna(latest['avg_volume']):
        return None
    
    # Check for breakout conditions
    # 1. Current high breaks above resistance
    # 2. Volume is above average
    # 3. Close is near high (strong close)
    
    resistance_level = prev['resistance']  # Use previous resistance
    volume_multiplier = latest['volume'] / latest['avg_volume']
    close_to_high_ratio = latest['close'] / latest['high']
    
    if (latest['high'] > resistance_level and 
        volume_multiplier > 1.5 and  # Volume 50% above average
        close_to_high_ratio > 0.95):  # Close within 5% of high
        
        breakout_strength = min((latest['high'] - resistance_level) / resistance_level * 100, 5.0)
        
        return {
            "insight_type": "BREAKOUT",
            "signal_type": "BUY",
            "price": latest['close'],
            "score": min(breakout_strength / 5.0 + volume_multiplier / 3.0, 1.0),
            "attributes": {
                "resistance_level": resistance_level,
                "breakout_price": latest['high'],
                "volume_multiplier": volume_multiplier,
                "breakout_strength_pct": breakout_strength,
                "close_to_high_ratio": close_to_high_ratio
            }
        }
    
    return None
