# Trading Scanner Backend

Python FastAPI backend for the Trading Scanner system.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Run the server:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Service role key for database access
- `SHOONYA_*`: Shoonya API credentials

## API Endpoints

- `GET /api/ohlc?symbol=XXX` - Get OHLC data for charts
- `GET /api/insights?symbol=XXX` - Get insights for a symbol
- `GET /api/signals` - Get recent trade signals
- `POST /api/upload-screened` - Upload screened stocks CSV
- `POST /api/trigger_backfill` - Trigger data backfill
- `POST /api/run_scanner` - Run insight scanner

## Docker

```bash
docker build -t trading-scanner-backend .
docker run -p 8000:8000 --env-file .env trading-scanner-backend
```
