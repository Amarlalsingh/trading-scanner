# Trading Scanner - Step by Step Setup

## Step 1: Create Supabase Project

1. Go to https://supabase.com
2. Create new project
3. Wait for database to initialize
4. Go to SQL Editor
5. Run this SQL:

```sql
-- Copy and paste from infra/supabase_init.sql
-- Then run infra/fundamentals_schema.sql
```

6. Go to Settings > API
7. Copy your:
   - Project URL
   - anon/public key
   - service_role key

## Step 2: Configure Backend Environment

```bash
cd backend-python
cp .env.example .env
```

Edit `.env` with your credentials:
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_ANON_KEY=your-anon-key

# Add Shoonya credentials when ready
SHOONYA_USERID=
SHOONYA_PASSWORD=
# ... etc
```

## Step 3: Install Backend Dependencies

```bash
cd backend-python
pip3 install fastapi uvicorn supabase pandas yfinance python-dotenv
```

## Step 4: Configure Frontend Environment

```bash
cd frontend-nextjs
cp .env.local.example .env.local
```

Edit `.env.local`:
```
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Step 5: Start Backend

```bash
cd backend-python
uvicorn app.main:app --reload
```

## Step 6: Start Frontend

```bash
cd frontend-nextjs
npm run dev
```

## Step 7: Load Data

1. Open http://localhost:3000/admin
2. Click "Load Fundamentals" to load EQUITY_L.csv
3. Wait for completion
4. View dashboard at http://localhost:3000

## Next Steps

- Add Shoonya credentials for price data
- Run backfill and scanner
- View insights and signals
