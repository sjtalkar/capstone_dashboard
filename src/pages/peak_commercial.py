import sys

sys.path.append("..")

import os
import dash
import pickle
import pandas as pd
import plotly.express as px

from color_theme.color_dicts import COLOR_CHOICE_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, callback, Input
from lib.data_preparation.peaks_data import  TERM_REASON_DICT
# Place this in the home page
import plotly.graph_objects as go

fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Peak Commercial Expedition Analysis', name='Peak Commercial Expedition Analysis')

# print(f"This is the current directory : {os.path.abspath(os.getcwd())}")

commerce_noncommerce_by_year_df = pd.read_csv(
    os.path.join("data", "dash", "commerce_noncommerce_by_year_df.csv"))
exped_commercial_type_df = pd.read_csv(os.path.join("data", "dash", "exped_commercial_type_df.csv"))
commerce_noncommerce_by_year_df = commerce_noncommerce_by_year_df.fillna(0)


with open(os.path.join( "data", "dash", "store_data_lists.pickle"), 'rb') as handle:
    lists_dict = pickle.load(handle)
    all_peaks_list = lists_dict['all_peaks_list']
    commerce_peaks_list = lists_dict['commerce_peaks_list']

year_dict = {year: str(year) for year in range(1920, 2031, 10)}
layout = html.Div(
    [
        dbc.Row([
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
        dbc.Row([html.Div(className='m-1')]),
        dbc.Row([html.P(["Click on peaks in legend to the right of chart to select/deselect and focus on one peak."])]),
        dbc.Row([html.Div(className='m-1')]),
        dbc.Row([dbc.Col(
            [html.Label("Oxygen usage percent of expedition(bubble size is proportional to expedition count)"),
             dcc.Graph(id="oxygen_usage_perc_chart", className="rounded shadow")
             ],
            width=12,
            className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),]),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([dbc.Col([html.Label("Average Base Camps By Year"),
                          dcc.Graph(id="base_camps_chart", className="rounded shadow"),
                          ],
                         width=6,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start pb-2"),
                 dbc.Col([html.Label("Average Days To Summit By Year"),
                          dcc.Graph(id="summit_days_chart", className="rounded shadow")
                          ],
                         width=6,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 ]),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([dbc.Col([html.Label("Total Commercial Expeditions By Year"),
                          dcc.Graph(id="total_commerce_expeds_chart", className="rounded shadow")
                          ],
                         width=6,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 dbc.Col([html.Label("Percentage Commercial Expeditions By Year"),
                          dcc.Graph(id="commerce_expeds_chart", className="rounded shadow")
                          ],
                         width=6,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),

                 ]),
        dbc.Row([html.Div(className='m-4')]),
        # dbc.Row([dbc.Col([html.Label("Total Base Camps By Year"),
        #                   dcc.Graph(id="total_base_camps_chart", className="rounded shadow")
        #                   ],
        #                  width=6,
        #                  className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
        #
        #          dbc.Col([html.Label("Total Days Taken By All Expeditions To Summit By Year"),
        #                   dcc.Graph(id="total_summit_days_chart", className="rounded shadow")
        #                   ],
        #                  width=6,
        #                  className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
        #          ]),
        # dbc.Row([html.Div(className='m-4')]),

        dbc.Row([
                 dbc.Col([html.Label("Member deaths (as percent of total members)"),
                          dcc.Graph(id="member_deaths_perc_chart", className="rounded shadow")
                          ],
                         width=6,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 dbc.Col([html.Label("Hired deaths (as percent of total hired)"),
                          dcc.Graph(id="hired_deaths_perc_chart", className="rounded shadow")
                          ],
                         width=6,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 ]),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([dbc.Col([html.Label("Termination Reasons"),
                          dcc.Graph(id="termination_reason_chart", className="rounded shadow")
                          ],
                        width=12,
                        className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2")
                    ]),
        dbc.Row([dbc.Col([html.P(["0: Unknown", html.Br(), "1: Success (main peak)",html.Br(),
                                  "2: Success(subpeak, foresummit)", html.Br(),
                                  "3: Success (claimed)", html.Br(),
                                  "4: Bad weather (storms, high winds)", html.Br(),
                                  "5: Bad conditions (deep snow, avalanching, falling ice, or rock)", html.Br(),
                                  "6: Accident (death or serious injury)", html.Br(),
                                  "7: Illness, AMS, exhaustion, or frostbite"
                                  ], className="fst-italic fs-6 pt-1 pb-1")]),
                 dbc.Col([html.P(["8: Lack (or loss) of supplies, support or equipment", html.Br(), "9: Lack of time", html.Br(),
                                  "10: Route technically too difficult, lack of experience, strength, or motivation", html.Br(),
                                  "11: Did not reach base", html.Br(),
                                  "12: Did not attempt climb", html.Br(),
                                  "13: Attempt rumored", html.Br(),
                                  "14: Other"
                                  ], className="fst-italic fs-6 pt-1 pb-1")])
                 ]),
        dbc.Row([html.Div(className='m-4')]),

    ])

def common_df_setup(df, date_range):
    """
    Role of this function:
    For all the bar graphs, the filter includes a date range and a set of peaks that are commercial peaks
    Filter the dataframe by the filter and create a dictionary to uniformly color the peaks with the same set of colors
    :param df: dataframe with data for the chart
    :param date_range: Date range slider tuple 
    :return: filtered dataframe and a color dictionary for the commercial peaks  
    """
    selected_years_df = df[(df['YEAR'] >= date_range[0])
                           & (df['YEAR'] <= date_range[1])
                           & (df['PKNAME'].isin(commerce_peaks_list))].copy()
    selected_years_df['YEAR'] = selected_years_df['YEAR'].astype('str')

    final_colors_dict = {key: COLOR_CHOICE_DICT[value] for key, value in zip(commerce_peaks_list,
                                                                             ["mountain_cloud_blue",
                                                                              "parallel_theme_blue",
                                                                              "mountain_side_blue_green",
                                                                              "spruce_green_light",
                                                                              "spruce_green",
                                                                              ])}
    return selected_years_df, final_colors_dict


def create_bar_chart_figure(selected_years_df, final_colors_dict, y_col: str, y_col_title: str):
    """
    This function 
    :param selected_years_df: filtered dataframe
    :param final_colors_dict: dictionary of colors for commercial peaks
    :param y_col: column value to be plotted in bar graph
    :param y_col_title: 
    :return: 
    """
    fig = px.bar(selected_years_df,
                 x='YEAR',
                 y=y_col,
                 color='PKNAME',
                 color_discrete_map=final_colors_dict,
                 text_auto=True,
                 labels={
                     "PKNAME": "Peak Name",
                     y_col: y_col_title,
                     "YEAR": "Year",
                     "HEIGHTM": "Height in meters",
                     "EXPEDITIONS_COUNT": "Number of Expeditions"
                 },
                 hover_data=["YEAR", "PKNAME", "HEIGHTM", "EXPEDITIONS_COUNT", y_col]

                 )
    fig = common_layout_elements(fig)
    return fig


def create_line_chart_figure(selected_years_df, final_colors_dict, y_col: str, y_col_title: str):
    """
    This function creates a line for each of the peaks with time along the x-axis and y_col's values along y axis
    :param selected_years_df: filtered dataframe
    :param final_colors_dict: dictionary of colors for commercial peaks
    :param y_col: column value to be plotted in bar graph
    :param y_col_title:
    :return:
    """
    fig = px.line(selected_years_df,
                 x='YEAR',
                 y=y_col,
                 color='PKNAME',
                 color_discrete_map=final_colors_dict,
                 #text = y_col,
                 labels={
                     "PKNAME": "Peak Name",
                     y_col: y_col_title,
                     "YEAR": "Year",
                     "HEIGHTM": "Height in meters",
                     "EXPEDITIONS_COUNT": "Number of Expeditions"
                 },
                 hover_data=["YEAR", "PKNAME", "HEIGHTM", "EXPEDITIONS_COUNT", y_col]

                 )
    fig = common_layout_elements(fig)
    fig.update_traces(textposition="bottom right")
    return fig


def create_sized_scatter_chart_figure(selected_years_df, final_colors_dict, y_col: str, y_col_title: str):
    """
    This function
    :param selected_years_df: filtered dataframe
    :param final_colors_dict: dictionary of colors for commercial peaks
    :param y_col: column value to be plotted in bar graph
    :param y_col_title:
    :return:
    """
    fig = px.scatter(selected_years_df,
                     x='YEAR',
                     y=y_col,
                     color='PKNAME',
                     color_discrete_map=final_colors_dict,
                     size='EXPEDITIONS_COUNT',
                     labels={
                         "PKNAME": "Peak Name",
                         y_col: y_col_title,
                         "YEAR": "Year",
                         "HEIGHTM": "Height in meters",
                         "EXPEDITIONS_COUNT": "Number of Expeditions"
                     },
                     hover_data=["YEAR", "PKNAME", "HEIGHTM", "EXPEDITIONS_COUNT", y_col]

                     )
    fig = common_layout_elements(fig)
    return fig

def common_layout_elements(fig):
    """
    Set background and legend elements for chart
    :param fig: Plotly Dash figure
    :return:
    """
    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_layout(xaxis=dict(title=''), yaxis=dict(title=''))
    fig.update_layout(showlegend=True, legend=dict(
        title_font_family='Arial',
        font=dict(
            size=8
        )
    ))

    fig.update_yaxes(showgrid=False,
                     #visible=False, showticklabels=False
                     )
    fig.update_xaxes(showgrid=False)
    fig.update_traces(opacity=0.8)
    return fig


@callback(Output("commerce_expeds_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
    fig = create_line_chart_figure(selected_years_df, final_colors_dict, y_col="COMMERCIAL_ROUTES_PERC",
                                y_col_title="Percentage of Commercial Expeditions")
    fig = common_layout_elements(fig)

    return fig


@callback(Output("summit_days_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
    fig = create_line_chart_figure(selected_years_df, final_colors_dict, y_col="SUMMIT_DAYS_MEAN",
                                y_col_title="Average number of days to Summit")
    fig = common_layout_elements(fig)
    return fig


@callback(Output("base_camps_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
    fig = create_line_chart_figure(selected_years_df, final_colors_dict, y_col="NUM_CAMPS_MEAN",
                                y_col_title="Average Number of Camps")
    fig = common_layout_elements(fig)
    return fig


# @callback(Output("total_summit_days_chart", "figure"),
#           [Input('year_slider', 'value')],
#           )
# def update_chart(date_range):
#     selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
#     fig = create_bar_chart_figure(selected_years_df, final_colors_dict, y_col="SUMMIT_DAYS_COUNT",
#                                 y_col_title="Total number of days to Summit")
#     fig = common_layout_elements(fig)
#     return fig


@callback(Output("total_commerce_expeds_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
    fig = create_line_chart_figure(selected_years_df, final_colors_dict, y_col="COMMERCIAL_ROUTES_COUNT",
                                y_col_title="Total number of commercial routes")
    fig = common_layout_elements(fig)

    return fig


# @callback(Output("total_base_camps_chart", "figure"),
#           [Input('year_slider', 'value')],
#           )
# def update_chart(date_range):
#     selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
#     fig = create_bar_chart_figure(selected_years_df, final_colors_dict, y_col="NUM_CAMPS_COUNT",
#                                 y_col_title="Total Number of Camps")
#     fig = common_layout_elements(fig)
#     return fig


@callback(Output("oxygen_usage_perc_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
    fig = create_sized_scatter_chart_figure(selected_years_df, final_colors_dict, y_col="OXYGEN_USED_PERC",
                                  y_col_title="Percentage of expeditions using oxygen")
    fig = common_layout_elements(fig)

    return fig


@callback(Output("member_deaths_perc_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
    fig = create_line_chart_figure(selected_years_df, final_colors_dict, y_col="MEMBER_DEATHS_PERC",
                                  y_col_title="Percentage of member deaths")
    fig = common_layout_elements(fig)

    return fig


@callback(Output("hired_deaths_perc_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(commerce_noncommerce_by_year_df, date_range)
    fig = create_line_chart_figure(selected_years_df, final_colors_dict, y_col="HIRED_DEATHS_PERC",
                                  y_col_title="Percentage of hired deaths")
    fig = common_layout_elements(fig)

    return fig


@callback(Output("termination_reason_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(exped_commercial_type_df, date_range)
    reason_count_df = selected_years_df.groupby(
        ['PEAKID', 'PKNAME', 'HEIGHTM', 'COMRTE', 'TERMREASON']).agg(
        TERMINATION_REASON_COUNT=('TERMREASON', 'count')
    ).reset_index()
    reason_count_df['TERMREASON_STRING'] = reason_count_df['TERMREASON'].map(TERM_REASON_DICT)
    reason_count_df['TERMREASON'] = reason_count_df['TERMREASON'].astype('str')

    reason_count_df['COMRTE_STRING'] = reason_count_df['COMRTE'].map({0:"Non-Commercial", 1:"Commercial"})

    fig = px.bar(reason_count_df,
                 x='TERMREASON',
                 y='TERMINATION_REASON_COUNT',
                 barmode='group',
                 labels = {
                                "PKNAME": "Peak Name",
                                 "YEAR": "Year",
                                 "HEIGHTM": "Height in meters",
                                 "COMRTE_STRING": "Route Type",
                                 "TERMREASON_STRING" : "Termination reason for expedition",
                                 'TERMINATION_REASON_COUNT': 'Count of expeditions',
                                 "TERMREASON" : ''
                            },
                 hover_data = [ "PKNAME", "HEIGHTM", "TERMREASON_STRING"],
                 facet_col='COMRTE_STRING',
                 facet_col_wrap=4, facet_row_spacing=0.15, facet_col_spacing=0.1,
                 color='PKNAME',
                 color_discrete_map=final_colors_dict,
                 category_orders = dict(TERMREASON=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
                                                    '13', '14']),
                 )

    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_layout(xaxis=dict(title=''), yaxis=dict(title=''))
    fig.update_layout(showlegend=True, legend=dict(
        title_font_family='Courier New',
        font=dict(
            size=8
        )
    ))

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    fig.update_traces(opacity=0.8)
    return fig
