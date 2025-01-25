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
KEY = '2021032030-proj3-output'

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Initialize the Dash app
app = dash.Dash(__name__)

# Deques to keep track of the last 50 points for each graph
outgoing_traffic_history = deque(maxlen=50)
memory_caching_history = deque(maxlen=50)
timestamps = deque(maxlen=50)  # Shared timestamps

# Layout of the Dash app
app.layout = html.Div([
    dcc.Graph(id='outgoing-traffic-graph'),
    dcc.Graph(id='memory-caching-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
        n_intervals=0
    )
])

@app.callback(
    [Output('outgoing-traffic-graph', 'figure'),
     Output('memory-caching-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    global outgoing_traffic_history, memory_caching_history, timestamps

    metrics = {
        "outgoing_traffic_percentage": 0,
        "memory_caching_percentage": 0
    }

    # Fetch the latest data from Redis
    data = redis_client.get(KEY)
    if data:
        metrics = json.loads(data)

    logging.critical(data)

    # Append new data to the history
    timestamps.append(time.strftime('%H:%M:%S'))  # Add current time as a string
    outgoing_traffic_history.append(metrics["outgoing_traffic_percentage"])
    memory_caching_history.append(metrics["memory_caching_percentage"])

    # Create figures for each graph
    outgoing_traffic_fig = go.Figure(data=[
        go.Scatter(x=list(timestamps), y=list(outgoing_traffic_history), mode='lines+markers')
    ])
    outgoing_traffic_fig.update_layout(title='Outgoing Traffic Percentage', xaxis_title='Time', yaxis_title='Percentage')

    memory_caching_fig = go.Figure(data=[
        go.Scatter(x=list(timestamps), y=list(memory_caching_history), mode='lines+markers')
    ])
    memory_caching_fig.update_layout(title='Memory Caching Percentage', xaxis_title='Time', yaxis_title='Percentage')

    return outgoing_traffic_fig, memory_caching_fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
