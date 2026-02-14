"""Configuration management for Kafka Robot Fleet."""

import base64
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application configuration settings."""
    
    # Kafka configuration
    bootstrap_servers: str = Field(default="localhost:9092", env="KAFKA_BOOTSTRAP_SERVERS")
    schema_registry_url: str = Field(default="http://localhost:8081", env="SCHEMA_REGISTRY_URL")
    sasl_mechanism: str = Field(default="PLAIN", env="SASL_MECHANISM")
    sasl_username: str = Field(default=None, env="SASL_USERNAME")
    sasl_password: str = Field(default=None, env="SASL_PASSWORD")

    # Cryptographic keys (base64 encoded)
    control_private_key_b64: str = Field(default="", env="CONTROL_PRIVATE_KEY_B64")
    control_public_key_b64: str = Field(default="", env="CONTROL_PUBLIC_KEY_B64")
    safety_private_key_b64: str = Field(default="", env="SAFETY_PRIVATE_KEY_B64")
    safety_public_key_b64: str = Field(default="", env="SAFETY_PUBLIC_KEY_B64")

    # Topic names
    control_telemetry_topic: str = "robot-telemetry-control"
    safety_telemetry_topic: str = "robot-telemetry-safety"
    commands_topic: str = "robot-commands"
    retry_topic: str = "robot-commands-retry"
    completions_topic: str = "robot-command-completions"
    dlq_topic: str = "robot-commands-dlq"
    emergency_halt_topic: str = "robot-emergency-halt"
    idempotency_topic: str = "robot-idempotency-store"
    robot_state_topic: str = "robot-state"

    # Application settings
    default_num_robots: int = 1000
    default_telemetry_interval: float = 1.0
    dlq_retention_ms: int = 86400000  # 1 day
    idempotency_retention_ms: int = 604800000  # 7 days
    max_retries: int = 5
    initial_backoff_sec: float = 1.0
    command_timeout_sec: float = 600.0
    partitions_per_100_robots: int = 1
    chaos_injection_prob: float = 0.0
    simulation_speedup: float = 1.0
    canary_fraction: float = 0.1  # 10% of robots get real commands

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()

# Security protocol configuration
SECURITY_PROTOCOL = "SASL_PLAINTEXT" if settings.sasl_username else "PLAINTEXT"

# Decode cryptographic keys
CONTROL_PRIVATE_KEY = base64.b64decode(settings.control_private_key_b64) if settings.control_private_key_b64 else b""
CONTROL_PUBLIC_KEY = base64.b64decode(settings.control_public_key_b64) if settings.control_public_key_b64 else b""
SAFETY_PRIVATE_KEY = base64.b64decode(settings.safety_private_key_b64) if settings.safety_private_key_b64 else b""
SAFETY_PUBLIC_KEY = base64.b64decode(settings.safety_public_key_b64) if settings.safety_public_key_b64 else b""

# List of trusted public keys
TRUSTED_PUBLIC_KEYS = [k for k in (CONTROL_PUBLIC_KEY, SAFETY_PUBLIC_KEY) if k]
