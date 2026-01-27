#!/bin/bash
# ============================================================================
# Diagnostic Script for Sales Analytics System
# Checks system health, logs, and common issues
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "════════════════════════════════════════════════════════════════"
echo "🔍 Sales Analytics System - Diagnostic Tool"
echo "════════════════════════════════════════════════════════════════"
echo ""

# Function to print section headers
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to check service
check_service() {
    local name=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} $name is running"
        return 0
    else
        echo -e "  ${RED}✗${NC} $name is NOT running"
        return 1
    fi
}

# Check current directory
print_section "📁 Current Directory"
pwd

# Check environment file
print_section "⚙️  Environment Configuration"
if [ -f .env ]; then
    echo -e "  ${GREEN}✓${NC} .env file exists"
    
    if grep -q "SUPABASE_URL=" .env && [ -n "$(grep "SUPABASE_URL=" .env | cut -d'=' -f2)" ]; then
        echo -e "  ${GREEN}✓${NC} SUPABASE_URL is set"
    else
        echo -e "  ${RED}✗${NC} SUPABASE_URL is NOT set"
    fi
    
    if grep -q "SUPABASE_KEY=" .env && [ -n "$(grep "SUPABASE_KEY=" .env | cut -d'=' -f2)" ]; then
        echo -e "  ${GREEN}✓${NC} SUPABASE_KEY is set"
    else
        echo -e "  ${RED}✗${NC} SUPABASE_KEY is NOT set"
    fi
    
    if grep -q "OPENAI_API_KEY=" .env && [ -n "$(grep "OPENAI_API_KEY=" .env | cut -d'=' -f2)" ]; then
        echo -e "  ${GREEN}✓${NC} OPENAI_API_KEY is set"
    else
        echo -e "  ${YELLOW}⚠${NC}  OPENAI_API_KEY is NOT set (AI features will not work)"
    fi
else
    echo -e "  ${RED}✗${NC} .env file NOT found"
fi

# Check if services are running
print_section "🚀 Services Status"

BACKEND_OK=0
FRONTEND_OK=0

if check_service "Backend (Port 8000)" "http://localhost:8000/docs"; then
    BACKEND_OK=1
fi

if check_service "Frontend (Port 3000)" "http://localhost:3000"; then
    FRONTEND_OK=1
fi

# Check backend logs for errors
print_section "📋 Recent Backend Logs (Last 20 lines)"
if [ -f backend.log ]; then
    tail -20 backend.log | grep -E "(ERROR|WARNING|RPC not available)" --color=always || echo "  No critical errors found"
else
    echo -e "  ${YELLOW}⚠${NC}  backend.log not found"
fi

# Check frontend logs for errors  
print_section "📋 Recent Frontend Logs (Last 10 lines)"
if [ -f frontend.log ]; then
    tail -10 frontend.log | grep -E "(ERROR|Error|error)" --color=always || echo "  No errors found"
else
    echo -e "  ${YELLOW}⚠${NC}  frontend.log not found"
fi

# Check for specific known issues
print_section "🔎 Known Issues Check"

# Check for RPC ambiguous column error
if [ -f backend.log ] && grep -q "column reference.*is ambiguous" backend.log; then
    echo -e "  ${RED}✗${NC} Found 'ambiguous column reference' error"
    echo "     → This means RPC functions are missing in Supabase"
    echo "     → Solution: Apply database/create_analytics_functions.sql"
    echo "     → See: docs/FIX_ANALYTICS_RPC.md for instructions"
else
    echo -e "  ${GREEN}✓${NC} No ambiguous column errors"
fi

# Check for missing Plotly
if [ -f backend.log ] && grep -q "Importing plotly failed" backend.log; then
    echo -e "  ${YELLOW}⚠${NC}  Plotly import failed (non-critical)"
    echo "     → Interactive plots will not work"
    echo "     → Solution: pip install plotly (if needed)"
else
    echo -e "  ${GREEN}✓${NC} No plotly issues"
fi

# Check for OpenSSL warnings
if [ -f backend.log ] && grep -q "NotOpenSSLWarning" backend.log; then
    echo -e "  ${YELLOW}⚠${NC}  OpenSSL version warning (non-critical)"
    echo "     → This is a macOS LibreSSL compatibility warning"
    echo "     → Safe to ignore unless you have SSL connection issues"
fi

# Test API endpoints
print_section "🧪 API Endpoints Test"

if [ $BACKEND_OK -eq 1 ]; then
    echo "Testing key endpoints..."
    
    # Test dashboard
    if curl -s -f "http://localhost:8000/api/analytics/dashboard" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} /api/analytics/dashboard"
    else
        echo -e "  ${RED}✗${NC} /api/analytics/dashboard"
    fi
    
    # Test top products
    if curl -s -f "http://localhost:8000/api/analytics/top-products?limit=5" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} /api/analytics/top-products"
    else
        echo -e "  ${RED}✗${NC} /api/analytics/top-products"
    fi
    
    # Test agent analytics
    if curl -s -f "http://localhost:8000/api/agent-analytics/dashboard?period_start=2026-01-01&period_end=2026-01-31" > /dev/null 2>&1; then
        echo -e "  ${GREEN}✓${NC} /api/agent-analytics/dashboard"
    else
        echo -e "  ${RED}✗${NC} /api/agent-analytics/dashboard"
    fi
