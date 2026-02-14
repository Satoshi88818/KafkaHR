"""Prometheus metrics for Kafka Robot Fleet."""

from prometheus_client import Counter, Gauge, Histogram

# Command metrics
COMMANDS_ISSUED = Counter(
    'robot_commands_issued_total',
    'Commands issued by source and action',
    ['source', 'action']
)

COMMAND_COMPLETIONS = Counter(
    'robot_command_completions_total',
    'Command completions by status',
    ['status']
)

# DLQ metrics
DLQ_ENTRIES = Counter(
    'robot_dlq_entries_total',
    'Messages sent to DLQ'
)

# Performance metrics
TRANSACTION_DURATION = Histogram(
    'robot_transaction_duration_seconds',
    'Transaction durations',
    ['component']
)

# Consumer metrics
CONSUMER_LAG = Gauge(
    'robot_consumer_lag',
    'Consumer lag per topic-partition',
    ['group', 'topic', 'partition']
)

# Telemetry metrics
PROCESSED_TELEMETRY = Counter(
    'robot_telemetry_processed_total',
    'Telemetry messages processed',
    ['component']
)

TELEMETRY_SENT = Counter(
    'robot_telemetry_sent_total',
    'Telemetry messages sent by producer'
)
