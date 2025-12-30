#!/bin/bash
# Start script for Railpack deployment

# Install dependencies from root requirements.txt
pip install -r requirements.txt

# Start the FastAPI server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
