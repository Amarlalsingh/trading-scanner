import pandas as pd
import importlib
import os
from datetime import date, datetime
from typing import List, Dict, Optional

from .supabase_client import (
    get_supabase_client, 
    get_candles_for_symbol, 
    insert_insight,
    upsert_stock_score
)

# Available insight modules
INSIGHT_MODULES = {
    'RSI_OVERSOLD': 'insights_engine.indicators.rsi',
    'RSI_OVERBOUGHT': 'insights_engine.indicators.rsi', 
    'EMA_CROSS': 'insights_engine.indicators.ema_cross',
    'BREAKOUT': 'insights_engine.patterns.breakout'
}

def get_insight_type_id(code: str) -> Optional[int]:
    """Get insight type ID from code"""
    supabase = get_supabase_client()
    result = supabase.table('insight_types').select('id').eq('code', code).execute()
    
    if result.data:
        return result.data[0]['id']
    return None

async def run_insights_for_symbol(symbol: str, target_date: Optional[str] = None):
    """Run all insight modules for a symbol"""
    if not target_date:
        target_date = date.today().isoformat()
    
    print(f"Running insights for {symbol} on {target_date}")
    
    # Get candle data
    candles = get_candles_for_symbol(symbol, days=100)
    
    if not candles:
        print(f"No candle data found for {symbol}")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(candles)
    df['ts'] = pd.to_datetime(df['ts'])
    df = df.sort_values('ts').reset_index(drop=True)
    
    insights_found = []
    
    # Run each insight module
    for insight_code, module_path in INSIGHT_MODULES.items():
        try:
            # Import module dynamically
            module = importlib.import_module(f"app.{module_path}")
            
            # Run the module
            result = module.run(df, symbol, {})
            
            if result:
                # Get insight type ID
                insight_type_id = get_insight_type_id(result['insight_type'])
                
                if insight_type_id:
                    insight_data = {
                        'symbol': symbol,
                        'insight_type_id': insight_type_id,
                        'detected_on': target_date,
                        'signal_type': result.get('signal_type'),
                        'price': result.get('price'),
                        'score': result.get('score'),
                        'attributes': result.get('attributes', {})
                    }
                    
                    # Insert insight
                    insert_result = insert_insight(insight_data)
                    insights_found.append(result)
                    
                    print(f"Found {result['insight_type']} for {symbol}: {result['signal_type']} at {result['price']}")
                
        except Exception as e:
            print(f"Error running {insight_code} for {symbol}: {e}")
            continue
    
    # Compute combined score
    if insights_found:
        await compute_combined_score(symbol, target_date, insights_found)
    
    print(f"Completed insights for {symbol}: {len(insights_found)} insights found")

async def compute_combined_score(symbol: str, target_date: str, insights: List[Dict]):
    """Compute combined score for a symbol"""
    
    # Default weights by category
    weights = {
        'FORMULA': 1.0,
        'PATTERN': 1.5,
        'SENTIMENT': 1.2
    }
    
    supabase = get_supabase_client()
    
    # Get insight types for weights
    insight_types = supabase.table('insight_types').select('*').execute()
    type_weights = {}
    
    for it in insight_types.data:
        type_weights[it['code']] = weights.get(it['category'], 1.0)
    
    total_score = 0
    total_weight = 0
    details = {'insights': []}
    
    for insight in insights:
        insight_type = insight['insight_type']
        score = insight.get('score', 0)
        weight = type_weights.get(insight_type, 1.0)
        
        # Adjust score based on signal type
        if insight.get('signal_type') == 'SELL':
            score = -score  # Negative for sell signals
        
        total_score += score * weight
        total_weight += weight
        
        details['insights'].append({
            'type': insight_type,
            'score': score,
            'weight': weight,
            'signal_type': insight.get('signal_type')
        })
    
    combined_score = total_score / total_weight if total_weight > 0 else 0
    details['combined'] = combined_score
    details['scale'] = '-1 to 1'
    
    # Upsert score
    score_data = {
        'symbol': symbol,
        'date': target_date,
        'combined_score': combined_score,
        'details': details
    }
    
    upsert_stock_score(score_data)
    print(f"Combined score for {symbol}: {combined_score:.3f}")

if __name__ == "__main__":
    import asyncio
    
    # Test with a single symbol
    asyncio.run(run_insights_for_symbol("RELIANCE"))
