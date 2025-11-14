# Trading Scanner Frontend

Next.js frontend for the Trading Scanner system.

## Setup

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your Supabase credentials
   ```

3. **Run development server:**
   ```bash
   npm run dev
   ```

## Environment Variables

- `NEXT_PUBLIC_SUPABASE_URL`: Your Supabase project URL
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`: Supabase anonymous key
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## Features

- **Dashboard**: Overview of all tracked stocks with scores
- **Stock Detail**: Individual stock analysis with charts and insights
- **Admin Panel**: Upload CSV files and trigger data operations
- **Interactive Charts**: TradingView Lightweight Charts integration

## Deployment

Deploy to Vercel:

```bash
npm run build
# Deploy to Vercel via GitHub integration
```