else
    echo -e "  ${YELLOW}⚠${NC}  Backend not running - skipping endpoint tests"
fi

# Check database connectivity
print_section "🗄️  Database Connectivity"

if [ -f .env ]; then
    SUPABASE_URL=$(grep "SUPABASE_URL=" .env | cut -d'=' -f2)
    
    if [ -n "$SUPABASE_URL" ]; then
        if curl -s -f "$SUPABASE_URL/rest/v1/" > /dev/null 2>&1; then
            echo -e "  ${GREEN}✓${NC} Supabase is reachable"
        else
            echo -e "  ${RED}✗${NC} Cannot reach Supabase"
        fi
    fi
fi

# Python environment check
print_section "🐍 Python Environment"

if [ -d .venv ]; then
    echo -e "  ${GREEN}✓${NC} Virtual environment exists (.venv)"
    
    if [ -f .venv/bin/python ]; then
        PYTHON_VERSION=$(.venv/bin/python --version 2>&1)
        echo "     Python: $PYTHON_VERSION"
    fi
    
    # Check key packages
    if .venv/bin/python -c "import fastapi" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} FastAPI installed"
    else
        echo -e "  ${RED}✗${NC} FastAPI NOT installed"
    fi
    
    if .venv/bin/python -c "import supabase" 2>/dev/null; then
        echo -e "  ${GREEN}✓${NC} Supabase client installed"
    else
        echo -e "  ${RED}✗${NC} Supabase client NOT installed"
    fi
else
    echo -e "  ${RED}✗${NC} Virtual environment NOT found"
    echo "     → Run: python -m venv .venv"
fi

# Node.js environment check
print_section "📦 Node.js Environment"

if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "  Node.js: $NODE_VERSION"
else
    echo -e "  ${RED}✗${NC} Node.js NOT installed"
fi

if [ -d node_modules ]; then
    echo -e "  ${GREEN}✓${NC} node_modules exists"
else
    echo -e "  ${YELLOW}⚠${NC}  node_modules NOT found"
    echo "     → Run: npm install"
fi

# Process check
print_section "⚙️  Running Processes"

echo "Checking for running processes..."
if pgrep -f "uvicorn.*main:app" > /dev/null; then
    BACKEND_PID=$(pgrep -f "uvicorn.*main:app")
    echo -e "  ${GREEN}✓${NC} Backend process running (PID: $BACKEND_PID)"
else
    echo -e "  ${RED}✗${NC} Backend process NOT running"
fi

if pgrep -f "next dev" > /dev/null; then
    FRONTEND_PID=$(pgrep -f "next dev")
    echo -e "  ${GREEN}✓${NC} Frontend process running (PID: $FRONTEND_PID)"
else
    echo -e "  ${RED}✗${NC} Frontend process NOT running"
fi

# Summary
print_section "📊 Summary"

ISSUES_FOUND=0

if [ $BACKEND_OK -eq 0 ]; then
    echo -e "  ${RED}⚠${NC}  Backend is not running"
    echo "     → Start with: ./start.sh or cd backend && .venv/bin/uvicorn app.main:app --reload"
    ISSUES_FOUND=1
fi

if [ $FRONTEND_OK -eq 0 ]; then
    echo -e "  ${RED}⚠${NC}  Frontend is not running"
    echo "     → Start with: ./start.sh or cd frontend && npm run dev"
    ISSUES_FOUND=1
fi

if [ -f backend.log ] && grep -q "column reference.*is ambiguous" backend.log; then
    echo -e "  ${RED}⚠${NC}  RPC functions need to be created"
    echo "     → Follow: docs/FIX_ANALYTICS_RPC.md"
    ISSUES_FOUND=1
fi

if [ $ISSUES_FOUND -eq 0 ]; then
    echo -e "  ${GREEN}✓${NC} All systems operational!"
else
    echo -e "  ${YELLOW}⚠${NC}  Issues found - see above for details"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "📚 Useful Commands:"
echo "════════════════════════════════════════════════════════════════"
echo "  Start services:    ./start.sh"
echo "  Stop services:     ./stop.sh"
echo "  Check status:      ./status.sh"
echo "  View backend logs: tail -f backend.log"
echo "  View frontend logs: tail -f frontend.log"
echo "  Backend API docs:  http://localhost:8000/docs"
echo "  Frontend:          http://localhost:3000"
echo "════════════════════════════════════════════════════════════════"
echo ""
