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
            
            # Get first 10 stocks for testing
            stocks = supabase.table('screened_stocks').select('symbol').limit(10).execute()
            
            fundamentals_data = []
            for stock in stocks.data:
                symbol = stock['symbol']
                try:
                    ticker = yf.Ticker(f"{symbol}.NS")
                    info = ticker.info
                    
                    fundamentals_data.append({
                        "symbol": symbol,
                        "company_name": info.get("longName"),
                        "market_cap": info.get("marketCap"),
                        "pe_ratio": info.get("trailingPE"),
                        "pb_ratio": info.get("priceToBook"),
                        "roe": info.get("returnOnEquity"),
                        "eps": info.get("trailingEps"),
                        "sector": info.get("sector"),
                        "industry": info.get("industry")
                    })
                except:
                    continue
            
            # Upsert to database
            if fundamentals_data:
                supabase.table('fundamentals').upsert(fundamentals_data).execute()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                "message": f"Loaded fundamentals for {len(fundamentals_data)} stocks",
                "count": len(fundamentals_data)
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {"error": str(e)}
            self.wfile.write(json.dumps(response).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
