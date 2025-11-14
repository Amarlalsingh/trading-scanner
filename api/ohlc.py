from http.server import BaseHTTPRequestHandler
import json
import os
import urllib.parse
from supabase import create_client

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            # Parse query parameters
            parsed_path = urllib.parse.urlparse(self.path)
            query_params = urllib.parse.parse_qs(parsed_path.query)
            
            symbol = query_params.get('symbol', [None])[0]
            from_date = query_params.get('from', [None])[0]
            to_date = query_params.get('to', [None])[0]
            
            if not symbol:
                raise ValueError("Symbol parameter is required")
            
            # Get Supabase client
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            supabase = create_client(supabase_url, supabase_key)
            
            # Query daily candles
            query = supabase.table('daily_candles').select('*').eq('symbol', symbol)
            
            if from_date:
                query = query.gte('ts', from_date)
            if to_date:
                query = query.lte('ts', to_date)
            
            result = query.order('ts').execute()
            
            # Format for lightweight charts
            data = []
            for row in result.data:
                data.append({
                    'time': row['ts'],
                    'open': row['open'],
                    'high': row['high'],
                    'low': row['low'],
                    'close': row['close'],
                    'volume': row['volume']
                })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(data).encode())
            
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
