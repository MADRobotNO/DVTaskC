import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from geopy.geocoders import Nominatim

df = pd.read_csv("healthy_lifestyle_city_2021.csv")
df = df.replace('-', 0)
df['Cost of a bottle of water(City)'] = df['Cost of a bottle of water(City)'].str.replace('£', '')
df['Cost of a monthly gym membership(City)'] = df['Cost of a monthly gym membership(City)'].str.replace('£', '')
df['Obesity levels(Country)'] = df['Obesity levels(Country)'].str.replace('%', '')
df = df.astype({col: float for col in df.columns[1:]})

app = dash.Dash(__name__)

geolocator = Nominatim(user_agent="city_geocoder")


def geocode_city(city):
    location = geolocator.geocode(city)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None


df['Latitude'], df['Longitude'] = zip(*df['City'].apply(geocode_city))

map_center = {"lat": 54.5260, "lon": 15.2551}

color_palette = px.colors.qualitative.Light24

color_map = {
    city: color_palette[i % len(color_palette)]
    for i, city in enumerate(df['City'].unique())
}

map_fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', color='City', hover_name='City', title="Top 44 Cities",
                            mapbox_style="carto-positron", center=map_center, zoom=3, color_discrete_map=color_map)

df_sun = df.sort_values('Sunshine hours(City)')
sunshine_happines_fig = px.scatter(df_sun, x='Sunshine hours(City)', y='Happiness levels(Country)',
                                   color='City',
                                   color_discrete_map=color_map,
                                   hover_name='City',
                                   trendline="lowess",
                                   trendline_scope="overall",
                                   title="Happiness levels vs. Sunshine hours", ).update_xaxes(title='Sunshine hours', autotickangles=[90], showgrid=False).update_yaxes(title="Happiness levels",)

df_pol = df.sort_values('Pollution(Index score) (City)')
pollution_happiness_fig = px.scatter(df_pol, x='Pollution(Index score) (City)', y='Life expectancy(years) (Country)',
                                     color='City',
                                     hover_name='City',
                                     title="Life expectancy vs. Pollution",
                                     trendline="lowess",
                                     trendline_scope="overall",
                                     color_discrete_map=color_map).update_xaxes(title="Pollution (index score)", showgrid=False).update_yaxes(title="Life expectancy (years)")

df_obe = df.sort_values('Obesity levels(Country)')
obesity_outdoor_fig = px.bar(df_obe, y='Obesity levels(Country)', x='City',

                                 color_discrete_map=color_map,
                                 hover_name='City',
                                 title="Obesity levels in Cities (ordered by obesity level)").update_xaxes(autotickangles=[90], showgrid=False).update_yaxes(title="Obesity levels").update_layout(showlegend=False)


rank_life_fig = px.bar(df, x='Rank', y='Life expectancy(years) (Country)',

                                 color_discrete_map=color_map,
                                 hover_name='City',
                                 title="Rank vs Life expectancy (ordered by rank)").update_xaxes(showgrid=False).update_yaxes(title="Life expectancy (years)").update_layout(showlegend=False)

