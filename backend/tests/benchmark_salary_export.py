import asyncio
import time
import pandas as pd
import uuid
from unittest.mock import MagicMock, patch
import sys
import os

# Ensure backend is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.routers.salary import export_salary_excel
from app.models.agents import SalaryCalculation

# Mock data
def create_mock_data(n=10000):
    return [
        SalaryCalculation(
            agent_id=str(uuid.uuid4()),
            agent_name=f"Agent {i}",
            year=2023,
            month=10,
            base_salary=1000.0,
            sales_amount=5000.0,
            commission_rate=5.0,
            commission=250.0,
            bonus=100.0,
            penalty=0.0,
            total_salary=1350.0
        )
        for i in range(n)
    ]

async def monitor_loop(stop_event, check_interval=0.01):
    """Monitors the event loop lag."""
    max_lag = 0
    while not stop_event.is_set():
        loop_start = time.time()
        await asyncio.sleep(check_interval)
        now = time.time()
        lag = now - loop_start - check_interval
        max_lag = max(max_lag, lag)
    return max_lag

async def benchmark():
    # Use AsyncMock to mimic the async nature of calculate_salary
    with patch("app.routers.salary.calculate_salary", new_callable=MagicMock) as mock_calc:
        # Make the mock return an awaitable that resolves to the data
        future = asyncio.Future()
        future.set_result(create_mock_data(20000))
        mock_calc.return_value = future

        stop_event = asyncio.Event()
        # Start monitor
        monitor_task = asyncio.create_task(monitor_loop(stop_event))

        print("Starting benchmark...")
        # Yield to allow monitor_loop to start
        await asyncio.sleep(0.1)

        start = time.time()
        await export_salary_excel(2023, 10)
        end = time.time()

        stop_event.set()
        max_lag = await monitor_task

        print(f"Execution time: {end - start:.4f}s")
        print(f"Max event loop lag: {max_lag:.4f}s")

if __name__ == "__main__":
    asyncio.run(benchmark())
