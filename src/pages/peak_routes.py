import sys

sys.path.append("..")

import os
import dash
import pandas as pd
import pickle
import numpy as np
import dash_daq as daq
import plotly.express as px

from color_theme.color_dicts import COLOR_CHOICE_DICT, TIME_SERIES_COLOR_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback

# Place this in the home page
import plotly.graph_objects as go

fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Peak Routes Analysis', name='Peak Routes Analysis')

# print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
#peak_routes_df =  pd.read_csv( os.path.join('src', 'data', 'dash', 'peak_routes_df.csv' ))
peak_routes_df = pd.read_csv(os.path.join('src', 'data',  'peak_routes_df.csv'))

# Store the list of countries in a small pickle file
#with open(os.path.join("src", "data", "dash", "store_data_lists.pickle"), 'rb') as handle:
with open(os.path.join("src", "data",  "store_data_lists.pickle"), 'rb') as handle:
    lists_dict = pickle.load(handle)
    all_peaks_list = lists_dict['all_peaks_list']


layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([
                        dbc.Row([html.P("Select Peak", className="m-0"),
                                 dcc.Dropdown(id="peak_dropdown",
                                              options=[
                                                  {"label": pkname, "value": pkname} for
                                                  pkname in all_peaks_list],
                                              value='Everest',
                                              clearable=False,
                                              multi=False,
                                              className="rounded shadow mb-2")]),
                        dbc.Row([dbc.Col([daq.ToggleSwitch(
                            id='toggle_success_route',
                            value=False,
                            label="Select for successful routes",
                            labelPosition='top',
                            color=COLOR_CHOICE_DICT["mountain_side_blue_green"],
                            className="rounded shadow mt-2 mb-5 pb-2 w-30"
                        )]), ]),
                    ], width=4),
                    dbc.Col([daq.ToggleSwitch(
                        id='toggle_log_linear',
                        value=False,
                        label="Select for log count",
                        labelPosition='top',
                        color=COLOR_CHOICE_DICT["mountain_side_blue_green"],
                        className="rounded shadow mt-2 mb-5 pb-2 w-30"
                    )], width=3),
                ]),
            ], width=8),
        ]),
        dbc.Row(dbc.Col([html.Label("Number Of Unique Routes By Peak"),
                         dcc.Graph(id="all_peaks_routes_chart", className="rounded shadow")
                         ], className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"), ),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([
            dbc.Col([html.Label("Number Of Unique Routes On Selected Peak By Year"),
                     dcc.Graph(id="peak_routes_by_year_chart", className="rounded shadow")], width=6,
                    className="rounded shadow  rounded-top  rounded-end rounded-bottom rounded-start pb-1"),
            dbc.Col([html.Label("Routes Expedition Count On Selected Peak"),
                     dcc.Graph(id="peak_routes_chart", className="rounded shadow")], width=6,
                    className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start pb-1"),

        ]),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([
            dbc.Col([html.Label("Routes Commercial and Non-Commercial "),
                     dcc.Graph(id="peak_comm_routes_chart", className="rounded shadow")], width=12,
                    className="rounded shadow  rounded-top  rounded-end rounded-bottom rounded-start pb-1"),
        ]),

        dbc.Row([html.Div(className='m-4')]),
    ])


def common_bar_elements(x_col: str, y_col: str, color_col: str, selected_peaks_df, log_scale, pkname,
                        showlegend: bool = False, color_hex: str = "crimson"):
    """
    This function encapsulates the common chart elements of the line graphs on the peak expeditions page
    :param y_col: Column to be displayed on Y axis
    :param selected_peaks_df: datafrae with columns to chart

    :return: plotly dash chart
    """

    selected_peaks_df['color_col'] = np.where(selected_peaks_df['PKNAME'] == pkname, "selected", 'not_selected')

    if showlegend:
        fig = px.bar(selected_peaks_df, x=x_col, y=y_col, color=color_col,
                     color_discrete_map={
                         'Not Known': TIME_SERIES_COLOR_DICT["color_gold_2"],
                         'True': TIME_SERIES_COLOR_DICT["spruce_green_light"],
                         'False': TIME_SERIES_COLOR_DICT["color_ochre_1"]
                     },
                     labels={
                         "PEAKID": "Peak Id",
                         "PKNAME": "Peak Name",
                         "HEIGHTM": "Height in meters",
                         "ROUTE": "Full Route Description",
                         "COMM_ROUTE_COUNT": "Number of routes",
                         "COMRTE": "Is commercial route?",
                         "FULL_ROUTE_COUNT": "Count of expeditions on route",
                         "PEAK_ROUTE_COUNT": "Count of routes on peak"
                     },
                     hover_data=["PEAKID", "PKNAME", "HEIGHTM", y_col, color_col],
                     )

    else:
        fig = px.bar(selected_peaks_df, x=x_col, y=y_col, color='color_col',
                     color_discrete_map={
                         'selected': color_hex,
                         'not_selected': COLOR_CHOICE_DICT["mountain_side_blue_green"]
                     },
                     labels={
                         "PEAKID": "Peak Id",
                         "PKNAME": "Peak Name",
                         "HEIGHTM": "Height in meters",
                         "FULL_ROUTE_COUNT": "Count of expeditions on route",
                         "PEAK_ROUTE_COUNT": "Count of routes on peak"
                     },
                     hover_data=["PEAKID", "PKNAME", "HEIGHTM", y_col],
                     )

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})
    # Suppress the y-axis title
    fig.update_layout(xaxis_title=None, xaxis={'categoryorder': 'total descending'}, showlegend=showlegend)

    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    fig.update_traces(opacity=0.9)
    return fig


