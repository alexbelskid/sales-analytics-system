import pytest
import pandas as pd
from unittest.mock import MagicMock, patch, AsyncMock
from io import BytesIO
from app.routers.salary import export_salary_excel, _generate_excel_sync
from app.models.agents import SalaryCalculation
import uuid

def create_mock_data(n=10):
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

def test_generate_excel_sync():
    """Test the synchronous Excel generation function directly."""
    data = create_mock_data(5)
    output = _generate_excel_sync(data, 10, 2023)

    assert isinstance(output, BytesIO)
    output.seek(0)

    # Verify it's a valid Excel file by reading it back
    df = pd.read_excel(output)

    # Check columns
    expected_columns = ["Агент", "Оклад", "Продажи", "% комиссии", "Комиссия", "Бонус", "Штраф", "ИТОГО"]
    for col in expected_columns:
        assert col in df.columns

    # Check rows (5 data rows + 1 total row)
    assert len(df) == 6

    # Check "Total" row
    assert df.iloc[-1]["Агент"] == "ИТОГО"

@pytest.mark.asyncio
async def test_export_salary_excel_endpoint():
    """Test the export endpoint logic (mocking calculate_salary)."""
    with patch("app.routers.salary.calculate_salary", new_callable=AsyncMock) as mock_calc:
        mock_data = create_mock_data(5)
        mock_calc.return_value = mock_data

        # We also need to mock run_in_executor to ensure it calls our sync function
        # But since we want to test that it actually uses run_in_executor, we can spy on it
        # or just trust the integration.
        # Let's just run it. Asyncio run_in_executor works in tests too.

        response = await export_salary_excel(2023, 10)

        # Check response
        assert response.status_code == 200
        # StreamingResponse headers
        assert "Content-Disposition" in response.headers
        assert "salary_2023_10.xlsx" in response.headers["Content-Disposition"]
