import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import redis
import json
import time

# Redis configuration
REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
KEY = '2021032030-proj3-output'

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Initialize the Dash app
app = dash.Dash(__name__)

# Layout of the Dash app
app.layout = html.Div([
    dcc.Graph(id='outgoing-traffic-graph'),
    dcc.Graph(id='memory-caching-graph'),
    dcc.Graph(id='cpu-utilization-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # Update every 5 seconds
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
    # Fetch the latest data from Redis
    data = redis_client.get(KEY)
    if data:
        metrics = json.loads(data)
    else:
        metrics = {
            "outgoing_traffic_percentage": 0,
            "memory_caching_percentage": 0,
            # Assuming some default structure for CPU utilization
            "avg-util-cpu1-60sec-cpu0": 0,
            "avg-util-cpu1-60sec-cpu1": 0,
        }

    # Create figures for each graph
    outgoing_traffic_fig = go.Figure(data=[
        go.Scatter(x=[time.time()], y=[metrics["outgoing_traffic_percentage"]], mode='lines+markers')
    ])
    outgoing_traffic_fig.update_layout(title='Outgoing Traffic Percentage')

    memory_caching_fig = go.Figure(data=[
        go.Scatter(x=[time.time()], y=[metrics["memory_caching_percentage"]], mode='lines+markers')
    ])
    memory_caching_fig.update_layout(title='Memory Caching Percentage')

    cpu_utilization_fig = go.Figure()
    for key, value in metrics.items():
        if key.startswith("avg-util-cpu1-60sec-"):
            cpu_utilization_fig.add_trace(go.Scatter(x=[time.time()], y=[value], mode='lines+markers', name=key))
    cpu_utilization_fig.update_layout(title='Average CPU Utilization')

    return outgoing_traffic_fig, memory_caching_fig, cpu_utilization_fig

# Run the Dash app
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)