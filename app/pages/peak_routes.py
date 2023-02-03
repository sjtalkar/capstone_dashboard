import sys

sys.path.append("..")

import os
import dash
import numpy as np
import dash_daq as daq
import plotly.express as px

from color_theme.color_dicts import COLOR_CHOICE_DICT, TIME_SERIES_COLOR_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
from lib.data_preparation.peaks_data import PeakExpedition
# Place this in the home page
import plotly.graph_objects as go

fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Peak Routes Analysis', name='Peak Routes Analysis')

# print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
peak_expedition = PeakExpedition(os.path.join('app', 'data', 'raw_data'), os.path.join('app', 'data', 'nhpp'))
peak_routes_df = peak_expedition.create_peak_route_aggregation()

all_peaks_list = list(peak_routes_df['PEAKID'].unique())

layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([

                        html.P("Select Peak", className="m-0"),
                        dcc.Dropdown(id="peak_dropdown",
                                     options=[
                                         {"label": peakid, "value": peakid} for
                                         peakid in all_peaks_list],
                                         value='EVER',
                                         clearable=False,
                                         multi=False,
                                         className="rounded shadow mb-2")

                    ], width=4),
                    dbc.Col([daq.ToggleSwitch(
                        id='toggle_log_linear',
                        value=False,
                        label="Select for log count.",
                        labelPosition='top',
                        color=COLOR_CHOICE_DICT["mountain_side_blue_green"],
                        className="rounded shadow mt-2 mb-5 pb-2 w-30"
                    )], width=3),
                ]),
            ], width=8),
        ]),
        dbc.Row(dbc.Col([html.Label("Number of routes by peak"),
                         dcc.Graph(id="all_peaks_routes_chart", className="rounded shadow")
                         ], className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"), ),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([
            dbc.Col([html.Label("Top routes on peaks by year"),
                     dcc.Graph(id="peak_routes_by_year_chart", className="rounded shadow")], width=6,
                    className="rounded shadow  rounded-top  rounded-end rounded-bottom rounded-start pb-1"),
            dbc.Col([html.Label("Total routes on peak"),
                     dcc.Graph(id="peak_routes_chart", className="rounded shadow")], width=6,
                    className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start pb-1"),

        ]),
        dbc.Row([html.Div(className='m-4')]),
     ])


def common_bar_elements(x_col:str, y_col:str, color_col:str, selected_peaks_df, log_scale, peakid ):
    """
    This function encapsulates the common chart elements of the line graphs on the peak expeditions page
    :param y_col: Column to be displayed on Y axis
    :param selected_peaks_df: datafrae with columns to chart

    :return: plotly dash chart
    """

    selected_peaks_df['color_col'] = np.where(selected_peaks_df['PEAKID'] == peakid, "selected", 'not_selected')


    fig = px.bar(selected_peaks_df, x=x_col, y=y_col, color='color_col',
                 color_discrete_map={
                     'selected': '#c26a2d',
                     'not_selected': 'lightslategray'
                 },
                  labels={

                      "PEAKID": "Peak Id",
                      "PKNAME":"Peak Name",
                      "HEIGHTM": "Height in meters",
                      "FULL_ROUTE": "Full Route Description",
                      "FULL_ROUTE_COUNT" : "Count of distinct routes",
                      "NUM_FULL_ROUTES": "Number of distinct full routes"
                  },
                  hover_data=["PEAKID", "PKNAME", "HEIGHTM", y_col],
                  )




    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})
    # Suppress the y-axis title
    fig.update_layout(xaxis_title=None, xaxis={'categoryorder': 'total descending'}, showlegend=False)

    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    fig.update_traces(opacity=0.6)
    return fig


@callback(Output("all_peaks_routes_chart", "figure"),
          [
              Input("peak_dropdown", "value"),
              Input('toggle_log_linear', 'value')
          ]
         )
def update_line_chart(peakid, log_scale):
    y_col = 'NUM_FULL_ROUTES'
    color_col = x_col = 'PEAKID'


    fig = common_bar_elements(x_col, y_col, color_col, peak_routes_df, log_scale, peakid)

    return fig


@callback(Output("peak_routes_by_year_chart", "figure"),
          [
              Input("peak_dropdown", "value"),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart( peakid, log_scale):
    one_peak_routes_by_year_df = peak_expedition.route_df[peak_expedition.route_df['PEAKID'] == peakid].groupby(
        ['YEAR', 'FULL_ROUTE', 'PEAKID', 'PKNAME', 'HEIGHTM']).agg(
        FULL_ROUTE_COUNT=('FULL_ROUTE', 'count')).reset_index().sort_values(['FULL_ROUTE_COUNT'], ascending=False)
    one_peak_routes_by_year_df['YEAR'] = one_peak_routes_by_year_df['YEAR'].astype('str')
    y_col = 'FULL_ROUTE_COUNT'
    x_col = 'YEAR'

    fig = px.bar(one_peak_routes_by_year_df, x=x_col, y=y_col,
                 labels={
                     "PEAKID": "Peak Id",
                     "PKNAME": "Peak Name",
                     "HEIGHTM": "Height in meters",
                     "FULL_ROUTE": "Full Route Description",
                     "FULL_ROUTE_COUNT": "Count of distinct routes",
                     "NUM_FULL_ROUTES": "Number of distinct full routes"
                 },
                 hover_data=["PEAKID", "PKNAME", "HEIGHTM", y_col],
                 # markers=True
                 )

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})
    year_array = [str(year) for year in range (1920, 2030, 1)]
    # Suppress the y-axis title
    #print(year_array)
    fig.update_layout(xaxis_title=None, xaxis={'categoryarray': year_array})
    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    fig.update_traces(opacity=0.6)

    #print(one_peak_routes_by_year_df)

    return fig


@callback(Output("peak_routes_chart", "figure"),
          [
              Input("peak_dropdown", "value"),
              Input('toggle_log_linear', 'value')

          ])
def update_line_chart(peakid, log_scale):
    one_peak_routes_df = peak_expedition.route_df[peak_expedition.route_df['PEAKID'] == peakid].groupby(
        ['PEAKID', 'PKNAME', 'HEIGHTM', 'FULL_ROUTE']).agg(
        FULL_ROUTE_COUNT=('FULL_ROUTE', 'count')).reset_index().sort_values(['FULL_ROUTE_COUNT'], ascending=False)
    y_col = 'FULL_ROUTE_COUNT'
    x_col = 'FULL_ROUTE'
    color_col = 'PEAKID'
    fig = common_bar_elements(x_col, y_col, color_col,  one_peak_routes_df, log_scale, peakid)

    return fig


