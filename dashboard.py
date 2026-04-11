import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from collections import deque
import threading
import dash
from dash import dcc, html, ctx
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from generator import generate_api_traffic
from detector import AnomalyDetector
from reporter import generate_incident_report

MAX_POINTS    = 60
timestamps    = deque(maxlen=MAX_POINTS)
latencies     = deque(maxlen=MAX_POINTS)
req_per_sec   = deque(maxlen=MAX_POINTS)
error_rates   = deque(maxlen=MAX_POINTS)
anomaly_flags = deque(maxlen=MAX_POINTS)

last_report     = {"text": "", "visible": False}
anomaly_history = []

detector = AnomalyDetector()
detector.load_pretrained()

app = dash.Dash(__name__)

BG        = '#0d1117'
CARD      = '#161b22'
CARD2     = '#1c2128'
BORDER    = '#30363d'
BORDER2   = '#21262d'
STEEL     = '#58a6ff'
SLATE     = '#79c0ff'
COOLWHITE = '#cdd9e5'
GREEN     = '#3fb950'
RED       = '#f85149'
DIMWHITE  = '#e6edf3'
MUTED     = '#7d8590'


def build_fig(xs, ys, title, line_col, fill_col, y_title, dot_colors):
    return {
        'data': [go.Scatter(
            x=list(xs), y=list(ys),
            mode='lines+markers',
            line={'color': line_col, 'width': 2},
            marker={'color': list(dot_colors), 'size': 6},
            fill='tozeroy',
            fillcolor=fill_col,
        )],
        'layout': go.Layout(
            title={'text': title, 'font': {'color': MUTED, 'size': 11}, 'x': 0.01},
            height=185,
            margin={'t': 32, 'b': 28, 'l': 52, 'r': 16},
            plot_bgcolor=CARD,
            paper_bgcolor=CARD,
            font={'color': DIMWHITE, 'size': 10},
            xaxis={'gridcolor': BORDER2, 'color': MUTED, 'zerolinecolor': BORDER2, 'tickfont': {'size': 9}},
            yaxis={'title': y_title, 'gridcolor': BORDER2, 'color': MUTED, 'zerolinecolor': BORDER2, 'tickfont': {'size': 9}},
        )
    }


