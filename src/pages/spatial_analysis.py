import sys

sys.path.append("..")
import os
import dash
import pickle
import pandas as pd
import pydeck as pdk


mapbox_token = os.environ.get("MAPBOX_ACCESS_TOKEN")

import matplotlib.cm as cmx
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, callback


dash.register_page(__name__, title='Spatial Peak Analysis', name='Spatial Peak Analysis')


#peak_expedition_by_year_season_df = pd.read_csv(os.path.join("src", "data", "dash", "peak_expedition_by_year_season_df.csv"))
peak_expedition_by_year_season_df = pd.read_csv(
    os.path.join("src", "data",  "peak_expedition_by_year_season_df.csv"))

primary_df = peak_expedition_by_year_season_df[['YEAR', 'LAT', 'LON', 'HEIGHTM', 'PEAKID', 'PKNAME', 'EXPEDITIONS_COUNT']].drop_duplicates()

lat_avg = primary_df['LAT'].unique().mean()
lon_avg = primary_df['LON'].unique().mean()

# with open(os.path.join("src", "data", "dash", "store_data_lists.pickle"), 'rb') as handle:
with open(os.path.join("src", "data",  "store_data_lists.pickle"), 'rb') as handle:
    lists_dict = pickle.load(handle)
    all_peaks_list = lists_dict['all_peaks_list']

load_dotenv()
mapbox_token = os.environ.get("MAPBOX_ACCESS_TOKEN")
my_mapbox_api_key =  {'mapbox': mapbox_token}

# https://deckgl.readthedocs.io/en/latest/gallery/column_layer.html
# https://github.com/groundhogday321/python-pydeck-examples/blob/main/python%20pydeck.ipynb
mountain_peaks = peak_expedition_by_year_season_df.copy()
mountain_peaks['scaled_elevation'] = mountain_peaks['HEIGHTM'] / 1_0
min_val = mountain_peaks['scaled_elevation'].min()
max_val = mountain_peaks['scaled_elevation'].max()
# print(f"Check scaled Elevation {mountain_peaks}")

# In PyDeck, the view_state object specifies the camera position and orientation for a 3D visualization.
# The pitch and bearing properties of the view_state object control the pitch (tilt) and bearing (rotation) of the camera, respectively.
# The pitch property specifies the angle, in degrees, between the camera's direction of view and the horizontal plane.
# A pitch of 0 degrees corresponds to a camera that is pointing straight ahead, while a pitch of 90 degrees corresponds to a camera that is pointing straight up.
# The bearing property specifies theangle, in degrees, between the camera 's direction of view and true north.
# A bearing of 0 degrees corresponds to a camera that is pointing directly north, while a bearing of 90 degrees corresponds to a camera that is pointing east.
# view (location, zoom level, etc.)
view = pdk.ViewState(latitude=lat_avg, longitude=lon_avg, zoom=6)
view.pitch = 80
view.bearing = 0  # Higher this number, the more east the camera is tilting

layout = html.Div(

    [
        html.Link(
            href= os.path.join('..', 'assets', 'mapbox-gl.css'),
            rel='stylesheet'
        ),
        dbc.Row([
            dbc.Col([
                html.P("Peak expedition count greater than", className="m-0"),
                dcc.Dropdown(id="num_expeditions_dropdown",
                             options=[
                                 {"label": f"{num_expeditions} Expeditions", "value": num_expeditions} for
                                 num_expeditions in
                                 [1, 10, 20, 30, 40, 50, 60, 70, 80]], value=1, clearable=False,
                             className="rounded shadow")

            ], width=4, className="w-4  ps-3 pe-3"),

            dbc.Col([
                html.P("Select time range for expedition:", className="m-0"),
                dcc.RangeSlider(1920, 2030, 10,
                                value=[1920, 2030],
                                marks={
                                    1920: '1920',
                                    1930: '1930',
                                    1940: '1940',
                                    1950: '1950',
                                    1960: '1960',
                                    1970: '1970',
                                    1980: '1980',
                                    1990: '1990',
                                    2000: '2000',
                                    2010: '2010',
                                    2020: '2020',
                                    2030: '2030'

                                },
                                id='year_slider',
                                className="rounded shadow"

                                ),
            ], width=4,
                className="w-4"),

        ]),
        dbc.Row([dbc.Col([html.P(
            ["Column Heights are Expedition Counts", html.Br(), "Color is based on Height of Mountain"],
            className="border rounded-pill"),],
            )]),
        dbc.Row([dbc.Col([html.Div([
            dcc.Loading(
                id="loading-1",
                children=[
                    html.Iframe(
                        id="spatial_iframe",
                        className="vh-100 vw-100",

                    )
                ],
                type="circle",
                fullscreen=True,
            )],
        ), ], width=12, className="rounded shadow rounded-top rounded-end rounded-start rounded-bottom  rounded-top")]),

    ]
)


