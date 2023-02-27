import sys

sys.path.append("..")

import os
import dash
import pickle
import pandas as pd
import dash_daq as daq
import plotly.express as px

from color_theme.color_dicts import COLOR_CHOICE_DICT, TIME_SERIES_COLOR_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, callback, Input

# Place this in the home page
import plotly.graph_objects as go



fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Commercial and Non-commercial Expedition Distributions',
                   name='Commercial and Non-commercial Expedition Distributions')

# print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
peak_exped_df = pd.read_csv(os.path.join( "src", "data", "dash", "peak_exped_df.csv"), dtype={'COMRTE':object})
print(
    f'File Path = {os.path.join(os.path.abspath(os.path.join("src", "data", "dash", "peak_exped_df.csv")), )}')

#These are generated every time page is loaded
exped_commercial_type_df = peak_exped_df[~peak_exped_df['COMRTE'].isna()].copy()

with open(os.path.join("src", "data", "dash", "store_data_lists.pickle"), 'rb') as handle:
    lists_dict = pickle.load(handle)
    all_peaks_list = lists_dict['all_peaks_list']
    commerce_peaks_list = lists_dict['commerce_peaks_list']

success_exped_commercial_type_df = exped_commercial_type_df[exped_commercial_type_df['TERMREASON'] == 1]
all_exped_commercial_type_df = exped_commercial_type_df

