from http.server import BaseHTTPRequestHandler
import json
import os
import yfinance as yf
from supabase import create_client

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/fundamentals':
            self.load_fundamentals()
        else:
            self.send_error(404)
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = {"message": "Fundamentals API - use POST to load data"}
        self.wfile.write(json.dumps(response).encode())
    
    def load_fundamentals(self):
        try:
            # Get Supabase client
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            supabase = create_client(supabase_url, supabase_key)
            
            # Get first 5 stocks for testing
            stocks = supabase.table('screened_stocks').select('symbol').limit(5).execute()
            
            fundamentals_data = []
            errors = []
            
            for stock in stocks.data:
                symbol = stock['symbol']
                try:
                    # Try different ticker formats
                    ticker_formats = [f"{symbol}.NS", f"{symbol}.BO", symbol]
                    
                    for ticker_format in ticker_formats:
                        try:
                            ticker = yf.Ticker(ticker_format)
                            info = ticker.info
                            
                            # Check if we got valid data
                            if info and info.get('symbol'):
                                fundamentals_data.append({
                                    "symbol": symbol,
                                    "company_name": info.get("longName") or info.get("shortName"),
                                    "market_cap": info.get("marketCap"),
                                    "pe_ratio": info.get("trailingPE") or info.get("forwardPE"),
                                    "pb_ratio": info.get("priceToBook"),
                                    "roe": info.get("returnOnEquity"),
                                    "eps": info.get("trailingEps"),
                                    "sector": info.get("sector"),
                                    "industry": info.get("industry"),
                                    "meta": {"ticker_used": ticker_format}
                                })
                                break  # Success, stop trying other formats
                        except:
                            continue
                    else:
                        errors.append(f"Failed to fetch {symbol}")
                        
                except Exception as e:
                    errors.append(f"Error with {symbol}: {str(e)}")
            
            # Upsert to database
            if fundamentals_data:
                supabase.table('fundamentals').upsert(fundamentals_data).execute()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "message": f"Loaded fundamentals for {len(fundamentals_data)} stocks",
                "count": len(fundamentals_data),
                "errors": errors[:5],  # Show first 5 errors
                "sample_data": fundamentals_data[:2] if fundamentals_data else []
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"error": str(e), "details": "Check environment variables"}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