@callback(
    dash.dependencies.Output("spatial_iframe", "src"),
    [Input("num_expeditions_dropdown", "value"), Input('year_slider', 'value')],
)
def show_iframe(num_expeditions, date_range):
    #print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
    full_file_path = f"src/assets/spatial_analysis_{num_expeditions}_{date_range[0]}_{date_range[1]}.html"
    url_to_return = f"spatial_analysis_{num_expeditions}_{date_range[0]}_{date_range[1]}.html"

    if os.path.exists(full_file_path):
        #print(f"File Exists = {full_file_path}")
        print("")
    else:
        mountain_peaks = primary_df[
            (primary_df['EXPEDITIONS_COUNT'] >= num_expeditions) & (primary_df['YEAR'] >= date_range[0])
            & (primary_df['YEAR'] <= date_range[1])].copy()

        mountain_peaks['scaled_elevation'] = mountain_peaks['HEIGHTM'] / 1_00

        mountain_peaks = mountain_peaks.groupby(['LAT', 'LON', 'HEIGHTM', 'PEAKID', 'PKNAME', 'scaled_elevation']
                                                ).agg(EXPEDITIONS_COUNT=('EXPEDITIONS_COUNT', 'sum')).reset_index()

        # create mapping from population to color #https: // www.einblick.ai / tools / pydeck - deckgl - in -python /
        color_choice = cm = plt.get_cmap('cool')
        cNorm = colors.Normalize(vmin=mountain_peaks["scaled_elevation"].min(),
                                 vmax=mountain_peaks["scaled_elevation"].max())
        scalarMap = cmx.ScalarMappable(norm=cNorm, cmap=color_choice)
        mountain_peaks["color"] = mountain_peaks.apply(lambda row: scalarMap.to_rgba(row["scaled_elevation"]), axis=1)

        # layer
        column_layer = pdk.Layer(
            'ColumnLayer',
            data=mountain_peaks,
            get_position=['LON', 'LAT'],
            get_elevation='EXPEDITIONS_COUNT',
            elevation_scale=500,
            radius=1000,  # thickness of the column cylinders
            get_fill_color="[color[0] * 255, color[1] * 255, color[2] * 255, color[3] * 255]",
            # [255, 150, 0],
            pickable=True,
            auto_highlight=True)

        # add tooltip
        tooltip = {
            "html": "<b>Expeditions: {EXPEDITIONS_COUNT}</b><br><b>Peak: {PEAKID}</b><br><b>Peak Name: {PKNAME}</b><br><b>Elevation: {HEIGHTM}</b>",
            "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial',
                      "z-index": "10000"},
        }

        # render map
        # with no map_style, map goes to default
        column_layer_map = pdk.Deck(layers=[column_layer],
                                    initial_view_state=view,
                                    api_keys=my_mapbox_api_key,
                                    map_provider="mapbox",
                                    map_style=pdk.map_styles.SATELLITE,
                                    tooltip=tooltip
                                    )

        # display and save map (to_html(), show())
        # print("File saved : {full_file_path}")
        # print(f"URL returned :{url_to_return}")

        column_layer_map.to_html(full_file_path)
        
    return dash.get_asset_url(url_to_return)
