# Deployment Guide

## Backend (Render)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Fix deployment config"
   git push origin main
   ```

2. **Render Setup:**
   - Go to render.com
   - Connect GitHub repo
   - Select `backend-python` folder
   - Set environment variables:
     - `SUPABASE_URL`: https://jzbbqbktptguqbnribbj.supabase.co
     - `SUPABASE_SERVICE_ROLE_KEY`: [your key from .env]

3. **Build Command:** `pip install -r requirements.txt`
4. **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Frontend (Vercel)

1. **Push to GitHub** (same as above)

2. **Vercel Setup:**
   - Go to vercel.com
   - Import GitHub repo
   - Root directory: `/` (main folder)
   - Framework: Next.js
   - Environment variables:
     - `NEXT_PUBLIC_API_URL`: https://your-render-app.onrender.com
     - `NEXT_PUBLIC_SUPABASE_URL`: https://jzbbqbktptguqbnribbj.supabase.co
     - `NEXT_PUBLIC_SUPABASE_ANON_KEY`: [your anon key]

## Common Issues Fixed:

1. **Backend:** Added PORT environment variable support
2. **Frontend:** Fixed API URL to point to Render
3. **CORS:** Configured for production domains
4. **Environment:** Separated local and production configs
