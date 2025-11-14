import pandas as pd
import ta
from typing import Optional, Dict

def run(df: pd.DataFrame, symbol: str, meta: dict) -> Optional[Dict]:
    """
    EMA Crossover indicator
    Returns BUY signal when short EMA crosses above long EMA
    Returns SELL signal when short EMA crosses below long EMA
    """
    if len(df) < 50:  # Need enough data for 50-period EMA
        return None
    
    # Calculate EMAs
    df['ema_12'] = ta.trend.EMAIndicator(df['close'], window=12).ema_indicator()
    df['ema_26'] = ta.trend.EMAIndicator(df['close'], window=26).ema_indicator()
    
    # Check for crossover
    current_12 = df['ema_12'].iloc[-1]
    current_26 = df['ema_26'].iloc[-1]
    prev_12 = df['ema_12'].iloc[-2]
    prev_26 = df['ema_26'].iloc[-2]
    
    if pd.isna(current_12) or pd.isna(current_26) or pd.isna(prev_12) or pd.isna(prev_26):
        return None
    
    latest_close = df['close'].iloc[-1]
    
    # Bullish crossover: 12 EMA crosses above 26 EMA
    if prev_12 <= prev_26 and current_12 > current_26:
        distance = (current_12 - current_26) / current_26
        return {
            "insight_type": "EMA_CROSS",
            "signal_type": "BUY",
            "price": latest_close,
            "score": min(distance * 10, 1.0),  # Normalize score
            "attributes": {
                "ema_12": current_12,
                "ema_26": current_26,
                "crossover_type": "bullish",
                "distance_pct": distance * 100
            }
        }
    
    # Bearish crossover: 12 EMA crosses below 26 EMA
    elif prev_12 >= prev_26 and current_12 < current_26:
        distance = (current_26 - current_12) / current_26
        return {
            "insight_type": "EMA_CROSS",
            "signal_type": "SELL", 
            "price": latest_close,
            "score": min(distance * 10, 1.0),  # Normalize score
            "attributes": {
                "ema_12": current_12,
                "ema_26": current_26,
                "crossover_type": "bearish",
                "distance_pct": distance * 100
            }
        }
    
    return None
