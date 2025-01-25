from typing import Any, Dict
from collections import deque

DEQUE_LENGTH = 12


def handler(input: Dict[str, Any], context: object) -> Dict[str, Any]:
    cpu_utilization_history = {}

    # Retrieve the CPU utilization history from Redis
    if "history" not in context["env"]:
        context["env"]["history"] = cpu_utilization_history
    else:
        cpu_utilization_history = context["env"]["history"]

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
    context["env"]["history"] = cpu_utilization_history

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
