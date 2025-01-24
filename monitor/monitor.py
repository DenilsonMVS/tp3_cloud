import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import redis
import json

# Redis server configuration
REDIS_HOST = '192.168.121.187'
REDIS_PORT = 6379
REDIS_DB = 0
KEY = '2021032030-proj3-output'

# Connect to Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

# Initialize the Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Resource Monitoring Dashboard"),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    ),
    html.Div(id='live-update-text'),
])

@app.callback(
    Output('live-update-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_metrics(n):
    value = redis_client.get(KEY)
    if value:
        data = json.loads(value)
        return [
            html.Div(f"Percent Network Egress: {data.get('percent-network-egress', 'N/A')}%"),
            html.Div(f"Percent Memory Caching: {data.get('percent-memory-caching', 'N/A')}%"),
        ]
    return "No data available."

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
    