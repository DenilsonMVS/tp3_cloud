import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import redis
import json
import time
import logging
from collections import deque

# Redis configuration
REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
MAIN_KEY = '2021032030-proj3-output'
CPU_PREFIX = 'avg-util-cpu1-60sec-'  # Prefix for CPU utilization keys

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Initialize the Dash app
app = dash.Dash(__name__)

# Deques to keep track of the last 50 points for each graph
outgoing_traffic_history = deque(maxlen=50)
memory_caching_history = deque(maxlen=50)
timestamps = deque(maxlen=50)  # Shared timestamps
cpu_utilization_history = {}  # Dictionary to track CPU utilization per key

# Layout of the Dash app
app.layout = html.Div([
    dcc.Graph(id='outgoing-traffic-graph'),
    dcc.Graph(id='memory-caching-graph'),
    dcc.Graph(id='cpu-utilization-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5 * 1000,  # Update every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    [Output('outgoing-traffic-graph', 'figure'),
     Output('memory-caching-graph', 'figure'),
     Output('cpu-utilization-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    global outgoing_traffic_history, memory_caching_history, timestamps, cpu_utilization_history

    metrics = {
        "outgoing_traffic_percentage": 0,
        "memory_caching_percentage": 0
    }

    # Fetch the latest data from Redis for the main key
    data = redis_client.get(MAIN_KEY)
    if data:
        metrics = json.loads(data)

    logging.critical(data)

    # Append new data to the history
    timestamps.append(time.strftime('%H:%M:%S'))  # Add current time as a string
    outgoing_traffic_history.append(metrics.get("outgoing_traffic_percentage", 0))
    memory_caching_history.append(metrics.get("memory_caching_percentage", 0))

    # Update CPU utilization metrics based on the prefix in the metrics dictionary
    for key, value in metrics.items():
        if key.startswith(CPU_PREFIX):
            if key not in cpu_utilization_history:
                # Initialize a deque for the new key
                cpu_utilization_history[key] = deque(maxlen=50)
            cpu_utilization_history[key].append(float(value))

    # Create figures for the graphs
    outgoing_traffic_fig = go.Figure(data=[
        go.Scatter(x=list(timestamps), y=list(outgoing_traffic_history), mode='lines+markers')
    ])
    outgoing_traffic_fig.update_layout(title='Outgoing Traffic Percentage', xaxis_title='Time', yaxis_title='Percentage')

    memory_caching_fig = go.Figure(data=[
        go.Scatter(x=list(timestamps), y=list(memory_caching_history), mode='lines+markers')
    ])
    memory_caching_fig.update_layout(title='Memory Caching Percentage', xaxis_title='Time', yaxis_title='Percentage')

    # Create the CPU utilization graph
    cpu_utilization_fig = go.Figure()
    for key, values in cpu_utilization_history.items():
        cpu_utilization_fig.add_trace(go.Scatter(
            x=list(timestamps),
            y=list(values),
            mode='lines+markers',
            name=key
        ))
    cpu_utilization_fig.update_layout(title='CPU Utilization (Last 60 Seconds)', xaxis_title='Time', yaxis_title='Utilization')

    return outgoing_traffic_fig, memory_caching_fig, cpu_utilization_fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
