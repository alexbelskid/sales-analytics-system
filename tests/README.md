# Tests

Integration and end-to-end tests for the Sales Analytics System.

## Structure

```
tests/
├── integration/        # Backend integration tests
│   ├── test_advanced_analytics.sh
│   ├── test_import_logic.py
│   ├── test_import_proof.py
│   ├── test_supabase_insert.py
│   └── verify_backend.py
├── e2e/               # End-to-end browser tests
├── fixtures/          # Test data
│   ├── test_advanced_sales.csv
│   ├── test_sales_upload.csv
│   └── abc_xyz_test.json
├── tests.json         # Test results
└── README.md          # This file
```

## Running Tests

### Integration Tests

Tests that verify backend functionality:

```bash
# Test backend API
cd tests/integration
python verify_backend.py

# Test Supabase connection
python test_supabase_insert.py

# Test import logic
python test_import_logic.py test_import_proof.py
```

### Advanced Analytics Test

```bash
chmod +x tests/integration/test_advanced_analytics.sh
./tests/integration/test_advanced_analytics.sh
```

## Test Data

Test fixtures are located in `tests/fixtures/`:

- `test_sales_upload.csv` - Small dataset for upload tests
- `test_advanced_sales.csv` - Dataset for analytics tests
- `abc_xyz_test.json` - Configuration test data

**Note:** Test data is separate from `database/seeds/` which is for development.

## Writing Tests

### Backend Tests

Located in `backend/tests/`:
- Unit tests for services
- Model validation tests
- API endpoint tests

### Integration Tests

Located here in `tests/integration/`:
- Full workflow tests
- Database interaction tests
- External API tests

### E2E Tests

Located in `tests/e2e/`:
- Browser automation tests
- Full user journey tests

## Related Documentation

- [Backend Tests](../backend/tests/README.md)
- [Troubleshooting](../docs/TROUBLESHOOTING.md)
- [CI/CD Setup](../docs/DEPLOYMENT.md#testing)
