import sys

sys.path.append("..")

import os
import dash
import pickle
import pandas as pd
import dash_daq as daq
import plotly.express as px
from numpy import random

from color_theme.color_dicts import COLOR_CHOICE_DICT, TIME_SERIES_COLOR_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
# Place this in the home page
import plotly.graph_objects as go

fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Peak Popularity Analysis', name='Peak Popularity Analysis')

# print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
peak_expedition_by_year_season_df = pd.read_csv(os.path.join("app", "data", "dash", "peak_expedition_by_year_season_df.csv"))
commerce_noncommerce_by_year_df  = pd.read_csv(os.path.join("app", "data", "dash", "peak_exped_df.csv"))

# Store the list of countries in a small pickle file
with open(os.path.join("app", "data", "dash", "store_data_lists.pickle"), 'rb') as handle:
    lists_dict = pickle.load(handle)
    all_peaks_list = lists_dict['all_peaks_list']


def get_selected_peaks(min_num_expeditions, date_range, peakname_list):
    popular_peaks_list = list(
        peak_expedition_by_year_season_df[
            peak_expedition_by_year_season_df['EXPEDITIONS_COUNT'] >= min_num_expeditions]['PKNAME'].unique())

    add_peaks_df = peak_expedition_by_year_season_df[(peak_expedition_by_year_season_df['YEAR'] >= date_range[0])
                                                     & (peak_expedition_by_year_season_df['YEAR'] <= date_range[
        1])].copy()
    # We show peaks with highest count of expeditions by default
    selected_peaks_df = peak_expedition_by_year_season_df[
        (peak_expedition_by_year_season_df['PKNAME'].isin(popular_peaks_list)) &
        (peak_expedition_by_year_season_df['YEAR'] >= date_range[0])
        & (peak_expedition_by_year_season_df['YEAR'] <= date_range[1])].copy()

    if peakname_list is None:
        highlight_countries_list = []
    elif isinstance(peakname_list, str):
        highlight_countries_list = [peakname_list]
    else:
        highlight_countries_list = peakname_list

    # print(f"Highlight countries list = {highlight_countries_list}")
    highlight_countries_dict = {country: order for order, country in enumerate(highlight_countries_list)}

    if peakname_list is None:
        add_peaks_df.drop(add_peaks_df.index, inplace=True)
    else:
        new_peaks = list(set(peakname_list).difference(set(selected_peaks_df['PKNAME'].unique())))
        if len(new_peaks) > 0:
            add_peaks_df = add_peaks_df[add_peaks_df['PKNAME'].isin(new_peaks)]
            selected_peaks_df = pd.concat([selected_peaks_df, add_peaks_df], axis="rows")

    num_peaks = len(highlight_countries_list)
    colors = [TIME_SERIES_COLOR_DICT[key] for key in TIME_SERIES_COLOR_DICT.keys()]
    colors = colors[0:num_peaks]

    selection_colors_dict = dict(zip(highlight_countries_list, colors))
    final_colors_dict = {pkname: selection_colors_dict[pkname] if pkname in highlight_countries_list else "#252526" for
                         pkname in list(selected_peaks_df['PKNAME'].unique())}

    # https://towardsdatascience.com/highlighted-line-chart-with-plotly-express-e69e2a27fea8\
    # Line order matters
    selected_peaks_df['PEAK_ORDER'] = selected_peaks_df['PKNAME'].map(highlight_countries_dict).fillna(
        len(highlight_countries_list) + 1)
    selected_peaks_df.sort_values(['PEAK_ORDER', 'PKNAME', 'YEAR_SEASON_DATE'], ascending=False, inplace=True)
    return selected_peaks_df, final_colors_dict, highlight_countries_list


year_dict = {year: str(year) for year in range(1920, 2031, 10)}
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
                                options=[{"label": peakname, "value": peakname} for peakname in all_peaks_list],
                                value=['Everest'],
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
                                marks=year_dict,
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
            dbc.Col([html.Label("Total members on peaks by year"),
                     dcc.Graph(id="peak_member_count_chart", className="rounded shadow")], width=6,
                    className="rounded shadow  rounded-top  rounded-end rounded-bottom rounded-start pb-1"),
            dbc.Col([html.Label("Total hired on peaks by year"),
                     dcc.Graph(id="peak_hired_count_chart", className="rounded shadow")], width=6,
                    className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start pb-1"),

        ]),
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
        dbc.Row([html.Div(className='m-2')]),
        dbc.Row([html.P([
            "* This peak expedition data shows values filtered for expeditions that were successful.",
            html.Br()],
            className="rounded shadow g-5 small fst-italic")
        ]),
        dbc.Row([html.Div(className='m-1')]),
        dbc.Row([html.P(["The visualizations on this page were created to answer questions such as :"
                        , html.Br()
                        , "1.	What is the trend in oxygen usage?"
                        , html.Br()
                        ,
                        "2.	What is the trend in members and number of expeditions in each season of years since expeditions became popular in the Himalayas?"
                        , html.Br()
                        , "3.	Does number of hired personnel follow the same trend as members?"
                        , html.Br()
                        , "4.	What is the percentage of members and hired personnel that have died over the years?"
                        , html.Br()
                        , "5.	Is there a trend that can be detected in oxygen usage on various peaks?"
                        , html.Br()
                        ,
                        "To facilitate analysis and comparison among peaks, the user can select to group peaks with the most expeditions and "
                        , "then in addition, highlight and compare other peaks to this group. "
                          "Peaks with number of expeditions ranging from 1 to 100 in increments of 10 can be compared with individual peaks not in the group selected."
                        , "Individual peaks within the group can also be highlighted against others in the group. "
                 ],
                        className="rounded shadow small fst-italic")
                 ]),

    ])


