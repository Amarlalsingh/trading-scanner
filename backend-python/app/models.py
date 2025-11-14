from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class StockScore(BaseModel):
    symbol: str
    date: date
    combined_score: float
    details: Dict[str, Any]

class Insight(BaseModel):
    symbol: str
    insight_type_id: int
    detected_on: date
    signal_type: Optional[str] = None
    price: Optional[float] = None
    score: Optional[float] = None
    attributes: Optional[Dict[str, Any]] = None

class Signal(BaseModel):
    symbol: str
    pattern: str
    signal_type: str
    detected_on: date
    buy_price: Optional[float] = None
    stop_loss: Optional[float] = None
    target_price: Optional[float] = None
    risk_reward: Optional[float] = None
    support_levels: Optional[List[float]] = None
    resistance_levels: Optional[List[float]] = None
    extra: Optional[Dict[str, Any]] = None

class ScreenedStock(BaseModel):
    symbol: str
    exchange: str = "NSE"
    meta: Optional[Dict[str, Any]] = None

class DailyCandle(BaseModel):
    symbol: str
    ts: date
    open: float
    high: float
    low: float
    close: float
    volume: float
