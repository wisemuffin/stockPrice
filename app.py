# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import plotly.plotly as py
import plotly.graph_objs as go

import pandas as pd
import numpy as np
from datetime import datetime
import pandas_datareader.data as web

# test imports
import json

external_css = [
    # dash stylesheet
    'https://codepen.io/chriddyp/pen/bWLwgP.css',
    'https://maxcdn.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css',
    'https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css'
]


# Parameters
START = datetime(2016, 12, 1)
END = datetime(2017, 7, 1)
DATASOURCE = 'yahoo'
stocksymbol = "aapl"

df = web.DataReader(stocksymbol, DATASOURCE, START, END)

columnNames = ['High', 'Low']

'''
Build the App
'''

app = dash.Dash()
server = app.server

# used when assigning callbacks to components that are generated by other callbacks (and therefore not in the initial layout), then you can suppress this exception by setting
app.config['suppress_callback_exceptions'] = True


app.layout = html.Div(children=[
    html.Div([
        html.H1(children='Stock Analysis', style={'display': 'inline-block'}),
    ],
        style={'display': 'inline-block'}
    ),
    dcc.Dropdown(
        id='stocksymbol',
        options=[
            "aapl", "nflx"
        ],
        value="aapl"  # dimension_options[0],
    ),
    dcc.Graph(id='Stock_line_chart')
])


@app.callback(
    Output(component_id='Stock_line_chart', component_property='figure'),
    [Input(component_id='stocksymbol', component_property='value')]
)
def Stock_line_chart(date_filter):
    data = []

    for col in columnNames:
        data.append(
            go.Scatter(
                x=df.index,
                y=df[col],
                name=col,
            )
        )

    for col in columnNames:
        data.append(
            go.Scatter(
                x=df.index,
                y=[df[col].mean()]*len(df.index),
                name=col+'_avg',
                line=dict(dash='dash')
            )
        )

    data.append(
        go.Bar(
            x=df.index,
            y=df['Volume'],
            name='Volume',
            yaxis='y2'
        )
    )

    # Add annotations
    # set up interactivty on dash

    high_annotations = [dict(x=df.High.idxmax(),
                             y=df.High.max(),
                             xref='x', yref='y',
                             text='High Max:<br>'+str('{0:.2f}'.format(df.High.max())),
                             ax=0, ay=-40)]
    low_annotations = [dict(x=df.High.idxmin(),
                            y=df.Low.min(),
                            xref='x', yref='y',
                            text='Low Min:<br>'+str('{0:.2f}'.format(df.Low.min())),
                            ax=0, ay=40)]

    updatemenus = list([
        dict(type="buttons",
             active=-1,
             buttons=list([
                 dict(label='High',
                      method='update',
                      args=[{'visible': [True, False, True, False, True]},
                            {'title': stocksymbol+' High',
                             'annotations': high_annotations}]),
                 dict(label='Low',
                      method='update',
                      args=[{'visible': [False, True, False, True, True]},
                            {'title': stocksymbol+' Low',
                             'annotations': low_annotations}]),
                 dict(label='Both',
                      method='update',
                      args=[{'visible': [True, True, True, True, True]},
                            {'title': stocksymbol,
                             'annotations': high_annotations+low_annotations}]),
             ]),
             )
    ])

    layout = go.Layout(
        title=stocksymbol,
        showlegend=False,
        updatemenus=updatemenus,
        yaxis=dict(
            title='Stock Price $\'s'
        ),
        yaxis2=dict(
            title='Volume',
            titlefont=dict(
                color='rgb(148, 103, 189)'
            ),
            tickfont=dict(
                color='rgb(148, 103, 189)'
            ),
            overlaying='y',
            side='right'
        )
    )
    return go.Figure(data=data, layout=layout)


# Choose the CSS styly you like
for css in external_css:
    app.css.append_css({'external_url': css})

if __name__ == '__main__':
    app.run_server(debug=True)
