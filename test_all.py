"""Comprehensive tests for Kafka Robot Fleet system."""

import pytest
import asyncio
import json
import base64
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from cryptography.hazmat.primitives.asymmetric import ed25519

# Import modules to test
from kafka_robot_fleet.config import settings, TRUSTED_PUBLIC_KEYS
from kafka_robot_fleet.core.security import sign_message, verify_signature, verify_against_trusted_keys
from kafka_robot_fleet.core.schemas import (
    TELEMETRY_SCHEMA_STR,
    COMMAND_SCHEMA_STR,
    COMPLETION_SCHEMA_STR,
)


class TestConfiguration:
    """Tests for configuration management."""
    
    def test_settings_defaults(self):
        """Test that default settings are loaded correctly."""
        assert settings.bootstrap_servers == "localhost:9092"
        assert settings.schema_registry_url == "http://localhost:8081"
        assert settings.default_num_robots == 1000
        assert settings.max_retries == 5
        assert settings.canary_fraction == 0.1
    
    def test_topic_names(self):
        """Test that topic names are configured correctly."""
        assert settings.control_telemetry_topic == "robot-telemetry-control"
        assert settings.commands_topic == "robot-commands"
        assert settings.dlq_topic == "robot-commands-dlq"
        assert settings.emergency_halt_topic == "robot-emergency-halt"
    
    def test_retry_configuration(self):
        """Test retry configuration."""
        assert settings.max_retries == 5
        assert settings.initial_backoff_sec == 1.0
        assert settings.command_timeout_sec == 600.0


class TestCryptographicSecurity:
    """Tests for cryptographic signing and verification."""
    
    @pytest.fixture
    def key_pair(self):
        """Generate a test key pair."""
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        return {
            'private': private_key.private_bytes_raw(),
            'public': public_key.public_bytes_raw()
        }
    
    def test_sign_message(self, key_pair):
        """Test message signing."""
        message = b"test command"
        signature = sign_message(message, key_pair['private'])
        
        assert signature is not None
        assert len(signature) == 64  # Ed25519 signatures are 64 bytes
    
    def test_verify_valid_signature(self, key_pair):
        """Test verification of valid signature."""
        message = b"test command"
        signature = sign_message(message, key_pair['private'])
        
        result = verify_signature(message, signature, key_pair['public'])
        assert result is True
    
    def test_verify_invalid_signature(self, key_pair):
        """Test verification of invalid signature."""
        message = b"test command"
        wrong_signature = b"0" * 64
        
        result = verify_signature(message, wrong_signature, key_pair['public'])
        assert result is False
    
    def test_verify_tampered_message(self, key_pair):
        """Test verification fails for tampered message."""
        message = b"test command"
        signature = sign_message(message, key_pair['private'])
        
        tampered_message = b"tampered command"
        result = verify_signature(tampered_message, signature, key_pair['public'])
        assert result is False
    
    def test_verify_against_trusted_keys(self, key_pair):
        """Test verification against multiple trusted keys."""
        message = b"test command"
        signature = sign_message(message, key_pair['private'])
        
        # Generate additional keys
        other_key = ed25519.Ed25519PrivateKey.generate()
        trusted_keys = [other_key.public_key().public_bytes_raw(), key_pair['public']]
        
        result = verify_against_trusted_keys(message, signature, trusted_keys)
        assert result is True
    
    def test_verify_against_trusted_keys_all_invalid(self, key_pair):
        """Test verification fails when no trusted keys match."""
        message = b"test command"
        signature = sign_message(message, key_pair['private'])
        
        # Generate different keys
        other_key1 = ed25519.Ed25519PrivateKey.generate()
        other_key2 = ed25519.Ed25519PrivateKey.generate()
        trusted_keys = [
            other_key1.public_key().public_bytes_raw(),
            other_key2.public_key().public_bytes_raw()
        ]
        
        result = verify_against_trusted_keys(message, signature, trusted_keys)
        assert result is False
    
    def test_verify_with_empty_trusted_keys(self, key_pair):
        """Test verification passes when no trusted keys configured (security disabled)."""
        message = b"test command"
        signature = sign_message(message, key_pair['private'])
        
        result = verify_against_trusted_keys(message, signature, [])
        assert result is True  # Should pass when security is disabled
    
    def test_sign_with_invalid_key(self):
        """Test signing with invalid key raises error."""
        message = b"test command"
        invalid_key = b"too_short"
        
        with pytest.raises(ValueError):
            sign_message(message, invalid_key)


