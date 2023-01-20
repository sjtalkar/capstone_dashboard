import sys

sys.path.append("..")

import os
import dash
import plotly.express as px

from color_theme.color_dicts import COLOR_CHOICE_DICT
import dash_bootstrap_components as dbc
from dash import dcc, html, Output, callback, Input
from lib.data_preparation.peaks_data import PeakExpedition
# Place this in the home page
import plotly.graph_objects as go

fig = go.Figure(layout=dict(template='plotly'))

dash.register_page(__name__, title='Peak Commercial Expedition Analysis', name='Peak Commercial Expedition Analysis')

# print(f"This is the current directory : {os.path.abspath(os.getcwd())}")
peak_expedition = PeakExpedition(os.path.join('app', 'data', 'raw_data'), os.path.join('app', 'data', 'nhpp'))
commerce_noncommerce_by_year_df, commerce_peaks_list = peak_expedition.create_commerce_noncommerce_peak_aggregation(
    by_season=False)
commerce_noncommerce_by_year_df = commerce_noncommerce_by_year_df.fillna(0)

min_year = commerce_noncommerce_by_year_df['YEAR'].min()
max_year = commerce_noncommerce_by_year_df['YEAR'].max()
all_peaks_list = list(commerce_noncommerce_by_year_df['PEAKID'].unique())

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
        dbc.Row([dbc.Col([html.Label("Average Number Of Base Camps By Year"),
                          dcc.Graph(id="base_camps_chart", className="rounded shadow")
                          ],
                         width=4, className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"),
                 dbc.Col([html.Label("Average Number of Commercial Expeditions By Year"),
                          dcc.Graph(id="commerce_expeds_chart", className="rounded shadow")
                          ],
                         width=4, className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"),
                 dbc.Col([html.Label("Average Number of Days To Summit By Year"),
                          dcc.Graph(id="summit_days_chart", className="rounded shadow")
                          ],
                         width=4, className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"),
                 ]),
        dbc.Row([html.Div(className='m-4')]),
        dbc.Row([dbc.Col([html.Label("Total Number Of Base Camps By Year"),
                          dcc.Graph(id="total_base_camps_chart", className="rounded shadow")
                          ],
                         width=4, className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"),
                 dbc.Col([html.Label("Total Number of Commercial Expeditions By Year"),
                          dcc.Graph(id="total_commerce_expeds_chart", className="rounded shadow")
                          ],
                         width=4, className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"),
                 dbc.Col([html.Label("Total Number Of Days Taken By All Expeditions To Summit By Year"),
                          dcc.Graph(id="total_summit_days_chart", className="rounded shadow")
                          ],
                         width=4, className="rounded shadow rounded-top  rounded-end rounded-bottom rounded-start"),
                 ]),
        dbc.Row([html.Div(className='m-4')]),
    ])


def common_df_setup(date_range):
    selected_years_df = commerce_noncommerce_by_year_df[
        (commerce_noncommerce_by_year_df[
             'YEAR'] >= date_range[0])
        & (commerce_noncommerce_by_year_df[
               'YEAR'] <= date_range[1])
        & (commerce_noncommerce_by_year_df['PKNAME'].isin(
            commerce_peaks_list))].copy()
    selected_years_df['YEAR'] = selected_years_df['YEAR'].astype('str')
    # melt_selected_years_df = selected_years_df.melt(
    #     id_vars=['YEAR', 'PEAKID', 'PKNAME', 'HEIGHTM', 'EXPEDITIONS_COUNT'],
    #     value_vars=['COMMERCIAL_ROUTES_MEAN', 'SUMMIT_DAYS_MEAN', 'NUM_CAMPS_MEAN'])
    final_colors_dict = {key: COLOR_CHOICE_DICT[value] for key, value in zip(list(selected_years_df['PKNAME'].unique()),
                                                                             ["mountain_cloud_blue",
                                                                              "parallel_theme_blue",
                                                                              "mountain_side_blue_green",
                                                                              "spruce_green_light",
                                                                              "spruce_green",
                                                                              ])}
    return selected_years_df, final_colors_dict


def create_average_figure(selected_years_df, final_colors_dict,y_col:str, y_col_title:str):
    fig = px.bar(selected_years_df,
                 x='YEAR',
                 y=y_col,
                 color='PKNAME',
                 color_discrete_map=final_colors_dict,
                 labels={
                     "PKNAME": "Peak Name",
                     y_col:y_col_title,
                     "YEAR": "Year",
                     "HEIGHTM": "Height in meters",
                     "EXPEDITIONS_COUNT": "Number of Expeditions"
                 },
                 hover_data=["YEAR", "PKNAME", "HEIGHTM", "EXPEDITIONS_COUNT", y_col ]

                 )
    fig = common_layout_elements(fig)
    return fig



def common_layout_elements(fig):
    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    fig.update_layout(xaxis=dict(title=''), yaxis=dict(title=''))

    fig.update_yaxes(showgrid=False)
    fig.update_xaxes(showgrid=False)
    fig.update_traces(opacity=0.8)
    return fig



@callback(Output("commerce_expeds_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_line_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(date_range)
    fig = create_average_figure(selected_years_df, final_colors_dict, y_col="COMMERCIAL_ROUTES_MEAN",
                                y_col_title="Average number of commercial routes")
    fig = common_layout_elements(fig)

    return fig


@callback(Output("summit_days_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_line_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(date_range)
    fig = create_average_figure(selected_years_df, final_colors_dict, y_col="SUMMIT_DAYS_MEAN",
                                y_col_title="Average number of days to Summit")
    fig = common_layout_elements(fig)
    return fig


@callback(Output("base_camps_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_line_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(date_range)
    fig = create_average_figure(selected_years_df, final_colors_dict, y_col="NUM_CAMPS_MEAN",
                                y_col_title="Average Number of Camps")
    fig = common_layout_elements(fig)
    return fig



@callback(Output("total_summit_days_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_line_chart(date_range):
    selected_years_df, final_colors_dict= common_df_setup(date_range)
    fig = create_average_figure(selected_years_df, final_colors_dict, y_col="SUMMIT_DAYS_COUNT",
                                y_col_title="Total number of days to Summit")
    fig = common_layout_elements(fig)
    return fig


@callback(Output("total_commerce_expeds_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_line_chart(date_range):
    selected_years_df, final_colors_dict= common_df_setup(date_range)
    fig = create_average_figure(selected_years_df, final_colors_dict, y_col="COMMERCIAL_ROUTES_COUNT",
                                y_col_title="Total number of commercial routes")
    fig = common_layout_elements(fig)

    return fig


@callback(Output("total_base_camps_chart", "figure"),
          [Input('year_slider', 'value')],
          )
def update_line_chart(date_range):
    selected_years_df, final_colors_dict = common_df_setup(date_range)
    fig = create_average_figure(selected_years_df, final_colors_dict, y_col="NUM_CAMPS_COUNT",
                                y_col_title="Total Number of Camps")
    fig = common_layout_elements(fig)
    return fig