app.layout = html.Div(style={
    'background': BG,
    'fontFamily': '-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif',
    'height': '100vh', 'display': 'flex', 'flexDirection': 'column',
    'margin': '0', 'padding': '0', 'color': DIMWHITE
}, children=[

    # header
    html.Div(style={
        'background': CARD, 'borderBottom': f'1px solid {BORDER}',
        'padding': '10px 20px', 'display': 'flex',
        'justifyContent': 'space-between', 'alignItems': 'center'
    }, children=[
        html.Div(style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}, children=[
            html.Div(style={'width': '6px', 'height': '6px', 'borderRadius': '50%', 'background': GREEN}),
            html.Span("api-anomaly-detector", style={'fontSize': '14px', 'fontWeight': '600', 'color': STEEL}),
            html.Span("/", style={'color': MUTED, 'fontSize': '14px'}),
            html.Span("live-monitor", style={'fontSize': '14px', 'color': DIMWHITE}),
            html.Span("v1.0", style={
                'fontSize': '10px', 'color': MUTED, 'background': CARD2,
                'padding': '1px 8px', 'borderRadius': '20px',
                'border': f'1px solid {BORDER}', 'marginLeft': '4px'
            }),
        ]),
        html.Div(id='hdr-status', children="System healthy", style={
            'fontSize': '11px', 'color': GREEN, 'background': '#1a2e1a',
            'padding': '3px 12px', 'borderRadius': '20px',
            'border': '1px solid #2ea04355', 'fontWeight': '500'
        }),
    ]),

    # body
    html.Div(style={'display': 'flex', 'flex': '1', 'overflow': 'hidden'}, children=[

        # LEFT PANEL
        html.Div(style={
            'width': '260px', 'minWidth': '260px', 'background': CARD,
            'borderRight': f'1px solid {BORDER}', 'padding': '16px 14px',
            'display': 'flex', 'flexDirection': 'column', 'gap': '14px',
            'overflowY': 'auto'
        }, children=[

            # 3 vertical metric cards
            html.Div(style={'display': 'flex', 'flexDirection': 'column', 'gap': '6px'}, children=[

                html.Div(style={
                    'background': CARD2, 'border': f'1px solid {BORDER}',
                    'borderTop': f'2px solid {STEEL}',
                    'borderRadius': '6px', 'padding': '12px 14px', 'textAlign': 'center'
                }, children=[
                    html.Div("LATENCY", style={'fontSize': '9px', 'color': MUTED, 'letterSpacing': '1.5px', 'marginBottom': '6px'}),
                    html.Div(id='s-lat', children="--", style={'fontSize': '28px', 'fontWeight': '600', 'color': STEEL, 'lineHeight': '1'}),
                    html.Div("ms", style={'fontSize': '10px', 'color': MUTED, 'marginTop': '4px'}),
                ]),

                html.Div(style={
                    'background': CARD2, 'border': f'1px solid {BORDER}',
                    'borderTop': f'2px solid {SLATE}',
                    'borderRadius': '6px', 'padding': '12px 14px', 'textAlign': 'center'
                }, children=[
                    html.Div("REQ / SEC", style={'fontSize': '9px', 'color': MUTED, 'letterSpacing': '1.5px', 'marginBottom': '6px'}),
                    html.Div(id='s-rps', children="--", style={'fontSize': '28px', 'fontWeight': '600', 'color': SLATE, 'lineHeight': '1'}),
                    html.Div("rps", style={'fontSize': '10px', 'color': MUTED, 'marginTop': '4px'}),
                ]),

                html.Div(style={
                    'background': CARD2, 'border': f'1px solid {BORDER}',
                    'borderTop': f'2px solid {COOLWHITE}',
                    'borderRadius': '6px', 'padding': '12px 14px', 'textAlign': 'center'
                }, children=[
                    html.Div("ERROR RATE", style={'fontSize': '9px', 'color': MUTED, 'letterSpacing': '1.5px', 'marginBottom': '6px'}),
                    html.Div(id='s-err', children="--", style={'fontSize': '28px', 'fontWeight': '600', 'color': COOLWHITE, 'lineHeight': '1'}),
                    html.Div("%", style={'fontSize': '10px', 'color': MUTED, 'marginTop': '4px'}),
                ]),

            ]),

            # anomaly count
            html.Div(id='s-count', children="0 anomalies detected", style={
                'fontSize': '11px', 'color': MUTED, 'textAlign': 'center',
                'padding': '6px', 'borderRadius': '5px',
                'background': CARD2, 'border': f'1px solid {BORDER}'
            }),

            # inject button
            html.Button("INJECT ANOMALY", id='anomaly-btn', n_clicks=0, style={
                'width': '100%', 'padding': '9px', 'fontSize': '10px',
                'fontWeight': '600', 'cursor': 'pointer', 'borderRadius': '5px',
                'border': f'1px solid {BORDER}', 'background': CARD2,
                'color': DIMWHITE, 'letterSpacing': '1.5px'
            }),

            html.Div(style={'borderTop': f'1px solid {BORDER}'}),

            html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center'}, children=[
                html.Span("INCIDENT LOG", style={'fontSize': '9px', 'color': MUTED, 'letterSpacing': '2px', 'fontWeight': '600'}),
                html.Span(id='s-count-badge', children="0", style={
                    'fontSize': '10px', 'color': RED, 'background': '#2d1117',
                    'padding': '1px 7px', 'borderRadius': '10px', 'border': f'1px solid {RED}44'
                }),
            ]),

            html.Div(id='reports', style={
                'flex': '1', 'overflowY': 'auto',
                'display': 'flex', 'flexDirection': 'column', 'gap': '6px'
            }, children=[
                html.Div("No incidents recorded.", style={
                    'fontSize': '11px', 'color': MUTED,
                    'fontStyle': 'italic', 'textAlign': 'center', 'padding': '16px 0'
                })
            ]),
        ]),

        # RIGHT PANEL — 3 coloured graphs
        html.Div(style={
            'flex': '1', 'display': 'flex', 'flexDirection': 'column',
            'padding': '10px', 'gap': '6px', 'background': BG, 'overflowY': 'auto'
        }, children=[
            dcc.Graph(id='g-lat', config={'displayModeBar': False}, style={'flex': '1'}),
            dcc.Graph(id='g-rps', config={'displayModeBar': False}, style={'flex': '1'}),
            dcc.Graph(id='g-err', config={'displayModeBar': False}, style={'flex': '1'}),
        ]),
    ]),

    dcc.Interval(id='tick', interval=2000, n_intervals=0),
])


def gen_report_bg(point):
    try:
        r = generate_incident_report(point)
        last_report['text'] = r
        last_report['visible'] = True
        anomaly_history.append({'time': point['timestamp'], 'report': r})
    except Exception as e:
        last_report['text'] = f"Failed: {e}"
        last_report['visible'] = True


