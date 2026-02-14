# Kafka Robot Fleet Management System

A production-grade, event-driven robot fleet management system built on Apache Kafka with advanced features including cryptographic signing, transactional processing, and comprehensive observability.

## Overview

This system manages a fleet of autonomous robots operating in a lunar/planetary environment. It demonstrates enterprise-grade Kafka patterns including:

- **Avro Schema Registry** integration for schema evolution
- **Transactional processing** with exactly-once semantics
- **Cryptographic signing** using Ed25519 for command authentication
- **Dead Letter Queue (DLQ)** pattern with automatic retry logic
- **Idempotency** guarantees for command execution
- **Prometheus metrics** for observability
- **OpenTelemetry** instrumentation
- **Canary deployments** with gradual rollout capabilities
- **Emergency halt** mechanisms for fleet-wide safety

## Architecture

### Components

1. **Robot Producers** - Generate telemetry data (position, status, environment)
2. **Control Center Consumer** - Processes telemetry and issues commands
3. **Safety Monitor Consumer** - Monitors for dangerous conditions
4. **Robot Command Consumer** - Executes commands on robots with transactional guarantees
5. **Retry Consumer** - Handles failed commands with exponential backoff
6. **DLQ Processor** - Monitors poison pills and failed messages

### Kafka Topics

| Topic | Purpose | Retention |
|-------|---------|-----------|
| `robot-telemetry-control` | Robot position and status data | 7 days |
| `robot-telemetry-safety` | Environmental safety telemetry | 7 days |
| `robot-commands` | Commands to be executed by robots | 7 days |
| `robot-commands-retry` | Failed commands for retry | 7 days |
| `robot-command-completions` | Command execution results | 7 days |
| `robot-commands-dlq` | Poison pill messages | 1 day |
| `robot-emergency-halt` | Emergency stop signals | 7 days |
| `robot-idempotency-store` | Command deduplication | 7 days |
| `robot-state` | Persistent robot state | Compacted |

## Features

### 1. Cryptographic Command Signing

Commands can be cryptographically signed using Ed25519 keys for authentication:

```python
# Commands are signed with private keys
# Robots verify signatures against trusted public keys
```

### 2. Transactional Processing

Commands are processed with exactly-once semantics:
- Atomic read-process-write operations
- Automatic offset management
- Rollback on failures

### 3. Retry with Exponential Backoff

Failed commands are automatically retried:
- Initial backoff: 1 second
- Exponential increase: 2^retry_count
- Maximum retries: 5
- Poison pills moved to DLQ

### 4. Idempotency

Commands are executed exactly once:
- Command IDs tracked in `robot-idempotency-store`
- Duplicate commands are skipped
- State is consistent across retries

### 5. Canary Deployments

Gradual rollout of new commands:
- 10% of fleet receives real commands (configurable)
- 90% receives dry-run commands
- Safe testing of new behaviors

### 6. Emergency Halt

Fleet-wide emergency stop capability:
- Broadcasts halt command to all robots
- Immediate velocity reduction to zero
- State preserved for recovery

### 7. Observability

Comprehensive metrics exposed via Prometheus:
- `robot_commands_issued_total` - Commands issued by source and action
- `robot_command_completions_total` - Command completions by status
- `robot_dlq_entries_total` - DLQ message count
- `robot_transaction_duration_seconds` - Transaction timing
- `robot_consumer_lag` - Consumer lag per partition
- `robot_telemetry_processed_total` - Telemetry processing rate
- `robot_telemetry_sent_total` - Telemetry production rate

## Installation

### Prerequisites

- Python 3.8+
- Apache Kafka 2.8+
- Confluent Schema Registry
- Docker (optional, for local Kafka setup)

### Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- aiokafka
- confluent-kafka[avro]
- pydantic
- prometheus-client
- opentelemetry-instrumentation-aiokafka
- cryptography
- numpy

### Local Development Setup

1. Start Kafka and Schema Registry using Docker Compose:

```bash
docker-compose up -d
```

2. Generate cryptographic keys (optional):

```bash
python -m kafka_robot_fleet.utils.keygen
```

3. Configure environment variables:

