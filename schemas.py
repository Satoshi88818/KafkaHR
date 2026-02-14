"""Avro schemas for Kafka Robot Fleet."""

import json

# Telemetry schema
TELEMETRY_SCHEMA_STR = json.dumps({
    "type": "record", "name": "Telemetry", "namespace": "robot",
    "fields": [
        {"name": "robot_id", "type": "int"},
        {"name": "timestamp", "type": "double"},
        {"name": "position", "type": {"type": "record", "name": "Position", "fields": [
            {"name": "x", "type": "double"}, {"name": "y", "type": "double"}, {"name": "z", "type": "double"}
        ]}},
        {"name": "status", "type": "string"},
        {"name": "payload", "type": {"type": "record", "name": "Payload", "fields": [
            {"name": "regolith_tons", "type": "double"}, {"name": "energy_level", "type": "int"}
        ]}},
        {"name": "environment", "type": {"type": "record", "name": "Environment", "fields": [
            {"name": "temperature", "type": "double"}, {"name": "radiation", "type": "double"}
        ]}},
        {"name": "velocity", "type": {"type": "record", "name": "Velocity", "fields": [
            {"name": "vx", "type": "double", "default": 0.0},
            {"name": "vy", "type": "double", "default": 0.0},
            {"name": "vz", "type": "double", "default": 0.0}
        ]}, "default": {"vx": 0.0, "vy": 0.0, "vz": 0.0}},
        {"name": "battery_voltage", "type": "double", "default": 12.0},
        {"name": "zone", "type": "int", "default": 0}
    ]
})

# Command schema
COMMAND_SCHEMA_STR = json.dumps({
    "type": "record", "name": "Command", "namespace": "robot",
    "fields": [
        {"name": "robot_id", "type": "int"},
        {"name": "action", "type": "string"},
        {"name": "params", "type": {"type": "record", "name": "Params", "fields": [
            {"name": "duration_sec", "type": "int"}
        ]}},
        {"name": "correlation_id", "type": "string"},
        {"name": "issued_at", "type": "double"},
        {"name": "command_id", "type": "string"},
        {"name": "dry_run", "type": "boolean", "default": False},
        {"name": "expires_at", "type": "double", "default": 0.0},
        {"name": "retry_count", "type": "int", "default": 0}
    ]
})

# Completion schema
COMPLETION_SCHEMA_STR = json.dumps({
    "type": "record", "name": "Completion", "namespace": "robot",
    "fields": [
        {"name": "robot_id", "type": "int"},
        {"name": "correlation_id", "type": "string"},
        {"name": "status", "type": "string"},
        {"name": "timestamp", "type": "double"},
        {"name": "diagnostics", "type": {"type": "record", "name": "Diagnostics", "fields": [
            {"name": "errors", "type": {"type": "array", "items": "string"}},
            {"name": "warnings", "type": {"type": "array", "items": "string"}},
            {"name": "duration_ms", "type": "double"}
        ]}}
    ]
})

# Emergency halt schema
EMERGENCY_HALT_SCHEMA_STR = json.dumps({
    "type": "record", "name": "EmergencyHalt", "namespace": "robot",
    "fields": [
        {"name": "issued_at", "type": "double"},
        {"name": "reason", "type": "string"},
        {"name": "zone", "type": "int"},
        {"name": "correlation_id", "type": "string"}
    ]
})

# Idempotency schema
IDEMPOTENCY_SCHEMA_STR = json.dumps({
    "type": "record", "name": "IdempotencyRecord", "namespace": "robot",
    "fields": [
        {"name": "executed_at", "type": "double"}
    ]
})

# Robot state schema
STATE_SCHEMA_STR = json.dumps({
    "type": "record", "name": "RobotState", "namespace": "robot",
    "fields": [
        {"name": "robot_id", "type": "int"},
        {"name": "position", "type": {"type": "record", "name": "StatePosition", "fields": [
            {"name": "x", "type": "double"}, {"name": "y", "type": "double"}, {"name": "z", "type": "double"}
        ]}},
        {"name": "velocity", "type": {"type": "record", "name": "StateVelocity", "fields": [
            {"name": "vx", "type": "double"}, {"name": "vy", "type": "double"}, {"name": "vz", "type": "double"}
        ]}},
        {"name": "temp", "type": "double"},
        {"name": "cooling_until", "type": "double"},
        {"name": "halted", "type": "boolean"},
        {"name": "zone", "type": "int"}
    ]
})
