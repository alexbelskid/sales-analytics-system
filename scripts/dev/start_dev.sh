#!/bin/bash

# Kill existing processes on ports 8000 and 3000
echo "Stopping existing servers..."
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

# Attempt migration if supabase CLI is available
if command -v supabase &> /dev/null; then
    echo "Applying database migrations..."
    supabase db push --local
else
    echo "Supabase CLI not found. Skipping migration (Manual step required if new tables needed)."
fi

# Start Backend
echo "Starting Backend..."
cd backend
# Start uvicorn in background using python3 -m
nohup python3 -m uvicorn app.main:app --reload --port 8000 >> backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend started (PID: $BACKEND_PID)"

# Start Frontend
echo "Starting Frontend..."
cd ../frontend
# Install dependencies if needed
npm install > /dev/null 2>&1
# Start Next.js
nohup npm run dev >> frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID: $FRONTEND_PID)"

echo "------------------------------------------------"
echo "Servers are running!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "------------------------------------------------"
