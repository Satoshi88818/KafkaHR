# Quick Start Guide

Get up and running with Kafka Robot Fleet in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for local Kafka)
- Git (optional)

## Step 1: Install Dependencies

```bash
cd kafka_robot_fleet
pip install -r requirements.txt
```

## Step 2: Start Local Kafka Cluster

```bash
docker-compose up -d
```

This starts:
- Zookeeper (port 2181)
- Kafka (port 9092)
- Schema Registry (port 8081)
- Prometheus (port 9090)
- Grafana (port 3000)

Wait ~30 seconds for services to be ready.

## Step 3: Configure Environment

```bash
cp .env.example .env
```

The defaults work for local development!

## Step 4: Install Package

```bash
pip install -e .
```

## Step 5: Run Tests

```bash
pytest -v
```

You should see all tests passing:

```
tests/test_all.py::TestConfiguration::test_settings_defaults PASSED
tests/test_all.py::TestConfiguration::test_topic_names PASSED
tests/test_all.py::TestCryptographicSecurity::test_sign_message PASSED
...
======================== 34 passed in 2.5s ========================
```

## Step 6: Generate Test Coverage

```bash
pytest --cov=kafka_robot_fleet --cov-report=html
```

Open `htmlcov/index.html` in your browser to see coverage report.

## What's Next?

### Run the Full Application

The complete application code would be in:
- `kafka_robot_fleet/main.py` (entry point)
- `consumers/` directory (consumer implementations)
- `producers/` directory (producer implementations)

### Monitor with Prometheus

1. Open http://localhost:9090
2. Query metrics: `robot_commands_issued_total`

### Visualize with Grafana

1. Open http://localhost:3000
2. Login: admin/admin
3. Add Prometheus datasource
4. Create dashboards

### Explore the Code

Start with:
1. `config/settings.py` - Configuration
2. `core/schemas.py` - Data structures
3. `tests/test_all.py` - Examples of usage

## Common Commands

```bash
# Run specific test
pytest tests/test_all.py::TestCryptographicSecurity::test_sign_message -v

# Run with coverage
pytest --cov=kafka_robot_fleet --cov-report=term-missing

# Format code
black kafka_robot_fleet/

# Lint code
flake8 kafka_robot_fleet/

# Type check
mypy kafka_robot_fleet/
```

## Troubleshooting

### Kafka not starting

```bash
# Check logs
docker-compose logs kafka

# Restart
docker-compose down
docker-compose up -d
```

### Import errors

```bash
# Reinstall in development mode
pip install -e .
```

### Port conflicts

Edit `docker-compose.yml` to change ports if needed.

## Clean Up

```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Remove Python cache
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

## Need Help?

- Read the full [README.md](README.md)
- Check the [TESTING.md](TESTING.md) guide
- Review [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)
