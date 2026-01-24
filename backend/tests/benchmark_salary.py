import pytest
from unittest.mock import MagicMock, patch
from app.routers.salary import calculate_salary
from uuid import uuid4
import time

@pytest.mark.asyncio
async def test_benchmark_salary(mock_supabase):
    # Setup Data
    num_agents = 100
    sales_per_agent = 50

    agents_data = []

    for i in range(num_agents):
        agent_id = str(uuid4())

        # Prepare embedded sales
        agent_sales = []
        for j in range(sales_per_agent):
            agent_sales.append({
                "agent_id": agent_id,
                "total_amount": 1000,
                "sale_date": "2023-01-15"
            })

        # Prepare embedded calcs
        agent_calcs = []
        if i % 2 == 0:
            agent_calcs.append({
                "agent_id": agent_id,
                "penalty": 500,
                "bonus": 0,
                "notes": "Late",
                "year": 2023,
                "month": 1
            })

        agents_data.append({
            "id": agent_id,
            "name": f"Agent {i}",
            "base_salary": 50000,
            "commission_rate": 5,
            "bonus_threshold": 100000,
            "bonus_amount": 5000,
            "is_active": True,
            "sales": agent_sales,
            "salary_calculations": agent_calcs
        })

    # Configure Mock
    # New chain:
    # .select("...").eq("is_active", True)
    # .gte("sales.sale_date", ...)
    # .lt("sales.sale_date", ...)
    # .eq("salary_calculations.year", ...)
    # .eq("salary_calculations.month", ...)
    # .execute()

    mock_query = MagicMock()

    # We need to construct the chain correctly.
    # select() -> eq() -> gte() -> lt() -> eq() -> eq() -> execute()

    # Let's simplify and make any sequence of calls end up returning the data
    chain = mock_query.select.return_value
    chain.eq.return_value = chain # Allow chaining
    chain.gte.return_value = chain
    chain.lt.return_value = chain

    # The final .execute() returns data
    chain.execute.return_value.data = agents_data

    # Also handle the .eq chained calls which return self (the query builder)

    mock_supabase.table.return_value = mock_query

    # Patch the supabase in the router module
    with patch("app.routers.salary.supabase", mock_supabase):
        # Run Benchmark
        start_time = time.time()
        results = await calculate_salary(year=2023, month=1)
        end_time = time.time()

        print(f"\nExecution time: {end_time - start_time:.4f}s")

        # Verify Results
        assert len(results) == num_agents
        assert results[0].sales_amount == 50000  # 50 * 1000

        # Verify Call Counts
        # table() is called 1 time only (for agents)
        assert mock_supabase.table.call_count == 1

        # Verify call arguments
        mock_supabase.table.assert_called_with("agents")

        print("Optimization verified: 1 query.")