app.layout = html.Div([
    html.H1("Explore Healthy Lifestyle Cities Report 2021 dataset", style={'text-align': 'center', 'margin-bottom': '20px'}),
    html.Div([
        dcc.Graph(id='map-fig', figure=map_fig, style={'width': '98%', 'display': 'inline-block', 'margin-top': '5px'}),

        dcc.Graph(id='sunshine-life-fig', figure=sunshine_happines_fig, style={'width': '48%', 'display': 'inline-block'},
                  config={
                      'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                  }),

        dcc.Graph(id='pollution-happiness-fig', figure=pollution_happiness_fig,
                  style={'width': '48%', 'display': 'inline-block'},
                  config={
                      'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                  }),
        dcc.Graph(id='obesity-outdoor-fig', figure=obesity_outdoor_fig, style={'width': '48%', 'display': 'inline-block'},
                  config={
                      'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                  }),
        dcc.Graph(id='rank-life-fig', figure=rank_life_fig, style={'width': '48%', 'display': 'inline-block'},
                          config={
                              'modeBarButtonsToRemove': ['lasso2d', 'select2d']
                          })
    ], style={'margin-bottom': '20px', 'border': '1px solid grey'}),
    html.Footer(
        html.Small("By Martin Agnar Dahl - 2024")
        , style={"text-align": "center"})
])


@app.callback(
    [Output('sunshine-life-fig', 'figure'),
     Output('pollution-happiness-fig', 'figure'),
     Output('obesity-outdoor-fig', 'figure'),
     Output('rank-life-fig', 'figure')],
    [Input('map-fig', 'selectedData')]
)
def update_graphs(selected_map_data):
    ctx = dash.callback_context
    if not ctx.triggered:
        prop_id = None
    else:
        prop_id = ctx.triggered[0]['prop_id']

    filtered_df = df.copy()

    if prop_id == 'map-fig.selectedData':
        if selected_map_data and selected_map_data['points']:
            selected_cities = extract_selected_cities(selected_map_data)
            filtered_df = filter_df_by_selected_cities(filtered_df, selected_cities)

        filtered_df_sol = filtered_df.sort_values(by='Sunshine hours(City)')

        sunshine_life_fig_updated = (px.scatter(filtered_df_sol, x='Sunshine hours(City)', y='Happiness levels(Country)',
                                                color='City',
                                                hover_name='City',
                                                title="Happiness levels vs. Sunshine hours",
                                                trendline="lowess",
                                                trendline_scope="overall",
                                                color_discrete_map=color_map)
                                     .update_xaxes(autotickangles=[90], showgrid=False))

        filtered_df_pol = filtered_df.sort_values(by='Pollution(Index score) (City)')
        pollution_happiness_fig_updated = px.scatter(filtered_df_pol, x='Pollution(Index score) (City)',
                                                     y='Life expectancy(years) (Country)',
                                                     color='City',
                                                     hover_name='City',
                                                     title="Pollution vs. Life expectancy",
                                                     trendline="lowess",
                                                     trendline_scope="overall",
                                                     color_discrete_map=color_map).update_xaxes(autotickangles=[90],
                                                                                                showgrid=False)

        filtered_df_obe = filtered_df.sort_values(by='Obesity levels(Country)')
        obesity_outdoor_fig_updated = (px.bar(filtered_df_obe, y='Obesity levels(Country)', x='City',
                                              color_discrete_map=color_map,
                                              hover_name='City',
                                              title="Obesity levels in Cities (ordered by obesity level)").update_xaxes(
                                              autotickangles=[90],
                                              showgrid=False)
                                       .update_yaxes(title="Obesity levels").update_layout(showlegend=False))

        rank_life_fig_updated = (px.bar(filtered_df, x='Rank', y='Life expectancy(years) (Country)',
                                        color_discrete_map=color_map,
                                        hover_name='City',
                                        title="Rank vs Life expectancy (ordered by rank)")
                                 .update_xaxes(showgrid=False).update_yaxes(title="Life expectancy (years)")
                                 .update_layout(showlegend=False))

        return sunshine_life_fig_updated, pollution_happiness_fig_updated, obesity_outdoor_fig_updated, rank_life_fig_updated

    else:
        return sunshine_happines_fig, pollution_happiness_fig, obesity_outdoor_fig, rank_life_fig


def extract_selected_cities(selected_data):
    selected_cities = []
    if selected_data:
        if 'points' in selected_data:
            selected_cities.extend([point['hovertext'] for point in selected_data['points']])
        if 'lassoPoints' in selected_data:
            lasso_points = selected_data['lassoPoints']
            selected_cities.extend([point['hovertext'] for point in lasso_points])
    return selected_cities


def filter_df_by_selected_cities(df, selected_cities):
    if selected_cities:
        return df[df['City'].isin(selected_cities)]
    else:
        return df


if __name__ == '__main__':
    app.run_server()