@app.callback(
    [Output('g-lat',         'figure'),
     Output('g-rps',         'figure'),
     Output('g-err',         'figure'),
     Output('hdr-status',    'children'),
     Output('hdr-status',    'style'),
     Output('s-lat',         'children'),
     Output('s-rps',         'children'),
     Output('s-err',         'children'),
     Output('s-count',       'children'),
     Output('s-count',       'style'),
     Output('s-count-badge', 'children'),
     Output('reports',       'children')],
    [Input('tick',           'n_intervals'),
     Input('anomaly-btn',    'n_clicks')]
)
def update(n, n_clicks):
    inject = ctx.triggered_id == 'anomaly-btn'

    point = generate_api_traffic(inject_anomaly=inject)
    detector.add_datapoint(point)
    detector.train()
    is_anomaly, confidence = detector.predict(point)

    timestamps.append(point['timestamp'])
    latencies.append(point['latency_ms'])
    req_per_sec.append(point['requests_per_sec'])
    error_rates.append(point['error_rate'] * 100)
    anomaly_flags.append(is_anomaly)

    dots_steel    = [RED if a else STEEL    for a in anomaly_flags]
    dots_slate    = [RED if a else SLATE    for a in anomaly_flags]
    dots_coolwhite= [RED if a else COOLWHITE for a in anomaly_flags]

    if inject or is_anomaly:
        hdr = f"Anomaly detected  —  {confidence}% confidence"
        hstyle = {
            'fontSize': '11px', 'color': RED, 'fontWeight': '600',
            'background': '#2d1117', 'padding': '3px 12px',
            'borderRadius': '20px', 'border': f'1px solid {RED}55'
        }
    else:
        hdr = "System healthy"
        hstyle = {
            'fontSize': '11px', 'color': GREEN, 'fontWeight': '500',
            'background': '#1a2e1a', 'padding': '3px 12px',
            'borderRadius': '20px', 'border': '1px solid #2ea04355'
        }

    if inject:
        point['confidence'] = confidence
        t = threading.Thread(target=gen_report_bg, args=(point,))
        t.daemon = True
        t.start()

    total = len(anomaly_history)
    count_txt = f"{total} anomal{'y' if total == 1 else 'ies'} detected"
    count_style = {
        'fontSize': '11px', 'textAlign': 'center', 'padding': '6px',
        'borderRadius': '5px',
        'color': RED if total > 0 else MUTED,
        'background': '#2d1117' if total > 0 else CARD2,
        'border': f'1px solid {RED}44' if total > 0 else f'1px solid {BORDER}',
        'fontWeight': '500' if total > 0 else '400'
    }

    if not anomaly_history:
        reports = [html.Div("No incidents recorded.", style={
            'fontSize': '11px', 'color': MUTED,
            'fontStyle': 'italic', 'textAlign': 'center', 'padding': '16px 0'
        })]
    else:
        reports = []
        for i, h in enumerate(reversed(anomaly_history[-6:])):
            latest = i == 0
            reports.append(html.Div(style={
                'background': '#1a0d0f' if latest else CARD2,
                'border': f'1px solid {RED}66' if latest else f'1px solid {BORDER}',
                'borderLeft': f'2px solid {RED}' if latest else f'2px solid {BORDER}',
                'borderRadius': '5px', 'padding': '8px 10px',
            }, children=[
                html.Div(style={
                    'display': 'flex', 'justifyContent': 'space-between',
                    'marginBottom': '5px', 'alignItems': 'center'
                }, children=[
                    html.Span("INCIDENT", style={
                        'fontSize': '8px', 'color': RED if latest else MUTED,
                        'fontWeight': '700', 'letterSpacing': '1.5px'
                    }),
                    html.Span(h['time'], style={
                        'fontSize': '9px', 'color': MUTED, 'fontFamily': 'monospace'
                    }),
                ]),
                html.P(h['report'], style={
                    'fontSize': '10px', 'lineHeight': '1.6', 'margin': '0',
                    'color': DIMWHITE if latest else MUTED
                })
            ]))

    return (
        build_fig(timestamps, latencies,   'Latency (ms)',   STEEL,     'rgba(88,166,255,0.06)',  'ms',    dots_steel),
        build_fig(timestamps, req_per_sec, 'Requests / sec', SLATE,     'rgba(121,192,255,0.06)', 'req/s', dots_slate),
        build_fig(timestamps, error_rates, 'Error rate (%)', COOLWHITE, 'rgba(205,217,229,0.05)', '%',     dots_coolwhite),
        hdr, hstyle,
        str(point['latency_ms']),
        str(point['requests_per_sec']),
        str(round(point['error_rate'] * 100, 1)),
        count_txt, count_style,
        str(total),
        reports,
    )


if __name__ == '__main__':
    app.run(debug=True)

