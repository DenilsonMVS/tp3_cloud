import redis
import json
from typing import Any, Dict
from collections import deque

# Redis connection configuration
REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEY = 'denilsonsantos-history'
DEQUE_LENGTH = 12

# Initialize the Redis client
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

def get_cpu_utilization_history() -> Dict[str, deque]:
    """Retrieve the CPU utilization history from Redis."""
    history = redis_client.get(REDIS_KEY)
    if history:
        history_dict = json.loads(history)
        # Convert lists back to deque
        return {key: deque(values, maxlen=DEQUE_LENGTH) for key, values in history_dict.items()}
    return {}

def save_cpu_utilization_history(history: Dict[str, deque]) -> None:
    """Save the CPU utilization history to Redis."""
    # Convert deque objects to lists before storing in Redis
    history_dict = {key: list(values) for key, values in history.items()}
    redis_client.set(REDIS_KEY, json.dumps(history_dict))

def handler(input: Dict[str, Any], context: object) -> Dict[str, Any]:
    # Retrieve the CPU utilization history from Redis
    cpu_utilization_history = get_cpu_utilization_history()

    # Extract relevant metrics from the input
    bytes_sent = input.get('net_io_counters_eth0-bytes_sent', 0)
    bytes_recv = input.get('net_io_counters_eth0-bytes_recv', 0)
    virtual_memory_total = input.get('virtual_memory-total', 1)  # Avoid division by zero
    virtual_memory_buffers = input.get('virtual_memory-buffers', 0)
    virtual_memory_cached = input.get('virtual_memory-cached', 0)

    # Calculate the percentage of outgoing traffic bytes
    if bytes_sent + bytes_recv > 0:
        outgoing_traffic_percentage = (bytes_sent / (bytes_recv + bytes_sent)) * 100
    else:
        outgoing_traffic_percentage = 0

    # Calculate the percentage of memory caching content
    memory_caching_content = virtual_memory_buffers + virtual_memory_cached
    memory_caching_percentage = (memory_caching_content / virtual_memory_total) * 100

    # Initialize CPU utilization history if not already done
    cpu_ids = [key for key in input if key.startswith("cpu_percent-")]

    # Update CPU utilization history
    for key in cpu_ids:
        cpu_utilization = input.get(key, 0)
        if key not in cpu_utilization_history:
            cpu_utilization_history[key] = deque(maxlen=DEQUE_LENGTH)
        cpu_utilization_history[key].append(cpu_utilization)

    # Save the updated CPU utilization history to Redis
    save_cpu_utilization_history(cpu_utilization_history)

    # Calculate the average CPU utilization
    average_cpu_utilization = {
        f"avg-util-cpu1-60sec-{key}": sum(cpu_utilization_history[key]) / len(cpu_utilization_history[key]) if len(cpu_utilization_history[key]) > 0 else 0
        for key in cpu_ids
    }

    # Merge the dictionaries using dictionary unpacking
    return {
        "outgoing_traffic_percentage": outgoing_traffic_percentage,
        "memory_caching_percentage": memory_caching_percentage,
        **average_cpu_utilization  # Unpack the average_cpu_utilization dictionary
    }