def common_line_elements(y_col:str, selected_peaks_df, final_colors_dict, log_scale, highlight_countries_list, hover_data):
    """
    This function encapsulates the common chart elements of the line graphs on the peak expeditions page
    :param y_col: Column to be displayed on Y axis
    :param selected_peaks_df: datafrae with columns to chart
    :param final_colors_dict: Dictionary of colors to use for peaks
    :param log_scale: User selection on whether to display log scale
    :param highlight_countries_list: Countries to hilight dictionary
    :param hover_data:

    :return: plotly dash chart
    """
    fig = px.line(selected_peaks_df, x='YEAR_SEASON_DATE', y=y_col, color='PKNAME',
                  color_discrete_map=final_colors_dict,
                  labels={
                      "OXYGEN_USED_PERC":"Percentage of expeditions with oxygen usage",
                      "EXPEDITIONS_COUNT": "Expeditions",
                      "YEAR_SEASON_DATE": "Year Season Date",
                      "MEMBER_DEATHS_PERC": "Member Deaths Percentage",
                      "TOTMEMBERS_COUNT": "Total number of members",
                      "MEMBER_DEATHS_COUNT": "Total number of member deaths",
                      "HIRED_DEATHS_PERC": "Hired Deaths Percentage",
                      "TOTHIRED_COUNT": "Number of Hired",
                      "HIRED_DEATHS_COUNT": "Total number of hired deaths",
                      "PEAKID": "Peak Id",
                      "PKNAME":"Peak Name",
                      "HEIGHTM": "Height in meters"
                  },
                  hover_data=hover_data,
                  markers=True
                  )

    # set thickness
    for num, peakname in enumerate(fig["data"]):
        if peakname["legendgroup"] in highlight_countries_list:
            fig["data"][num]["line"]["width"] = 2

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})
    # Suppress the y-axis title
    fig.update_layout(xaxis_title=None)


    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    if log_scale:
        fig.update_yaxes(type="log", range=[0, 2])  # log range: 10^0=1, 10^5=100000
    fig.update_traces(opacity=0.6)
    return fig


@callback(Output("peak_expeds_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakname_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakname_list)

    hover_data = ["EXPEDITIONS_COUNT", "YEAR_SEASON_DATE", "PEAKID", "PKNAME", "HEIGHTM"]
    y_col = 'EXPEDITIONS_COUNT'
    fig = common_line_elements(y_col, selected_peaks_df, final_colors_dict, log_scale, highlight_countries_list, hover_data)

    return fig


@callback(Output("peak_member_count_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakname_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakname_list)

    hover_data = ['TOTMEMBERS_COUNT', 'YEAR_SEASON_DATE', "PEAKID", "PKNAME"]
    y_col = 'TOTMEMBERS_COUNT'
    fig = common_line_elements(y_col, selected_peaks_df, final_colors_dict, log_scale, highlight_countries_list,
                               hover_data)

    return fig


@callback(Output("peak_hired_count_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakname_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakname_list)

    hover_data = ['TOTHIRED_COUNT', 'YEAR_SEASON_DATE', "PEAKID", "PKNAME", "HEIGHTM"]
    y_col = 'TOTHIRED_COUNT'
    fig = common_line_elements(y_col, selected_peaks_df, final_colors_dict, log_scale, highlight_countries_list,
                               hover_data)

    return fig


@callback(Output("peak_member_deaths_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakname_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakname_list)

    hover_data = ['TOTMEMBERS_COUNT', 'MEMBER_DEATHS_COUNT', "MEMBER_DEATHS_PERC", 'YEAR_SEASON_DATE', "PEAKID", "PKNAME",
                  "HEIGHTM"]
    y_col = 'MEMBER_DEATHS_PERC'
    fig = common_line_elements(y_col, selected_peaks_df, final_colors_dict, log_scale, highlight_countries_list, hover_data)

    return fig


@callback(Output("peak_hired_deaths_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_line_chart(min_num_expeditions, peakname_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakname_list)

    hover_data = ['TOTHIRED_COUNT', 'HIRED_DEATHS_COUNT', "HIRED_DEATHS_PERC", 'YEAR_SEASON_DATE', "PEAKID", "PKNAME",
                  "HEIGHTM"]
    y_col = 'HIRED_DEATHS_PERC'
    fig = common_line_elements(y_col, selected_peaks_df, final_colors_dict, log_scale, highlight_countries_list, hover_data)

    return fig


@callback(Output("peak_oxygen_chart", "figure"),
          [
              Input("num_expeditions_dropdown", "value"),
              Input("peak_selection_dropdown", "value"),
              Input('year_slider', 'value'),
              Input('toggle_log_linear', 'value')
          ])
def update_oxygen_line_chart(min_num_expeditions, peakname_list, date_range, log_scale):
    selected_peaks_df, final_colors_dict, highlight_countries_list = get_selected_peaks(min_num_expeditions, date_range,
                                                                                        peakname_list)

    final_colors_dict_list = list(final_colors_dict.items())
    random.shuffle(final_colors_dict_list)
    final_colors_dict = dict(final_colors_dict_list)

    hover_data = ["OXYGEN_USED_PERC", "YEAR_SEASON_DATE", "PEAKID", "PKNAME", "HEIGHTM"]
    y_col = "OXYGEN_USED_PERC"
    fig = common_line_elements(y_col, selected_peaks_df, final_colors_dict, log_scale, highlight_countries_list,
                               hover_data)

    return fig
