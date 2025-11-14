# Trading Scanner

A comprehensive trading scanner system that fetches daily OHLC data from Shoonya, runs insight algorithms, and provides a Next.js frontend for visualization.

## 🚀 Features

- **Technical Analysis**: RSI, EMA crossover, breakout patterns
- **Fundamental Data**: Market cap, PE ratio, sector analysis for 4000+ NSE stocks
- **Real-time Dashboard**: Interactive charts with TradingView Lightweight Charts
- **Signal Detection**: Automated buy/sell signal generation
- **Supabase Integration**: PostgreSQL database with real-time updates

## 🏗️ Architecture

- **Backend**: Python FastAPI with Shoonya integration
- **Database**: Supabase (PostgreSQL)
- **Frontend**: Next.js with TradingView Lightweight Charts
- **Storage**: Supabase Storage for chart images

## 📦 Project Structure

```
trading-scanner/
├── backend-python/          # Python FastAPI backend
├── frontend-nextjs/          # Next.js frontend
├── infra/                   # Database migrations
└── docs/                    # Documentation
```

## 🛠️ Quick Setup

### 1. Database Setup
1. Create Supabase project
2. Run `setup_database.sql` in SQL Editor

### 2. Environment Configuration
```bash
# Backend
cp backend-python/.env.example backend-python/.env
# Edit with your Supabase credentials

# Frontend  
cp frontend-nextjs/.env.local.example frontend-nextjs/.env.local
# Edit with your Supabase credentials
```

### 3. Install Dependencies
```bash
# Frontend
cd frontend-nextjs && npm install

# Backend
cd backend-python && pip install -r requirements.txt
```

### 4. Start Services
```bash
# Backend
cd backend-python && uvicorn app.main:app --reload

# Frontend
cd frontend-nextjs && npm run dev
```

### 5. Load Data
1. Open http://localhost:3000/admin
2. Click "Load Fundamentals" to load EQUITY_L.csv
3. Add Shoonya credentials for price data
4. Run backfill and scanner

## 📊 Data Sources

- **EQUITY_L.csv**: 4000+ NSE stocks list
- **Shoonya API**: Daily OHLC price data
- **yfinance**: Fundamental data (PE, ROE, Market Cap)

## 🔧 API Endpoints

- `GET /api/ohlc` - OHLC data for charts
- `GET /api/insights` - Technical insights
- `GET /api/fundamentals` - Fundamental data
- `POST /api/load_fundamentals` - Load stock fundamentals
- `POST /api/run_scanner` - Run insight algorithms

## 🚀 Deployment

- **Frontend**: Deploy to Vercel
- **Backend**: Deploy to Railway/Fly.io
- **Database**: Supabase managed PostgreSQL

## 📝 License

MIT License
