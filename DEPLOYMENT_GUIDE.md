# 🚀 Deployment Guide

To make your AI System live, follow these steps.

## 1. Backend (Railway)
The brain of your AI needs a server.

1. Go to [Railway.app](https://railway.app/) and login/signup.
2. Click **"New Project"** -> **"Deploy from GitHub repo"**.
3. Select your repository (`alexbelskid/sales-analytics-system` or similar).
4. Select the **backend** folder if asked, or just deploy the root (but we recommend deploying just the backend service if possible, or using the Dockerfile).
   - Railway normally detects `Dockerfile` in `backend/`. If it asks for "Root Directory", set it to `./backend`.
5. **Variables**: Go to the "Variables" tab in your new service and add:
   - `TAVILY_API_KEY`: (from your .env)
   - `GROQ_API_KEY` or `OPENAI_API_KEY`: (from your .env)
   - `SUPABASE_URL`: (from your .env)
   - `SUPABASE_KEY`: (from your .env)
   - `SUPABASE_SERVICE_KEY`: (from your .env)
6. Railway will build and provide a URL (e.g., `https://backend-production.up.railway.app`). **Copy this URL.**

## 2. Frontend (Vercel)
The beautiful interface.

1. Go to [Vercel.com](https://vercel.com) and login.
2. Click **"Add New..."** -> **"Project"**.
3. Import your GitHub repository.
4. **Framework Preset**: Next.js (should be auto-detected).
5. **Root Directory**: Click "Edit" and select `frontend`.
6. **Environment Variables**:
   - `NEXT_PUBLIC_API_URL`: Paste the **Railway URL** from above (e.g., `https://backend-production.up.railway.app`).
   - *Note: Do NOT add trailing slash `/` at the end.*
7. Click **"Deploy"**.

## 3. Post-Deploy Check
Open your new Vercel URL (e.g., `sales-ai.vercel.app`) and go to `/ai-assistant`.
Try asking: *"Hello"*
- If it works: You are live! 🌍
- If error: Check Vercel Logs (Functions tab) or Railway Logs.

---
**Prepared by Antigravity Agent**
