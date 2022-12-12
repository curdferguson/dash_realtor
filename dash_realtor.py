from dash import Dash, dcc, html, Input, Output
import plotly.graph_objects as go
import pandas as pd
hotness = pd.read_csv('data/rdchotness.csv')

app = Dash(__name__)

app.layout = html.Div([
    html.Div([
    dcc.Dropdown(
        hotness['MSA'].unique(),
        'Dayton, OH',
        id='selected_msa'
    ),
    dcc.Dropdown(
        hotness['zip_code'].unique(),
        '45459',
        id='selected_zip'
    )]),
    #dcc.Checklist(
    #    soql_trees['boroname'].unique(),
    #    ['Queens', 'Manhattan'],
    #    id='boro',
    #    inline=True
    #)]),
    dcc.Graph(id='graphic')
])


@app.callback(
    Output('graphic', 'figure'),
    Input('selected_msa', 'value'),
    Input('selected_zip', 'value')
)



def update_figure(selected_msa, selected_zip):
    hotness_grouped = hotness[hotness['MSA'] == selected_msa].groupby(['zip_code', 'year_month'], )[['median_listing_price']].agg('max').reset_index()

    hotness_grouped['zip_code'] = [str(i) for i in hotness_grouped['zip_code']]
    hotness_grouped.loc[hotness_grouped['zip_code'].str.len() == 3, 'zip_code'] = ['00' + i for i in hotness_grouped.loc[hotness_grouped['zip_code'].str.len() == 3, 'zip_code']]
    hotness_grouped.loc[hotness_grouped['zip_code'].str.len() == 4, 'zip_code'] = ['0' + i for i in hotness_grouped.loc[hotness_grouped['zip_code'].str.len() == 4, 'zip_code']]

    fig = go.Figure()

    for zip in hotness_grouped[hotness_grouped['zip_code'] != selected_zip]['zip_code'].unique():
        fig.add_trace(go.Scatter(x=hotness_grouped['year_month'], y=hotness_grouped[hotness_grouped['zip_code'] == zip]['median_listing_price'], name=zip, mode='lines',
                            line=dict(color='#B5B6B7', width=2)))

    fig.add_trace(go.Scatter(x=hotness_grouped['year_month'], y=hotness_grouped[hotness_grouped['zip_code'] == selected_zip]['median_listing_price'], name=selected_zip, mode='lines',
                            line=dict(color='#EB5AEB', width=5)))
                        
    fig.update_xaxes(type='category')
    fig.update_xaxes(categoryorder='category ascending')

    fig.update_layout(
        title=f"Median Real Estate Listing Price by Zip Code, {selected_msa}",
        xaxis_title="Year - Month",
        yaxis_title="Median Listing Price",
        legend_title="Zip Code",
        #font=dict(
        #    family="Courier New, monospace",
        #    size=18,
        #    color="RebeccaPurple"
        #)
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=False)