```bash
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Configuration is managed via environment variables or `.env` file:

### Kafka Configuration

```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SCHEMA_REGISTRY_URL=http://localhost:8081
SASL_MECHANISM=PLAIN
SASL_USERNAME=your_username
SASL_PASSWORD=your_password
```

### Cryptographic Keys

```bash
CONTROL_PRIVATE_KEY_B64=<base64_encoded_private_key>
CONTROL_PUBLIC_KEY_B64=<base64_encoded_public_key>
SAFETY_PRIVATE_KEY_B64=<base64_encoded_private_key>
SAFETY_PUBLIC_KEY_B64=<base64_encoded_public_key>
```

### Application Settings

```bash
DEFAULT_NUM_ROBOTS=1000
DEFAULT_TELEMETRY_INTERVAL=1.0
MAX_RETRIES=5
COMMAND_TIMEOUT_SEC=600.0
CHAOS_INJECTION_PROB=0.0
SIMULATION_SPEEDUP=1.0
CANARY_FRACTION=0.1
```

## Usage

### Run the Demo

```bash
python -m kafka_robot_fleet.main --num-robots 1000 --telemetry-interval 1.0
```

### Command Line Options

- `--num-robots` - Number of robots in fleet (default: 1000)
- `--telemetry-interval` - Telemetry reporting interval in seconds (default: 1.0)
- `--mode` - Operation mode (currently only 'demo' supported)

### Monitoring

Prometheus metrics are exposed on port 8000:

```bash
curl http://localhost:8000/metrics
```

## Development

### Project Structure

```
kafka_robot_fleet/
├── __init__.py
├── main.py                 # Application entry point
├── config/
│   ├── __init__.py
│   └── settings.py         # Configuration management
├── core/
│   ├── __init__.py
│   ├── schemas.py          # Avro schemas
│   ├── security.py         # Cryptographic signing/verification
│   └── metrics.py          # Prometheus metrics
├── consumers/
│   ├── __init__.py
│   ├── control_center.py   # Control center consumer
│   ├── safety_monitor.py   # Safety monitoring consumer
│   ├── robot_commands.py   # Robot command executor
│   ├── retry.py            # Retry consumer
│   └── dlq.py              # Dead letter queue processor
├── producers/
│   ├── __init__.py
│   └── robot_telemetry.py  # Robot telemetry producer
├── utils/
│   ├── __init__.py
│   ├── kafka_helpers.py    # Kafka utility functions
│   ├── logging.py          # JSON logging formatter
│   └── keygen.py           # Key generation utility
└── tests/
    ├── __init__.py
    ├── test_config.py
    ├── test_security.py
    ├── test_consumers.py
    ├── test_producers.py
    └── test_integration.py
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kafka_robot_fleet --cov-report=html

# Run specific test file
pytest tests/test_security.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black kafka_robot_fleet/

# Lint code
flake8 kafka_robot_fleet/

# Type checking
mypy kafka_robot_fleet/
```

## Advanced Features

### Chaos Engineering

Enable chaos injection to test system resilience:

```bash
CHAOS_INJECTION_PROB=0.05  # 5% random failures
```

### Simulation Speedup

Accelerate simulation for testing:

```bash
SIMULATION_SPEEDUP=10.0  # 10x faster simulation
```

### Custom Partitioning Strategy

Adjust partitioning for scalability:

```bash
PARTITIONS_PER_100_ROBOTS=1  # 1 partition per 100 robots
```

## Performance Tuning

### Producer Configuration

- Batch size: Adjust for throughput vs latency
- Compression: Use `gzip` or `snappy` for high-volume topics
- Acks: Set to `all` for durability

### Consumer Configuration

- Fetch size: Increase for better throughput
- Max poll records: Tune for processing rate
- Session timeout: Adjust for rebalancing behavior

### Kafka Cluster

- Partition count: Scale based on parallelism needs
- Replication factor: Set to 3 for production
- Min in-sync replicas: Set to 2 for durability

## Troubleshooting

### Common Issues

**Consumer lag increasing:**
- Check partition count and consumer instances
- Verify processing logic performance
- Monitor Prometheus `robot_consumer_lag` metric

**Messages in DLQ:**
- Review DLQ processor logs
- Check command schema compatibility
- Verify robot state consistency

**Transaction timeouts:**
- Increase `COMMAND_TIMEOUT_SEC`
- Reduce batch sizes
- Check Kafka broker health

**Signature verification failures:**
- Verify public/private key configuration
- Check key encoding (base64)
- Ensure keys match between components

## Security Considerations

1. **Encryption in Transit**: Use TLS for Kafka connections in production
2. **Authentication**: Enable SASL authentication
3. **Authorization**: Configure Kafka ACLs
4. **Key Management**: Store private keys in secure vaults (e.g., HashiCorp Vault)
5. **Schema Registry Security**: Enable authentication and HTTPS

## Production Deployment

### Recommendations

1. Use Kubernetes for container orchestration
2. Deploy Schema Registry in HA mode
3. Enable monitoring with Prometheus and Grafana
4. Set up alerting for consumer lag and DLQ entries
5. Use separate Kafka clusters for dev/staging/prod
6. Implement automated rollback procedures
7. Regular backup of Kafka topics and Schema Registry

### Health Checks

Implement health check endpoints:
- Kafka connectivity
- Schema Registry availability
- Consumer lag thresholds
- DLQ message count

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- Apache Kafka community
- Confluent Platform
- OpenTelemetry project
- Cryptography library maintainers
