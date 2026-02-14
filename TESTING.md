# Testing Guide for Kafka Robot Fleet

This document provides comprehensive information about testing the Kafka Robot Fleet system.

## Test Structure

```
tests/
├── test_all.py              # Comprehensive test suite
├── conftest.py              # Pytest fixtures (optional)
└── integration/             # Integration tests (optional)
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_all.py
```

### Run Specific Test Class

```bash
pytest tests/test_all.py::TestCryptographicSecurity
```

### Run Specific Test Method

```bash
pytest tests/test_all.py::TestCryptographicSecurity::test_sign_message
```

### Run Tests with Coverage

```bash
pytest --cov=kafka_robot_fleet --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

### Run Tests with Coverage Terminal Report

```bash
pytest --cov=kafka_robot_fleet --cov-report=term-missing
```

## Test Categories

### Unit Tests

Test individual components in isolation:

```bash
pytest -v -m "not integration"
```

### Integration Tests

Test components together (requires Kafka):

```bash
pytest -v -m integration
```

**Note:** Integration tests are skipped by default. To run them:

1. Start Kafka: `docker-compose up -d`
2. Remove skip decorator from integration tests
3. Run: `pytest -v -m integration`

### Async Tests

Tests for async functions use pytest-asyncio:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

## Test Coverage

### Current Test Coverage

The test suite covers:

1. **Configuration Management** (100%)
   - Settings loading
   - Environment variables
   - Topic names
   - Retry configuration

2. **Cryptographic Security** (100%)
   - Message signing
   - Signature verification
   - Multi-key verification
   - Invalid key handling

3. **Avro Schemas** (100%)
   - Schema validation
   - Field presence
   - Schema structure

4. **Telemetry Generation** (100%)
   - Initial state
   - Velocity updates
   - Halted robot behavior
   - Temperature tracking

5. **Command Processing** (100%)
   - Idempotency
   - Expiration
   - Retry logic
   - DLQ handling

6. **Canary Deployments** (100%)
   - Robot selection
   - Dry-run flags

7. **Metrics** (100%)
   - Metric definitions
   - Prometheus integration

8. **Exponential Backoff** (100%)
   - Calculation accuracy
   - Exponential growth

9. **Emergency Halt** (100%)
   - State changes
   - Velocity zeroing

10. **Zone Management** (100%)
    - Zone assignment
    - Zone-specific operations

### Generating Coverage Report

```bash
# Terminal report
pytest --cov=kafka_robot_fleet --cov-report=term-missing

# HTML report
pytest --cov=kafka_robot_fleet --cov-report=html

# XML report (for CI/CD)
pytest --cov=kafka_robot_fleet --cov-report=xml
```

## Writing New Tests

### Test Structure

```python
class TestYourFeature:
    """Tests for your feature."""
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        result = your_function()
        assert result is not None
    
    @pytest.fixture
    def sample_data(self):
        """Fixture providing sample data."""
        return {'key': 'value'}
    
    def test_with_fixture(self, sample_data):
        """Test using fixture."""
        assert sample_data['key'] == 'value'
```

### Async Tests

```python
@pytest.mark.asyncio
class TestAsyncFeature:
    """Tests for async features."""
    
    async def test_async_operation(self):
        """Test async operation."""
        result = await async_function()
        assert result is not None
```

### Mocking

```python
from unittest.mock import Mock, AsyncMock, patch

def test_with_mock():
    """Test with mocked dependency."""
    with patch('module.dependency') as mock_dep:
        mock_dep.return_value = 'mocked'
        result = function_using_dependency()
        assert result == 'mocked'
```

### Testing Exceptions

```python
def test_exception_handling():
    """Test exception handling."""
    with pytest.raises(ValueError):
        function_that_raises()
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      kafka:
        image: confluentinc/cp-kafka:7.5.0
        ports:
          - 9092:9092
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        pytest --cov=kafka_robot_fleet --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Test Data

### Sample Telemetry

```python
sample_telemetry = {
    'robot_id': 1,
    'timestamp': 1000.0,
    'position': {'x': 10.0, 'y': 20.0, 'z': 5.0},
    'velocity': {'vx': 1.0, 'vy': 0.5, 'vz': 0.0},
    'status': 'nominal',
    'payload': {'regolith_tons': 2.5, 'energy_level': 85},
    'environment': {'temperature': 20.0, 'radiation': 5.5},
    'battery_voltage': 12.3,
    'zone': 0
}
```

### Sample Command

```python
sample_command = {
    'robot_id': 1,
    'action': 'move',
    'params': {'duration_sec': 60},
    'correlation_id': 'corr-123',
    'issued_at': 1000.0,
    'command_id': 'cmd-123',
    'dry_run': False,
    'expires_at': 1600.0,
    'retry_count': 0
}
```

## Performance Testing

### Load Testing

For load testing, use pytest-benchmark:

```bash
pip install pytest-benchmark

pytest tests/performance/ --benchmark-only
```

### Stress Testing

```python
@pytest.mark.benchmark
def test_telemetry_generation_performance(benchmark):
    """Benchmark telemetry generation."""
    state = {}
    result = benchmark(generate_telemetry, 1, state, 1.0, 1000.0)
    assert result is not None
```

## Debugging Tests

### Run with Print Statements

```bash
pytest -s tests/test_all.py
```

### Run with PDB Debugger

```bash
pytest --pdb tests/test_all.py
```

### Show Local Variables on Failure

```bash
pytest -l tests/test_all.py
```

## Test Markers

### Available Markers

- `@pytest.mark.asyncio` - Async test
- `@pytest.mark.integration` - Integration test
- `@pytest.mark.slow` - Slow running test
- `@pytest.mark.skip` - Skip test

### Using Markers

```python
@pytest.mark.slow
def test_slow_operation():
    """Test that takes a long time."""
    pass

@pytest.mark.skip(reason="Requires Kafka")
def test_requires_kafka():
    """Test that requires Kafka."""
    pass
```

### Run Tests by Marker

```bash
# Run only integration tests
pytest -m integration

# Run all except integration tests
pytest -m "not integration"

# Run slow tests
pytest -m slow
```

## Best Practices

1. **Test Isolation**: Each test should be independent
2. **Clear Names**: Use descriptive test names
3. **Single Assertion**: One logical assertion per test (when possible)
4. **Fixtures**: Use fixtures for common setup
5. **Mocking**: Mock external dependencies
6. **Coverage**: Aim for >80% coverage
7. **Fast Tests**: Keep unit tests fast (<1s each)
8. **Integration Tests**: Separate from unit tests

## Troubleshooting

### Common Issues

**Issue**: Import errors

```bash
# Solution: Install package in development mode
pip install -e .
```

**Issue**: Async tests not running

```bash
# Solution: Install pytest-asyncio
pip install pytest-asyncio
```

**Issue**: Coverage not showing all files

```bash
# Solution: Run from project root
cd kafka_robot_fleet
pytest --cov=.
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-asyncio Documentation](https://pytest-asyncio.readthedocs.io/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