year_dict = {year: str(year) for year in range(1920, 2031, 10)}
layout = html.Div(
    [
        dbc.Row([
            dbc.Col([
                html.P("View Distribution For Peak:", className="m-0"),
                dbc.Row([
                    dcc.Dropdown(
                        id="peak_selection_dropdown",
                        options=[{"label": peakname, "value": peakname} for peakname in commerce_peaks_list],
                        value='Everest',
                        clearable=False,
                        multi=False,
                        className="rounded shadow"
                    )
                ]),
                dbc.Row([daq.ToggleSwitch(
                    id='toggle_success_exped',
                    value=False,
                    label="Select for successful expeditions only",
                    labelPosition='top',
                    color=COLOR_CHOICE_DICT["mountain_side_blue_green"],
                    className="rounded shadow mt-2 mb-5 pb-2 w-30"
                )]),
            ], width=4),

            dbc.Col([
                html.P("Select time range for expedition:"),
                dcc.RangeSlider(1920, 2030, 10,
                                value=[1920, 2030],
                                marks=year_dict,
                                id='year_slider',
                                className="rounded shadow mb-5"
                                ),
            ], width=4
            ),
        ]),
        dbc.Row([dbc.Col([html.Label("Oxygen Usage"),
                          dcc.Graph(id="oxygen_usage_distrib_chart", className="rounded shadow"),
                          ],
                         width=4,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start pb-2"),
                 dbc.Col([html.Label("Average Member Deaths"),
                          dcc.Graph(id="member_deaths_distrib_chart", className="rounded shadow")
                          ],
                         width=4,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 dbc.Col([html.Label("Average Hired Deaths"),
                          dcc.Graph(id="hired_deaths_distrib_chart", className="rounded shadow")
                          ],
                         width=4,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 ]),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([dbc.Col([html.Label("Average Base Camps By Year"),
                          dcc.Graph(id="total_base_camps_distrib_chart", className="rounded shadow")
                          ],
                         width=4,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 dbc.Col([html.Label("Average Expedition Days"),
                          dcc.Graph(id="total_exped_days_distrib_chart", className="rounded shadow")
                          ],
                         width=4,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 dbc.Col([html.Label("Average Days to Summit from Base Camp"),
                          dcc.Graph(id="total_summit_days_distrib_chart", className="rounded shadow")
                          ],
                         width=4,
                         className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start  pb-2"),
                 ]),
        dbc.Row([html.Div(className='m-4')]),

    ])


def common_df_setup(date_range, chosenpeak, success_only):
    """
    Role of this function:
    For all the bar graphs, the filter includes a date range and a set of peaks that are commercial peaks
    Filter the dataframe by the filter and create a dictionary to uniformly color the peaks with the same set of colors
    :param date_range: Date range slider tuple
    :param success_only: filter only for termination reason = success. Do not filter otherwise
    :return: filtered dataframe and a color dictionary for the commercial peaks  
    """
    if success_only:
        df = success_exped_commercial_type_df
    else:
        df = all_exped_commercial_type_df
    selected_years_df = df[(df['YEAR'] >= date_range[0])
                           & (df['YEAR'] <= date_range[1])
                           & (df['PKNAME'] == chosenpeak)
                           ].copy()
    selected_years_df = selected_years_df.sort_values(['YEAR'])
    selected_years_df['YEAR'] = selected_years_df['YEAR'].astype('str')

    return selected_years_df


def create_dist_chart_figure(selected_years_df, y_col: str, y_col_title: str, histfunc:str):
    """
    This function 
    :param selected_years_df: filtered dataframe
    :param final_colors_dict: dictionary of colors for commercial peaks
    :param y_col: column value to be plotted in bar graph
    :param y_col_title: 
    :return: 
    """

    fig = px.histogram(selected_years_df,
                 x="YEAR",
                 y=y_col,
                 histfunc=histfunc,
                 color="COMRTE",
                 facet_col='COMRTE',
                 marginal="violin",
                 hover_data=['YEAR', 'O2USED', 'COMRTE', 'HEIGHTM'],
                 labels={'YEAR': 'Expedition Year',
                         'O2USED': 'Oxygen used during expedition',
                         'COMRTE': "Commercial Route",
                         "MDEATHS": "Member Deaths",
                         "TOTDAYS": "Total days of expeditions",
                         "SMTDAYS": "Days to summit",
                         "HDEATHS": "Hired Deaths",
                         "NUM_CAMPS": "Number of camps",
                         "PKNAME": "Peak Name"
                         },
                 color_discrete_map={'False': TIME_SERIES_COLOR_DICT["color_ochre_1"],
                                     'True': COLOR_CHOICE_DICT["mountain_side_blue_green"],
                                     },
                 )

    fig = common_layout_elements(fig)
    return fig


def common_layout_elements(fig):
    """
    Set background and legend elements for chart
    :param fig: Plotly Dash figure
    :return:
    """
    year_array = [str(year) for year in range(1920, 2030, 1)]
    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_layout(xaxis=dict(title=''), yaxis=dict(title=''), )
    fig.update_layout(showlegend=True,
                      xaxis={'categoryarray': year_array},
                      legend=dict(
                          title_font_family='Arial',
                          font=dict(
                              size=8
                          )
                      ))

    #"https://towardsdatascience.com/histograms-with-plotly-express-complete-guide-d483656c5ad7"
    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False, )
    fig.update_traces(opacity=0.8)
    return fig


@callback(Output("oxygen_usage_distrib_chart", "figure"),
          [Input('year_slider', 'value'),
           Input('peak_selection_dropdown', 'value'),
           Input('toggle_success_exped', 'value')]
          )
def update_chart(date_range, chosenpeak, success_only):
    selected_years_df = common_df_setup(date_range, chosenpeak, success_only)
    fig = create_dist_chart_figure(selected_years_df, y_col="O2USED",
                                   y_col_title="Oxygen Usage", histfunc='count')
    fig = common_layout_elements(fig)

    return fig


@callback(Output("member_deaths_distrib_chart", "figure"),
          [Input('year_slider', 'value'),
           Input('peak_selection_dropdown', 'value'),
           Input('toggle_success_exped', 'value')],
          )
def update_chart(date_range, chosenpeak, success_only):
    selected_years_df = common_df_setup(date_range, chosenpeak, success_only)
    fig = create_dist_chart_figure(selected_years_df, y_col="MDEATHS",
                                   y_col_title="Member Deaths", histfunc='avg')
    fig = common_layout_elements(fig)

    return fig


@callback(Output("hired_deaths_distrib_chart", "figure"),
          [Input('year_slider', 'value'),
           Input('peak_selection_dropdown', 'value'),
           Input('toggle_success_exped', 'value')],
          )
def update_chart(date_range, chosenpeak, success_only):
    selected_years_df = common_df_setup(date_range, chosenpeak, success_only)
    fig = create_dist_chart_figure(selected_years_df, y_col="HDEATHS",
                                   y_col_title="Hired Deaths", histfunc = 'avg')
    fig = common_layout_elements(fig)

    return fig


@callback(Output("total_base_camps_distrib_chart", "figure"),
          [Input('year_slider', 'value'),
           Input('peak_selection_dropdown', 'value'),
           Input('toggle_success_exped', 'value')],
          )
def update_chart(date_range, chosenpeak, success_only):
    selected_years_df = common_df_setup(date_range, chosenpeak, success_only)
    fig = create_dist_chart_figure(selected_years_df, y_col="NUM_CAMPS",
                                   y_col_title="Number of camps", histfunc = 'avg')
    fig = common_layout_elements(fig)

    return fig


@callback(Output("total_exped_days_distrib_chart", "figure"),
          [Input('year_slider', 'value'),
           Input('peak_selection_dropdown', 'value'),
           Input('toggle_success_exped', 'value')],
          )
def update_chart(date_range, chosenpeak, success_only):
    selected_years_df = common_df_setup(date_range, chosenpeak, success_only)
    fig = create_dist_chart_figure(selected_years_df, y_col="TOTDAYS",
                                   y_col_title="Total Expedition Days", histfunc='avg')
    fig = common_layout_elements(fig)

    return fig

@callback(Output("total_summit_days_distrib_chart", "figure"),
          [Input('year_slider', 'value'),
           Input('peak_selection_dropdown', 'value'),
           Input('toggle_success_exped', 'value')],
          )
def update_chart(date_range, chosenpeak, success_only):
    selected_years_df = common_df_setup(date_range, chosenpeak, success_only)
    fig = create_dist_chart_figure(selected_years_df, y_col="SMTDAYS",
                                   y_col_title="Days to Summit from Base Camp", histfunc='avg')
    fig = common_layout_elements(fig)

    return fig
