# 🚀 Quick Start Guide

## Prerequisites Check
```bash
node --version  # Should show v23.4.0 ✅
python3 --version  # Should show Python 3.x ✅
```

## Step 1: Create Supabase Project (5 minutes)

1. **Go to**: https://supabase.com → "New Project"
2. **Create project** → Wait for initialization
3. **SQL Editor** → Copy/paste this SQL:

```sql
-- Copy entire content from: infra/supabase_init.sql
-- Then copy entire content from: infra/fundamentals_schema.sql
```

4. **Settings → API** → Copy these values:
   - Project URL
   - anon public key  
   - service_role key

## Step 2: Configure Environment

**Backend:**
```bash
cd backend-python
cp .env.example .env
# Edit .env with your Supabase credentials
```

**Frontend:**
```bash
cd frontend-nextjs  
cp .env.local.example .env.local
# Edit .env.local with your Supabase credentials
```

## Step 3: Install Dependencies

**Frontend (works):**
```bash
cd frontend-nextjs
npm install  # ✅ Already done
```

**Backend (if pip works):**
```bash
cd backend-python
pip3 install fastapi uvicorn supabase pandas yfinance python-dotenv
```

## Step 4: Start Services

**Terminal 1 - Backend:**
```bash
cd backend-python
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend-nextjs
npm run dev
```

## Step 5: Load Data

1. **Open**: http://localhost:3000/admin
2. **Click**: "Load Fundamentals" 
3. **Wait**: For 4000+ stocks to load
4. **View**: http://localhost:3000

## 🎯 Current Status

- ✅ Frontend compiled and ready
- ✅ Database schema ready
- ✅ EQUITY_L.csv ready
- ⚠️ Backend needs pip fix or manual dependency install

## Next: Fix pip or install Python packages manually
