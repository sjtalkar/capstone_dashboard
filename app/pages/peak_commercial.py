import sys

sys.path.append("..")

import os
import dash
import plotly.express as px
from numpy import random

from color_theme.color_dicts import COLOR_CHOICE_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
from lib.data_preparation.peaks_data import PeakExpedition
# Place this in the home page
import plotly.graph_objects as go

fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Peak Commercial Expedition Analysis', name='Peak Commercial Expedition Analysis')

# print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
peak_expedition = PeakExpedition(os.path.join('app', 'data', 'raw_data'), os.path.join('app', 'data', 'nhpp'))
# commerce_noncommerce_by_season_df, commerce_peaks_list = peak_expedition.create_commerce_noncommerce_peak_aggregation(
#     by_season=True)
commerce_noncommerce_by_year_df, commerce_peaks_list = peak_expedition.create_commerce_noncommerce_peak_aggregation(
    by_season=False)

# print(f"commerce_peaks_list = {commerce_peaks_list}")

min_year = commerce_noncommerce_by_year_df['YEAR'].min()
max_year = commerce_noncommerce_by_year_df['YEAR'].max()
all_peaks_list = list(commerce_noncommerce_by_year_df['PEAKID'].unique())

year_dict = {year: str(year) for year in range(1920, 2031, 1)}
layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                html.P("Select time range for expedition:"),
                dcc.RangeSlider(1920, 2030, 1,
                                value=[1920, 2030],
                                marks=year_dict,
                                id='year_slider',
                                className="rounded shadow mb-5"
                                ),
            ], width=4
            )
        ]),
        dbc.Row(dbc.Col([html.Label("Commercial Expeditions By Year"),
                         dcc.Graph(id="commerce_expeds_chart", className="rounded shadow")
                         ],
                        className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"), ),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([html.P([
            "* This peak expedition data shows values filtered for expeditions that were successful.",
            html.Br()],
            className="rounded shadow g-5 small fst-italic")
        ])
    ])


@callback(Output("commerce_expeds_chart", "figure"),
          [
              Input('year_slider', 'value'),
          ])
def update_line_chart(year_selection):
    selected_year_df = commerce_noncommerce_by_year_df[
        (commerce_noncommerce_by_year_df[
             'YEAR'] == year_selection)
        & (commerce_noncommerce_by_year_df['PEAKID'].isin(
            commerce_peaks_list))].copy()

    fig = px.bar(selected_year_df, x='PKNAME', y='CA', color='PEAKID',
                 # color_discrete_map=final_colors_dict,
                 labels={
                     "PKNAME": "Peak Name",

                 },

                 )

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)

    return fig


@callback(Output("peak_member_deaths_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakid_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakid_list)

    fig = px.line(selected_peaks_df, x='YEAR_SEASON_DATE', y='MEMBER_DEATHS_PERC', color='PEAKID',
                  color_discrete_map=final_colors_dict,
                  labels={
                      "MEMBER_DEATHS_PERC": "Member Deaths Percentage",
                      "YEAR_SEASON_DATE": "",
                  },
                  markers=True
                  )

    # set thickness
    for num, peakid in enumerate(fig["data"]):
        if peakid["legendgroup"] in highlight_countries_list:
            fig["data"][num]["line"]["width"] = 1

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000
    fig.update_traces(opacity=0.6)

    return fig


@callback(Output("peak_hired_deaths_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakid_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakid_list)

    fig = px.line(selected_peaks_df, x='YEAR_SEASON_DATE', y='HIRED_DEATHS_PERC', color='PEAKID',
                  color_discrete_map=final_colors_dict,
                  labels={
                      "HIRED_DEATHS_PERC": "Hired Deaths Percentage",
                      "YEAR_SEASON_DATE": "",
                  },
                  markers=True
                  )

    # set thickness
    for num, peakid in enumerate(fig["data"]):
        if peakid["legendgroup"] in highlight_countries_list:
            fig["data"][num]["line"]["width"] = 1

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000
    fig.update_traces(opacity=0.6)

    return fig


@callback(Output("peak_oxygen_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_oxygen_line_chart(min_num_expeditions, peakid_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakid_list)

    final_colors_dict_list = list(final_colors_dict.items())
    random.shuffle(final_colors_dict_list)
    final_colors_dict = dict(final_colors_dict_list)

    # print(
    #     f"Selected peaks {selected_peaks_df[(selected_peaks_df['PEAKID'] == 'EVER')][['PEAKID', 'EXPEDITIONS_COUNT', 'OXYGEN_USED_PERC']]}")

    fig = px.line(selected_peaks_df, x='YEAR_SEASON_DATE', y='OXYGEN_USED_PERC', color='PEAKID',
                  color_discrete_map=final_colors_dict,
                  labels={
                      "OXYGEN_USED_PERC": "Oxygen Usage Percentage",
                      "YEAR_SEASON_DATE": "",
                  },
                  markers=True
                  )

    # set thickness
    for num, peakid in enumerate(fig["data"]):
        if peakid["legendgroup"] in highlight_countries_list:
            fig["data"][num]["line"]["width"] = 1

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000
    fig.update_traces(opacity=0.6)

    return fig