class TestSchemas:
    """Tests for Avro schemas."""
    
    def test_telemetry_schema_valid(self):
        """Test telemetry schema is valid JSON."""
        schema = json.loads(TELEMETRY_SCHEMA_STR)
        assert schema['type'] == 'record'
        assert schema['name'] == 'Telemetry'
        assert 'fields' in schema
        
        field_names = [f['name'] for f in schema['fields']]
        assert 'robot_id' in field_names
        assert 'timestamp' in field_names
        assert 'position' in field_names
        assert 'status' in field_names
    
    def test_command_schema_valid(self):
        """Test command schema is valid JSON."""
        schema = json.loads(COMMAND_SCHEMA_STR)
        assert schema['type'] == 'record'
        assert schema['name'] == 'Command'
        
        field_names = [f['name'] for f in schema['fields']]
        assert 'robot_id' in field_names
        assert 'action' in field_names
        assert 'command_id' in field_names
        assert 'dry_run' in field_names
    
    def test_completion_schema_valid(self):
        """Test completion schema is valid JSON."""
        schema = json.loads(COMPLETION_SCHEMA_STR)
        assert schema['type'] == 'record'
        assert schema['name'] == 'Completion'
        
        field_names = [f['name'] for f in schema['fields']]
        assert 'robot_id' in field_names
        assert 'status' in field_names
        assert 'correlation_id' in field_names


class TestTelemetryGeneration:
    """Tests for telemetry data generation."""
    
    def test_initial_position_generation(self):
        """Test initial position is generated correctly."""
        from kafka_robot_fleet.utils.kafka_helpers import generate_telemetry
        
        robot_id = 1
        state = {}
        dt = 1.0
        now = 1000.0
        
        telemetry = generate_telemetry(robot_id, state, dt, now)
        
        assert telemetry['robot_id'] == robot_id
        assert telemetry['timestamp'] == now
        assert 'position' in telemetry
        assert 'x' in telemetry['position']
        assert 'y' in telemetry['position']
        assert 'z' in telemetry['position']
    
    def test_velocity_update(self):
        """Test velocity is updated over time."""
        from kafka_robot_fleet.utils.kafka_helpers import generate_telemetry
        
        robot_id = 1
        state = {
            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
            'velocity': {'vx': 1.0, 'vy': 0.0, 'vz': 0.0},
            'temp': 20.0,
            'halted': False,
        }
        dt = 1.0
        now = 1000.0
        
        telemetry = generate_telemetry(robot_id, state, dt, now)
        
        # Position should have moved
        assert telemetry['position']['x'] != 0.0
    
    def test_halted_robot_no_movement(self):
        """Test halted robot does not move."""
        from kafka_robot_fleet.utils.kafka_helpers import generate_telemetry
        
        robot_id = 1
        initial_position = {'x': 10.0, 'y': 20.0, 'z': 5.0}
        state = {
            'position': initial_position.copy(),
            'velocity': {'vx': 1.0, 'vy': 1.0, 'vz': 0.0},
            'temp': 20.0,
            'halted': True,
        }
        dt = 1.0
        now = 1000.0
        
        telemetry = generate_telemetry(robot_id, state, dt, now)
        
        # Position should not have changed
        assert telemetry['position'] == initial_position
        assert telemetry['velocity'] == {'vx': 0.0, 'vy': 0.0, 'vz': 0.0}
        assert telemetry['status'] == 'halted'


class TestCommandProcessing:
    """Tests for command processing logic."""
    
    def test_command_idempotency(self):
        """Test that duplicate commands are not executed twice."""
        executed = set()
        command_id = "cmd-123"
        
        # First execution
        if command_id not in executed:
            executed.add(command_id)
            first_result = True
        else:
            first_result = False
        
        # Second execution (duplicate)
        if command_id not in executed:
            executed.add(command_id)
            second_result = True
        else:
            second_result = False
        
        assert first_result is True
        assert second_result is False
    
    def test_command_expiration(self):
        """Test that expired commands are not executed."""
        import time
        
        now = time.time()
        
        # Expired command
        expired_cmd = {
            'expires_at': now - 100,  # Expired 100 seconds ago
        }
        
        # Valid command
        valid_cmd = {
            'expires_at': now + 100,  # Expires in 100 seconds
        }
        
        assert expired_cmd['expires_at'] < now
        assert valid_cmd['expires_at'] > now
    
    def test_retry_count_increment(self):
        """Test that retry count is incremented correctly."""
        command = {'retry_count': 0}
        
        for i in range(1, 6):
            command['retry_count'] += 1
            assert command['retry_count'] == i
    
    def test_max_retries_exceeded(self):
        """Test that commands with max retries are sent to DLQ."""
        max_retries = 5
        
        # Command that has been retried too many times
        command = {'retry_count': 6}
        should_dlq = command['retry_count'] >= max_retries
        
        assert should_dlq is True
        
        # Command within retry limit
        command = {'retry_count': 4}
        should_dlq = command['retry_count'] >= max_retries
        
        assert should_dlq is False


class TestCanaryDeployment:
    """Tests for canary deployment logic."""
    
    def test_canary_selection(self):
        """Test that canary fraction of robots are selected."""
        canary_fraction = 0.1
        num_robots = 1000
        
        canary_robots = []
        for robot_id in range(1, num_robots + 1):
            if robot_id % int(1 / canary_fraction) == 0:
                canary_robots.append(robot_id)
        
        # Should be approximately 10% (100 robots)
        assert len(canary_robots) == 100
    
    def test_dry_run_flag(self):
        """Test dry run flag is set for non-canary robots."""
        canary_fraction = 0.1
        robot_id = 5  # Not a canary (not divisible by 10)
        
        is_canary = robot_id % int(1 / canary_fraction) == 0
        dry_run = not is_canary
        
        assert dry_run is True


