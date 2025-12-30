#!/bin/bash
# Start script for Railpack deployment

cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
