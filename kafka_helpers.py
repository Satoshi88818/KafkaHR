"""Kafka helper functions for topic creation, serialization, and telemetry generation."""

import math
import random
import logging
import numpy as np
from aiokafka import AIOKafkaProducer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import KafkaError
from confluent_kafka.schema_registry import SchemaRegistryClient
from confluent_kafka.schema_registry.avro import AvroSerializer, AvroDeserializer
from confluent_kafka.serialization import SerializationContext, MessageField

from kafka_robot_fleet.config import settings, SECURITY_PROTOCOL
from kafka_robot_fleet.core.schemas import (
    TELEMETRY_SCHEMA_STR,
    COMMAND_SCHEMA_STR,
    COMPLETION_SCHEMA_STR,
    EMERGENCY_HALT_SCHEMA_STR,
    IDEMPOTENCY_SCHEMA_STR,
    STATE_SCHEMA_STR,
)

logger = logging.getLogger(__name__)

# Schema Registry client
sr_client = SchemaRegistryClient({'url': settings.schema_registry_url})


def register_schema(subject: str, schema_str: str, compatibility: str = 'BACKWARD'):
    """
    Register an Avro schema with the Schema Registry.
    
    Args:
        subject: Schema subject name
        schema_str: Schema JSON string
        compatibility: Compatibility mode (BACKWARD, FORWARD, FULL, NONE)
    """
    try:
        schema = sr_client.parse_schema(schema_str, 'AVRO')
        sr_client.set_compatibility(subject, compatibility)
        sr_client.register_schema(subject, schema)
        logger.info(f"Schema registered: {subject}")
    except Exception as e:
        if '409' in str(e):
            logger.info(f"Schema already exists: {subject}")
        else:
            raise


def register_all_schemas():
    """Register all schemas for the application topics."""
    schema_mappings = [
        (settings.control_telemetry_topic, TELEMETRY_SCHEMA_STR),
        (settings.safety_telemetry_topic, TELEMETRY_SCHEMA_STR),
        (settings.commands_topic, COMMAND_SCHEMA_STR),
        (settings.retry_topic, COMMAND_SCHEMA_STR),
        (settings.completions_topic, COMPLETION_SCHEMA_STR),
        (settings.dlq_topic, COMMAND_SCHEMA_STR),
        (settings.emergency_halt_topic, EMERGENCY_HALT_SCHEMA_STR),
        (settings.idempotency_topic, IDEMPOTENCY_SCHEMA_STR),
        (settings.robot_state_topic, STATE_SCHEMA_STR),
    ]
    
    for topic, schema in schema_mappings:
        register_schema(f"{topic}-value", schema)


async def create_topics(num_robots: int):
    """
    Create all required Kafka topics with appropriate partitioning.
    
    Args:
        num_robots: Number of robots in the fleet (used for partition calculation)
    """
    admin = AIOKafkaAdminClient(
        bootstrap_servers=settings.bootstrap_servers,
        security_protocol=SECURITY_PROTOCOL,
        sasl_mechanism=settings.sasl_mechanism,
        sasl_plain_username=settings.sasl_username,
        sasl_plain_password=settings.sasl_password
    )
    await admin.start()
    
    try:
        # Calculate partition counts based on fleet size
        telemetry_partitions = max(16, math.ceil(num_robots / 100) * settings.partitions_per_100_robots)
        command_partitions = max(8, math.ceil(num_robots / 200) * settings.partitions_per_100_robots)
        
        topics = [
            NewTopic(settings.control_telemetry_topic, telemetry_partitions, 1),
            NewTopic(settings.safety_telemetry_topic, command_partitions, 1),
            NewTopic(settings.commands_topic, command_partitions, 1),
            NewTopic(settings.retry_topic, command_partitions, 1),
            NewTopic(settings.completions_topic, command_partitions, 1),
            NewTopic(settings.dlq_topic, 4, 1, config={
                'retention.ms': str(settings.dlq_retention_ms),
                'cleanup.policy': 'compact,delete',
            }),
            NewTopic(settings.emergency_halt_topic, 1, 1),
            NewTopic(settings.idempotency_topic, command_partitions, 1, config={
                'cleanup.policy': 'compact',
                'retention.ms': str(settings.idempotency_retention_ms)
            }),
            NewTopic(settings.robot_state_topic, command_partitions, 1, config={
                'cleanup.policy': 'compact'
            }),
        ]
        
        await admin.create_topics(topics)
        logger.info("Topics created successfully")
    except KafkaError as e:
        if 'TopicAlreadyExists' not in str(e):
            raise
        logger.info("Topics already exist")
    finally:
        await admin.stop()


