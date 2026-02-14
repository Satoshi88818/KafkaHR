"""Core components for Kafka Robot Fleet."""

from .schemas import (
    TELEMETRY_SCHEMA_STR,
    COMMAND_SCHEMA_STR,
    COMPLETION_SCHEMA_STR,
    EMERGENCY_HALT_SCHEMA_STR,
    IDEMPOTENCY_SCHEMA_STR,
    STATE_SCHEMA_STR,
)

from .security import (
    sign_message,
    verify_signature,
    verify_against_trusted_keys,
)

from .metrics import (
    COMMANDS_ISSUED,
    COMMAND_COMPLETIONS,
    DLQ_ENTRIES,
    TRANSACTION_DURATION,
    CONSUMER_LAG,
    PROCESSED_TELEMETRY,
    TELEMETRY_SENT,
)

__all__ = [
    # Schemas
    'TELEMETRY_SCHEMA_STR',
    'COMMAND_SCHEMA_STR',
    'COMPLETION_SCHEMA_STR',
    'EMERGENCY_HALT_SCHEMA_STR',
    'IDEMPOTENCY_SCHEMA_STR',
    'STATE_SCHEMA_STR',
    # Security
    'sign_message',
    'verify_signature',
    'verify_against_trusted_keys',
    # Metrics
    'COMMANDS_ISSUED',
    'COMMAND_COMPLETIONS',
    'DLQ_ENTRIES',
    'TRANSACTION_DURATION',
    'CONSUMER_LAG',
    'PROCESSED_TELEMETRY',
    'TELEMETRY_SENT',
]
