import sys
sys.path.append("..")

import os
import dash
import pandas as pd
import dash_daq as daq
import plotly.express as px
from numpy import random

from color_theme.color_dicts import COLOR_CHOICE_DICT, TIME_SERIES_COLOR_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
from lib.data_preparation.peaks_data import PeakExpedition
#Place this in the home page
import plotly.graph_objects as go
fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Peak Popularity Analysis', name='Peak Popularity Analysis')


#print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
peak_expedition = PeakExpedition(os.path.join('app','data','raw_data'))
_ = peak_expedition.set_latitude_longitude_with_peak_mapppings(os.path.join('app','data','nhpp'))
peak_expedition_by_year_season_df = peak_expedition.create_peak_aggregation()


min_year = peak_expedition_by_year_season_df['YEAR'].min()
max_year = peak_expedition_by_year_season_df['YEAR'].max()
all_peaks_list = list(peak_expedition_by_year_season_df['PEAKID'].unique())

def get_selected_peaks(min_num_expeditions, date_range, peakid_list):
    popular_peaks_list = list(
        peak_expedition_by_year_season_df[
            peak_expedition_by_year_season_df['EXPEDITIONS_COUNT'] >= min_num_expeditions]['PEAKID'].unique())

    add_peaks_df = peak_expedition_by_year_season_df[(peak_expedition_by_year_season_df['YEAR'] >= date_range[0])
                                                     & (peak_expedition_by_year_season_df['YEAR'] <= date_range[
        1])].copy()
    # We show peaks with highest count of expeditions by default
    selected_peaks_df = peak_expedition_by_year_season_df[
        (peak_expedition_by_year_season_df['PEAKID'].isin(popular_peaks_list)) &
        (peak_expedition_by_year_season_df['YEAR'] >= date_range[0])
        & (peak_expedition_by_year_season_df['YEAR'] <= date_range[1])].copy()

    if peakid_list is None:
        highlight_countries_list = []
    elif isinstance(peakid_list, str):
        highlight_countries_list = [peakid_list]
    else:
        highlight_countries_list = peakid_list

    # print(f"Highlight countries list = {highlight_countries_list}")
    highlight_countries_dict = {country: order for order, country in enumerate(highlight_countries_list)}

    if peakid_list is None:
        add_peaks_df.drop(add_peaks_df.index, inplace=True)
    else:
        new_peaks = list(set(peakid_list).difference(set(selected_peaks_df['PEAKID'].unique())))
        if len(new_peaks) > 0:
            add_peaks_df = add_peaks_df[add_peaks_df['PEAKID'].isin(new_peaks)]
            selected_peaks_df = pd.concat([selected_peaks_df, add_peaks_df], axis="rows")

    num_peaks = len(highlight_countries_list)
    colors = [TIME_SERIES_COLOR_DICT[key] for key in TIME_SERIES_COLOR_DICT.keys()]
    colors = colors[0:num_peaks]

    selection_colors_dict = dict(zip(highlight_countries_list, colors))
    final_colors_dict = {peakid: selection_colors_dict[peakid] if peakid in highlight_countries_list else "#252526" for
                         peakid in list(selected_peaks_df['PEAKID'].unique())}

    # https://towardsdatascience.com/highlighted-line-chart-with-plotly-express-e69e2a27fea8\
    # Line order matters
    selected_peaks_df['PEAK_ORDER'] = selected_peaks_df['PEAKID'].map(highlight_countries_dict).fillna(
        len(highlight_countries_list) + 1)
    selected_peaks_df.sort_values(['PEAK_ORDER', 'PEAKID', 'YEAR_SEASON_DATE'], ascending=False, inplace=True)
    return selected_peaks_df, final_colors_dict, highlight_countries_list

layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                dbc.Row([
                    dbc.Col([

                        html.P("Peak expedition count greater than", className="m-0"),
                        dcc.Dropdown(id="num_expeditions_dropdown",
                                     options=[
                                         {"label": f"{num_expeditions} Expeditions", "value": num_expeditions} for
                                         num_expeditions in
                                         [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]], value=10, clearable=False,
                                     className="rounded shadow mb-2")

                    ], width=4),
                    dbc.Col([
                        html.P("Highlight or Add Peaks:", className="m-0"),
                        dbc.Row([
                            dcc.Dropdown(
                                id="peak_selection_dropdown",
                                options=[{"label": peakid, "value": peakid} for peakid in all_peaks_list],
                                value=['EVER'],
                                clearable=False,
                                multi=True,
                                className="rounded shadow"
                            )
                        ]),
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
            dbc.Col([
                html.P("Select time range for expedition:"),
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
                                className="rounded shadow mb-5"

                                ),
            ], width=4
            )
        ]),
        dbc.Row(dbc.Col([html.Label("Number of expedition by year"),
                         dcc.Graph(id="peak_expeds_chart", className="rounded shadow")
                         ], className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"), ),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([
            dbc.Col([html.Label("Member deaths (out of total members) on peaks by year"),
                     dcc.Graph(id="peak_member_deaths_chart", className="rounded shadow")], width=6,
                    className="rounded shadow  rounded-top  rounded-end rounded-bottom rounded-start pb-1"),
            dbc.Col([html.Label("Hired deaths (out of total hired) on peaks by year"),
                     dcc.Graph(id="peak_hired_deaths_chart", className="rounded shadow")], width=6,
                    className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start pb-1"),

        ]),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([
            dbc.Col([html.Label("Oxygen usage (for expeditions) on peaks by year"),
                     dcc.Graph(id="peak_oxygen_chart", className="rounded shadow")], width=12,
                    className="rounded shadow  rounded-top  rounded-end rounded-bottom rounded-start  pb-1"),
        ]),

    ]
)

@callback(Output("peak_expeds_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakid_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakid_list)

    fig = px.line(selected_peaks_df, x='YEAR_SEASON_DATE', y='EXPEDITIONS_COUNT', color='PEAKID',
                  color_discrete_map=final_colors_dict,
                  labels={
                      "EXPEDITIONS_COUNT": "Expeditions",
                      "YEAR_SEASON_DATE": "",
                  },
                  markers=True
                  )

    # print(fig['data'])
    # set thickness
    for num, peakid in enumerate(fig["data"]):
        if peakid["legendgroup"] in highlight_countries_list:
            fig["data"][num]["line"]["width"] = 2

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000
    fig.update_traces(opacity=0.6)

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


