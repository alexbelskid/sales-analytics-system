import sys
import os
import time
import asyncio
from unittest.mock import MagicMock
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Mock prophet
sys.modules['prophet'] = MagicMock()

# Mock supabase
from app import database
database.supabase = MagicMock()

from app.services.forecast_service import ForecastService

# Generate large dataset
def generate_data(rows=5000): # Reduced to 5000 to be faster but enough to trigger pagination (page=1000)
    print(f"Generating {rows} mock rows...")
    start_date = pd.to_datetime('2020-01-01')
    days_added = np.random.randint(0, 1000, rows)
    dates = [start_date + pd.Timedelta(days=d) for d in days_added]

    data = []
    for d in dates:
        data.append({
            "sale_date": d.strftime('%Y-%m-%d'),
            "total_amount": float(np.random.uniform(10, 1000)),
            "id": "some-uuid",
            "sale_items": {"product_id": "123"} # Mock nested structure if needed
        })
    return data

DATA = generate_data(5000)

class MockResult:
    def __init__(self, data):
        self.data = data

class MockQuery:
    def __init__(self, data):
        self.all_data = data
        self.range_start = 0
        self.range_end = None
        self.calls = []

    def select(self, *args, **kwargs):
        self.calls.append(f"select({args})")
        return self

    def table(self, *args, **kwargs):
        self.calls.append(f"table({args})")
        return self

    def range(self, start, end):
        self.range_start = start
        self.range_end = end
        self.calls.append(f"range({start}, {end})")
        return self

    def gte(self, col, val):
        self.calls.append(f"gte({col}, {val})")
        return self

    def eq(self, col, val):
        self.calls.append(f"eq({col}, {val})")
        return self

    def in_(self, col, val):
        self.calls.append(f"in_({col}, {val})")
        return self

    def execute(self):
        self.calls.append("execute()")
        if self.range_end is not None:
            # inclusive range
            chunk = self.all_data[self.range_start : self.range_end + 1]
            return MockResult(chunk)
        return MockResult(self.all_data)

mock_query_instance = MockQuery(DATA)

# Setup mock
database.supabase.table.return_value = mock_query_instance

async def run_benchmark():
    service = ForecastService()

    print("Starting benchmark...")
    start_time = time.time()

    # Run train
    # We expect pagination to happen (5000 rows / 1000 page size = 5 fetches)
    res = await service.train()

    end_time = time.time()
    print(f"Time taken: {end_time - start_time:.4f} seconds")
    print(f"Result status: {res.get('status')}")
    print(f"Records used: {res.get('records_used')}")

    # Verify logic
    calls = mock_query_instance.calls
    print("\nVerifying calls...")

    # Check for GTE (date filter)
    has_gte = any("gte(sale_date" in c for c in calls)
    print(f"Date filter (gte) applied: {has_gte}")
    if not has_gte:
        print("FAIL: Date filter missing")
        sys.exit(1)

    # Check for Pagination
    range_calls = [c for c in calls if c.startswith("range")]
    print(f"Range calls count: {len(range_calls)}")
    if len(range_calls) < 5:
        print(f"FAIL: Expected at least 5 range calls, got {len(range_calls)}")
        sys.exit(1)

    print("SUCCESS: Optimizations verified.")

if __name__ == "__main__":
    asyncio.run(run_benchmark())
