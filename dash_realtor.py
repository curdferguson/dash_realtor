from dash import Dash, dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

pd.read_csv()

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
    dcc.Dropdown(
        soql_trees['spc_common'].unique(),
        'Japanese maple',
        id='spc'
    ),
    dcc.Checklist(
        soql_trees['boroname'].unique(),
        ['Queens', 'Manhattan'],
        id='boro',
        inline=True
    )]),
    dcc.Graph(id='graphic')
])


@app.callback(
    Output('graphic', 'figure'),
    Input('spc', 'value'),
    Input('boro', 'value')
)

def update_figure(species, boro_choice):
    filtered_soql = soql_trees[(soql_trees['spc_common'] == species) & (soql_trees['boroname'].isin(boro_choice))]

    fig = px.bar(filtered_soql, x="steward", color="health",
                y="count_tree_id",
                title=f"Health of {species}",
                barmode='group',
                height=600
                ).update_xaxes(type = "category")

    fig.update_layout(transition_duration=500)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)