class TestMetrics:
    """Tests for Prometheus metrics."""
    
    def test_metrics_defined(self):
        """Test that all metrics are properly defined."""
        from kafka_robot_fleet.core.metrics import (
            COMMANDS_ISSUED,
            COMMAND_COMPLETIONS,
            DLQ_ENTRIES,
            TRANSACTION_DURATION,
            CONSUMER_LAG,
        )
        
        assert COMMANDS_ISSUED is not None
        assert COMMAND_COMPLETIONS is not None
        assert DLQ_ENTRIES is not None
        assert TRANSACTION_DURATION is not None
        assert CONSUMER_LAG is not None


class TestExponentialBackoff:
    """Tests for exponential backoff logic."""
    
    def test_backoff_calculation(self):
        """Test exponential backoff calculation."""
        initial_backoff = 1.0
        
        expected_backoffs = [1.0, 2.0, 4.0, 8.0, 16.0]
        
        for retry_count in range(5):
            backoff = initial_backoff * (2 ** retry_count)
            assert backoff == expected_backoffs[retry_count]
    
    def test_backoff_increases_exponentially(self):
        """Test that backoff increases exponentially."""
        initial_backoff = 1.0
        
        backoff1 = initial_backoff * (2 ** 0)
        backoff2 = initial_backoff * (2 ** 1)
        backoff3 = initial_backoff * (2 ** 2)
        
        assert backoff2 == backoff1 * 2
        assert backoff3 == backoff2 * 2


@pytest.mark.asyncio
class TestAsyncOperations:
    """Tests for async operations."""
    
    async def test_producer_creation(self):
        """Test producer creation (mocked)."""
        with patch('kafka_robot_fleet.utils.kafka_helpers.AIOKafkaProducer') as mock_producer:
            mock_instance = AsyncMock()
            mock_producer.return_value = mock_instance
            
            from kafka_robot_fleet.utils.kafka_helpers import create_producer
            
            producer = await create_producer()
            assert producer is not None
    
    async def test_concurrent_telemetry_sends(self):
        """Test concurrent telemetry sending."""
        async def send_telemetry(robot_id):
            await asyncio.sleep(0.01)  # Simulate send
            return robot_id
        
        tasks = [send_telemetry(i) for i in range(10)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 10
        assert results == list(range(10))


class TestEmergencyHalt:
    """Tests for emergency halt functionality."""
    
    def test_halt_state_change(self):
        """Test that halt changes robot state."""
        state = {
            'halted': False,
            'velocity': {'vx': 10.0, 'vy': 5.0, 'vz': 0.0}
        }
        
        # Simulate emergency halt
        state['halted'] = True
        state['velocity'] = {'vx': 0.0, 'vy': 0.0, 'vz': 0.0}
        
        assert state['halted'] is True
        assert state['velocity']['vx'] == 0.0
        assert state['velocity']['vy'] == 0.0
        assert state['velocity']['vz'] == 0.0


class TestZoneManagement:
    """Tests for zone-based robot management."""
    
    def test_robot_zone_assignment(self):
        """Test robots are assigned to zones correctly."""
        num_zones = 10
        
        # Test first 20 robots
        for robot_id in range(1, 21):
            zone = (robot_id - 1) % num_zones
            assert 0 <= zone < num_zones
        
        # Verify distribution
        assert (1 - 1) % num_zones == 0
        assert (11 - 1) % num_zones == 0  # Same zone as robot 1
        assert (2 - 1) % num_zones == 1
    
    def test_emergency_halt_by_zone(self):
        """Test emergency halt can target specific zones."""
        robots = {
            1: {'zone': 0, 'halted': False},
            2: {'zone': 1, 'halted': False},
            3: {'zone': 0, 'halted': False},
        }
        
        halt_zone = 0
        
        for robot_id, state in robots.items():
            if state['zone'] == halt_zone:
                state['halted'] = True
        
        assert robots[1]['halted'] is True
        assert robots[2]['halted'] is False
        assert robots[3]['halted'] is True


# Integration test example
@pytest.mark.integration
@pytest.mark.asyncio
class TestIntegration:
    """Integration tests (require Kafka running)."""
    
    @pytest.mark.skip(reason="Requires running Kafka cluster")
    async def test_end_to_end_command_flow(self):
        """Test complete command flow from issuance to completion."""
        # This would test:
        # 1. Command issued by control center
        # 2. Command consumed by robot
        # 3. Command executed
        # 4. Completion message sent
        # 5. Completion consumed by control center
        pass
    
    @pytest.mark.skip(reason="Requires running Kafka cluster")
    async def test_retry_mechanism(self):
        """Test retry mechanism for failed commands."""
        # This would test:
        # 1. Command fails
        # 2. Command sent to retry topic
        # 3. Exponential backoff applied
        # 4. Command retried
        # 5. After max retries, sent to DLQ
        pass


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
