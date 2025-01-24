
from typing import Any, Dict

def handler(input: Dict[str, Any], context: object) -> Dict[str, Any]:
    # Extract relevant data from the input
    cpu_count = sum(1 for key in input if key.startswith("cpu_percent-"))
    cpu_usages = [input[f"cpu_percent-{i}"] for i in range(cpu_count)]
    
    # Calculate percentage of outgoing traffic bytes
    bytes_sent = input.get("net_io_counters_eth0-bytes_sent1", 0)
    bytes_recv = input.get("net_io_counters_eth0-bytes_recv1", 0)
    total_bytes = bytes_sent + bytes_recv
    percent_network_egress = (bytes_sent / total_bytes * 100) if total_bytes > 0 else 0

    # Calculate percentage of memory caching content
    cached_memory = input.get("virtual_memory-cached", 0)
    buffer_memory = input.get("virtual_memory-buffers", 0)
    total_memory = input.get("virtual_memory-total", 1)  # Avoid division by zero
    percent_memory_caching = ((cached_memory + buffer_memory) / total_memory * 100)

    # Initialize moving averages in env if not already present
    if 'cpu_moving_averages' not in context.env:
        context.env['cpu_moving_averages'] = [0.0] * cpu_count
        context.env['cpu_samples'] = [0] * cpu_count

    # Update moving averages
    for i in range(cpu_count):
        # Update the moving average for each CPU
        context.env['cpu_samples'][i] += 1
        context.env['cpu_moving_averages'][i] += (cpu_usages[i] - context.env['cpu_moving_averages'][i]) / context.env['cpu_samples'][i]

    # Prepare the output dictionary
    output = {
        "percent-network-egress": percent_network_egress,
        "percent-memory-caching": percent_memory_caching
    }

    # Add moving averages to the output
    for i in range(cpu_count):
        output[f"avg-util-cpu{i}-60sec"] = context.env['cpu_moving_averages'][i]

    return output