@callback(Output("all_peaks_routes_chart", "figure"),
          [
              Input("peak_dropdown", "value"),
              Input('toggle_log_linear', 'value'),
              Input('toggle_success_route', 'value')
          ]
          )
def update_line_chart(pkname, log_scale, route_success):
    y_col = 'PEAK_ROUTE_COUNT'
    color_col = x_col = 'PEAKID'

    if route_success:
        peak_routes_agg_df = peak_routes_df[peak_routes_df['ROUTE_SUCCESS'] == 1]
    else:
        peak_routes_agg_df = peak_routes_df

    # Find the number of unique routes on  a peak  (nunique)
    peak_routes_agg_df = peak_routes_agg_df.groupby(['PEAKID', 'PKNAME', 'HEIGHTM'])[
        'ROUTE'].nunique().reset_index().rename(columns={'ROUTE': 'PEAK_ROUTE_COUNT'})
    fig = common_bar_elements(x_col, y_col, color_col, peak_routes_agg_df, log_scale, pkname)

    return fig


@callback(Output("peak_routes_by_year_chart", "figure"),
          [
              Input("peak_dropdown", "value"),
              Input('toggle_log_linear', 'value'),
              Input('toggle_success_route', 'value')
          ])
def update_line_chart(pkname, log_scale, route_success):
    if route_success:
        df = peak_routes_df[peak_routes_df['ROUTE_SUCCESS'] == 1]
    else:
        df = peak_routes_df

    #Unique routes in a peak by year
    one_peak_routes_by_year_df = df[
        df['PKNAME'] == pkname].groupby(
        ['YEAR', 'PEAKID', 'PKNAME', 'HEIGHTM'])['ROUTE'].nunique().reset_index().rename(
        columns={'ROUTE': 'FULL_ROUTE_COUNT'}).sort_values(['FULL_ROUTE_COUNT'], ascending=False)
    one_peak_routes_by_year_df['YEAR'] = one_peak_routes_by_year_df['YEAR'].astype('str')
    y_col = 'FULL_ROUTE_COUNT'
    x_col = 'YEAR'

    fig = px.bar(one_peak_routes_by_year_df, x=x_col, y=y_col,
                 color_discrete_sequence=["#556f7d"] * one_peak_routes_by_year_df.shape[0],
                 labels={
                     "YEAR": "Year",
                     "PEAKID": "Peak Id",
                     "PKNAME": "Peak Name",
                     "HEIGHTM": "Height in meters",
                     "ROUTE": "Route Description",
                     "FULL_ROUTE_COUNT": "Count of distinct routes",
                     "COMM_ROUTE_COUNT": "Number of commercial/non-commercial routes"
                 },
                 hover_data=["PEAKID", "PKNAME", "HEIGHTM", y_col],
                 # markers=True
                 )

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})
    year_array = [str(year) for year in range(1920, 2030, 1)]
    # Suppress the y-axis title
    # print(year_array)
    fig.update_layout(xaxis_title=None, xaxis={'categoryarray': year_array})
    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    fig.update_traces(opacity=0.6)

    # print(one_peak_routes_by_year_df)

    return fig


@callback(Output("peak_routes_chart", "figure"),
          [
              Input("peak_dropdown", "value"),
              Input('toggle_log_linear', 'value'),
              Input('toggle_success_route', 'value')
          ])
def update_line_chart(pkname, log_scale, route_success):
    if route_success:
        df = peak_routes_df[peak_routes_df['ROUTE_SUCCESS'] == 1]
    else:
        df = peak_routes_df
    #Number of expeditions on routes for a peak
    one_peak_routes_df = df[df['PKNAME'] == pkname].groupby(
        ['PEAKID', 'PKNAME', 'HEIGHTM', 'ROUTE']).agg(
        FULL_ROUTE_COUNT=('ROUTE', 'count')).reset_index().sort_values(['FULL_ROUTE_COUNT'], ascending=False)
    y_col = 'FULL_ROUTE_COUNT'
    x_col = 'ROUTE'
    color_col = 'PEAKID'
    fig = common_bar_elements(x_col, y_col, color_col, one_peak_routes_df, log_scale, pkname,
                              color_hex=TIME_SERIES_COLOR_DICT["color_ochre_1"])

    return fig


@callback(Output("peak_comm_routes_chart", "figure"),
          [
              Input("peak_dropdown", "value"),
              Input('toggle_log_linear', 'value'),
              Input('toggle_success_route', 'value')
          ])
def update_line_chart(pkname, log_scale, route_success):
    if route_success:
        df = peak_routes_df[peak_routes_df['ROUTE_SUCCESS'] == 1]
    else:
        df = peak_routes_df
    comm_route_df = df[df['PKNAME'] == pkname]
    one_peak_routes_df = comm_route_df.groupby(['PEAKID', 'PKNAME', 'HEIGHTM', 'ROUTE', 'COMRTE']).agg(
        COMM_ROUTE_COUNT=('COMRTE', 'count')).reset_index().sort_values(['PEAKID', 'COMM_ROUTE_COUNT'])
    y_col = 'COMM_ROUTE_COUNT'
    x_col = 'ROUTE'
    color_col = 'COMRTE'
    fig = common_bar_elements(x_col, y_col, color_col, one_peak_routes_df, log_scale, pkname, showlegend=True)

    return fig
