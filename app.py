from dash import Dash, dcc, html, Input, Output, ctx
import plotly.graph_objects as go
import pandas as pd
from urllib.request import urlopen
import json

core = pd.read_csv('https://raw.githubusercontent.com/curdferguson/dash_realtor/main/data/rdc_core.csv')
state_files = pd.read_csv('data/state_files.csv').set_index('State')

core['zip_code'] = [str(i) for i in core['zip_code']]
core.loc[core['zip_code'].str.len() == 3, 'zip_code'] = ['00' + i for i in core.loc[core['zip_code'].str.len() == 3, 'zip_code']]
core.loc[core['zip_code'].str.len() == 4, 'zip_code'] = ['0' + i for i in core.loc[core['zip_code'].str.len() == 4, 'zip_code']]

lolite = dict(color='#B5B6B7', width=2)
hilite = dict(color='#EB5AEB', width=5)

opts_label=['Median Listing Price', 'Median Listing Price per Sq. Foot', 'Active Listing Count', 'Median Days on Market']
opts_value=['median_listing_price', 'median_listing_price_per_square_foot', 'active_listing_count', 'median_days_on_market']
opts_dict = {opts_value[i]: opts_label[i] for i in range(len(opts_label))}


app = Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.Div([
                dcc.Dropdown(
                    core['MSA'].unique(),
                    value='New York-Northern New Jersey-Long Island, NY-NJ-PA',
                    id='msa_dropdown'
                )
            ], style = {
                'width':'39%', 
                'display':'inline-block'
                }
            ), 
        html.Div(style = {
                'width':'9%', 
                'display':'inline-block'
                }
            ),
        html.Div([
                dcc.Dropdown(
                    options=opts_dict,
                    value='median_listing_price_per_square_foot',
                    id='metric_dropdown'
                )
            ], style = {
                'width':'29%', 
                'float':'center', 
                'display':'inline-block'
                }
            )#        ),
        #html.Div([
        #        html.Button(
        #            'Reset',
        #            id='update_button'
        #        )
        #    ], style = {
        #        'width':'19%', 
        #        'float':'right'
        #        }
        #    )
    ]),
    html.Div([
            dcc.Graph(id='msa_graphic')
    ]
    , style = {
                'width':'50%',
                'display':'inline-block'
                }),
    
    html.Div([
        dcc.Loading(
        id='loading',
        children=[
            dcc.Graph(id='zip_graphic')
        ])
    ], style = {
                'width':'50%', 
                'float':'right',
                'display':'inline-block'
                })
])

#@app.callback(
#    Output('zip_dropdown', 'options'),
#    Input('msa_dropdown', 'value'),
#    prevent_initial_call=True)
#def set_zipcode_options(selected_msa):
#    return [zip for zip in core[core['MSA'] == selected_msa]['zip_code'].unique()]
#
#@app.callback(
#    Output('zip_dropdown', 'value'),
#    Input('zip_dropdown', 'options'))
#def set_zipcode_value(option):
#    return option

@app.callback(
    Output('msa_graphic', 'figure'),
    [Input('msa_dropdown', 'value'),
    Input('metric_dropdown', 'value')],
    prevent_initial_call=False)

def msa_fig(selected_msa, selected_metric):
    core_grouped = core.groupby(['MSA', 'year_month'], )[[selected_metric]].agg('median').reset_index()
    df = core_grouped

    fig = go.Figure(layout_height=600)
    
    for msa in df['MSA'].unique():
        if msa != selected_msa:
            fig.add_trace(go.Scatter(
                x=df['year_month'], 
                y=df[df['MSA'] == msa][selected_metric],
                name=msa, 
                text=msa,
                hovertemplate=f'<b>{msa}</b><br>' + 
                    '%{x}<br>$%{y}<br>' +
                    '<extra></extra>',  
                mode='lines', 
                line=lolite,
                ))

    fig.add_trace(go.Scatter(
        x=df['year_month'], 
        y=df[df['MSA'] == selected_msa][selected_metric], 
        name=selected_msa,
        text=selected_msa, 
        hovertemplate=f'<b>{selected_msa}</b><br>' + 
        '%{x}<br>$%{y}<br>' +
        '<extra></extra>',  
        mode='lines', 
        line=hilite, 
        legendrank=1))

    fig.update_xaxes(type='category')
    fig.update_xaxes(categoryorder='category ascending')
    fig.update_xaxes(ticklabelstep=3)

    fig.update_layout(
        title=f"<b>{opts_dict[selected_metric]} by MSA</b>",
        xaxis_title="Year - Month",
        yaxis_title=f"{opts_dict[selected_metric]}",
        showlegend=False
        #font=dict(
        #    family="Courier New, monospace",
        #    size=18,
        #    color="RebeccaPurple"
        #)
    )
    return fig

@app.callback(
    Output('zip_graphic', 'figure'),
    [Input('msa_dropdown', 'value'),
    Input('metric_dropdown', 'value')],
    prevent_initial_call=False)

def zip_fig(selected_msa, selected_metric):    
    df = core[core['MSA'] == selected_msa]

    states = []
    for i in df['State'].unique():
        states.append(i)

    selected_states = pd.DataFrame(states)
    selected_states = selected_states.set_index(0, drop=True).join(state_files, how='left')

    state_zips = []
    for state in selected_states['state_json']:
        with urlopen(f'https://raw.githubusercontent.com/OpenDataDE/State-zip-code-GeoJSON/master/{state}') as response:
            state_zips.append(json.load(response))

    fig = go.Figure(layout_height=600)

    coords = pd.DataFrame({'lat': [], 'lon': []})

    for i in state_zips:
        fig.add_trace(go.Choroplethmapbox(
                        geojson=i,
                        locations=df['zip_code'], 
                        z=df[selected_metric],
                        featureidkey='properties.ZCTA5CE10',
                        colorscale = 'Reds',
                        zauto=False,
                        zmax=(df[selected_metric].quantile(0.80)),
                        zmin=(df[selected_metric].quantile(0.20)),
                        marker_opacity=0.5, 
                        text=df['zip_code'],
                        hovertemplate=f'{selected_msa}<br>' + 
                        'Zip Code: %{text}<br>' +
                        f'{opts_dict[selected_metric]}: ' + '$%{z}<br>' 
                        +'<extra></extra>'))

        lats = [i['features'][j]['properties']['INTPTLAT10'] for j in range(1, len(i['features']))]
        lons = [i['features'][j]['properties']['INTPTLON10'] for j in range(1, len(i['features']))]

        latlon = pd.DataFrame({'lat': lats, 'lon': lons})
        latlon['lat'] = latlon['lat'].apply(float)
        latlon['lon'] = latlon['lon'].apply(float)

        coords = pd.concat([coords, latlon], axis=0)

    coords = coords[(coords['lat'].isnull() == False) & (coords['lon'].isnull() == False)]
    coords_lat = coords['lat'].mean()
    coords_lon = coords['lon'].mean()

    print(coords.head(10))

    fig.update_layout(
        mapbox_style="open-street-map", mapbox_zoom=6,
        mapbox_center={"lat": coords_lat, "lon": coords_lon},
        title=f"<b>{opts_dict[selected_metric]} by Zip Code</b><br>" + selected_msa
        )
        
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
