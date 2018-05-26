import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go

app = dash.Dash(__name__)
server = app.server

df = pd.read_csv('player_dataset.csv', index_col=0)
df = df[df.Season != 'Career']
df['year'] = df.Season.apply(lambda x: int(x[:4]) + 1)
df['conference'] = df.conference.replace('pac-12', 'pac-10')
available_seasons = sorted(df.year.unique())
cols = ['2P', '2PA', '3P', '3PA', 'AST', 'BLK', 'DRB', 
                'FG', 'FGA', 'FT', 'FTA', 'G', 'GS', 'MP', 'ORB', 
                'PF', 'PTS', 'STL', 'TOV', 'TRB']


app.layout = html.Div([
    html.H1(children='NBA Production by NCAA Conference', style={'text-align': 'center'}),
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='statistic',
                options=[{'label':col, 'value':col} for col in cols],
                value='PTS'
            )
        ],
        style={'width': '25%', 'display': 'inline-block'}),

    ]),

    dcc.Graph(id='conference-graphic'),

    dcc.RangeSlider(
                id='years',
                marks={season: season for season in available_seasons if season % 5 == 0},
                min=df.year.min(),
                max=df.year.max(),
                value=[2000, 2018]
    )
], style={'width': '90%', 'margin-left': '5%'})


@app.callback(
    dash.dependencies.Output('conference-graphic', 'figure'),
    [dash.dependencies.Input('years', 'value'),
    dash.dependencies.Input('statistic', 'value')
    ])
def update_graph(years, statistic):
    dff = df[(df.year >= years[0]) & (df.year <= years[1])]
    plot_data = dff.groupby(['year', 'conference'])[statistic].sum()
    conferences = dff[dff.year==years[1]].groupby('conference').sum().sort_values(statistic, ascending=False).index.tolist()

    return {
        'data': [go.Scatter(
            x=plot_data.loc[:, conference].index,
            y=list(plot_data.loc[:, conference]),
            text=conference,
            name='{}. {}'.format(conferences.index(conference) + 1, conference),
            mode='lines',
        ) for conference in conferences],
        'layout': go.Layout(
            xaxis={'title': 'Year'},
            yaxis={'title': statistic},
            margin={'l': 40, 'b': 40, 't': 10, 'r': 10}
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)