def generate_telemetry(robot_id: int, state: dict, dt: float, now: float) -> dict:
    """
    Generate telemetry data for a robot based on its current state.
    
    Args:
        robot_id: Robot identifier
        state: Current robot state dictionary
        dt: Time delta since last update
        now: Current timestamp
    
    Returns:
        Telemetry data dictionary
    """
    last_position = state.get('position')
    last_velocity = state.get('velocity')
    last_temp = state.get('temp', random.uniform(-50, 50))

    # Initialize position and velocity if first time
    if last_position is None:
        position = {
            'x': random.uniform(-100, 100),
            'y': random.uniform(-100, 100),
            'z': random.uniform(0, 10)
        }
        velocity = {'vx': 0.0, 'vy': 0.0, 'vz': 0.0}
        temp = random.uniform(-50, 50)
    else:
        # Update position based on velocity (if not halted)
        if state.get('halted', False):
            position = last_position
            velocity = {'vx': 0.0, 'vy': 0.0, 'vz': 0.0}
        else:
            # Apply random acceleration
            accel = {
                'ax': random.uniform(-0.2, 0.2),
                'ay': random.uniform(-0.2, 0.2),
                'az': random.uniform(-0.08, 0.05)
            }
            velocity = {
                k: last_velocity[k] * 0.98 + accel['a' + k[1]] * dt
                for k in ['vx', 'vy', 'vz']
            }
            position = {
                k: last_position[k] + velocity['v' + k[1]] * dt
                for k in ['x', 'y', 'z']
            }
        
        # Update temperature
        temp_delta = random.uniform(-5, 5) * dt
        if now < state.get('cooling_until', 0):
            temp_delta -= 30 * dt  # Active cooling
        temp = last_temp + temp_delta
        temp = max(-150, min(200, temp))  # Clamp temperature

    # Determine status
    if state.get('halted', False):
        status = 'halted'
    elif now < state.get('cooling_until', 0):
        status = 'cooling'
    elif temp > 100:
        status = 'overheating'
    else:
        status = random.choice(['nominal', 'excavating', 'moving', 'dust_jam'])

    # Environmental radiation (Poisson distributed)
    radiation = np.random.poisson(5) + random.uniform(0, 5)

    # Update state
    state['position'] = position
    state['velocity'] = velocity
    state['temp'] = temp

    return {
        'robot_id': robot_id,
        'timestamp': now,
        'position': position,
        'velocity': velocity,
        'status': status,
        'payload': {
            'regolith_tons': random.uniform(0.5, 5) if 'excavating' in status else 0.0,
            'energy_level': random.randint(50, 100)
        },
        'environment': {'temperature': temp, 'radiation': radiation},
        'battery_voltage': random.uniform(11, 13),
        'zone': state.get('zone', 0)
    }


async def create_producer(transactional_id: str = None) -> AIOKafkaProducer:
    """
    Create and start a Kafka producer.
    
    Args:
        transactional_id: Optional transaction ID for exactly-once semantics
    
    Returns:
        Started AIOKafkaProducer instance
    """
    kwargs = {
        'bootstrap_servers': settings.bootstrap_servers,
        'security_protocol': SECURITY_PROTOCOL,
        'sasl_mechanism': settings.sasl_mechanism,
        'sasl_plain_username': settings.sasl_username,
        'sasl_plain_password': settings.sasl_password,
    }
    
    if transactional_id:
        kwargs['transactional_id'] = transactional_id
        kwargs['enable_idempotence'] = True
    
    producer = AIOKafkaProducer(**kwargs)
    await producer.start()
    
    if transactional_id:
        await producer.begin_transaction()
    
    return producer


def get_avro_serializer(schema_str: str, topic: str) -> AvroSerializer:
    """
    Get an Avro serializer for a given schema and topic.
    
    Args:
        schema_str: Avro schema JSON string
        topic: Topic name for serialization context
    
    Returns:
        AvroSerializer instance
    """
    return AvroSerializer(
        sr_client,
        schema_str,
        lambda obj, ctx: obj
    )


def get_avro_deserializer(schema_str: str, topic: str) -> AvroDeserializer:
    """
    Get an Avro deserializer for a given schema and topic.
    
    Args:
        schema_str: Avro schema JSON string
        topic: Topic name for deserialization context
    
    Returns:
        AvroDeserializer instance
    """
    return AvroDeserializer(
        sr_client,
        schema_str,
        lambda obj, ctx: obj
    )
