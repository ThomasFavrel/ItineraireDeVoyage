import dash
from dash import dcc
from dash import html


app = dash.Dash(__name__)

app.layout = html.Div(
    children=[
        html.H1('My Dash App'),
        dcc.Graph(
            id='my-graph',
            figure={
                'data': [
                    {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'Example'}
                ],
                'layout': {
                    'title': 'Bar Chart'
                }
            }
        )
    ]
)

if __name__ == '__main__':
    app.run_server(debug=True)
