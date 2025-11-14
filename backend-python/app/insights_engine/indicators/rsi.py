import pandas as pd
import ta
from typing import Optional, Dict

def run(df: pd.DataFrame, symbol: str, meta: dict) -> Optional[Dict]:
    """
    RSI Oversold/Overbought indicator
    Returns BUY signal when RSI < 30 (oversold)
    Returns SELL signal when RSI > 70 (overbought)
    """
    if len(df) < 14:  # Need at least 14 periods for RSI
        return None
    
    # Calculate RSI
    df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=14).rsi()
    
    latest_rsi = df['rsi'].iloc[-1]
    latest_close = df['close'].iloc[-1]
    
    if pd.isna(latest_rsi):
        return None
    
    # Determine signal
    if latest_rsi < 30:
        return {
            "insight_type": "RSI_OVERSOLD",
            "signal_type": "BUY",
            "price": latest_close,
            "score": (30 - latest_rsi) / 30,  # Higher score for more oversold
            "attributes": {
                "rsi_value": latest_rsi,
                "threshold": 30,
                "condition": "oversold"
            }
        }
    elif latest_rsi > 70:
        return {
            "insight_type": "RSI_OVERBOUGHT", 
            "signal_type": "SELL",
            "price": latest_close,
            "score": (latest_rsi - 70) / 30,  # Higher score for more overbought
            "attributes": {
                "rsi_value": latest_rsi,
                "threshold": 70,
                "condition": "overbought"
            }
        }
    
    return None
