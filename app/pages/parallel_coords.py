import sys
sys.path.append("..")

import os
import dash
import pickle
import pandas as pd
import plotly.graph_objects as go
import dash_bootstrap_components as dbc
from dash import dcc, html, Input, Output, callback
from color_theme.color_dicts import COLOR_CHOICE_DICT
from lib.data_preparation.member_data import MemberInfo

dash.register_page(__name__, title='Member Analysis', name='Member Analysis',path = '/')

member_data = MemberInfo(data_path=os.path.join("app", "data", "raw_data", "members.csv"))
members_counts_df, members_norm_df = member_data.get_members_parallel_coord_data()

items = [dbc.DropdownMenuItem(x) for x in range(10, 50, 10)]
display_col_names = ['CITIZEN', 'CALCAGE_median', 'CALCAGE_min', 'CALCAGE_max', 'MEMBER_COUNT', 'LEADER', 'HIRED', 'WEATHER',
                     'INJURY', 'DEATH', 'MO2USED', 'MHIGHPT', 'BCONLY', 'MSOLO', 'FEMALE']
display_col_names_labels = ['Nationality', 'Median Analysis Age*', 'Lowest Analysis Age*', 'Highest Analysis Age*',
                            'Members', 'Leader', 'Hired', 'Deaths due to weather', 'Injured', 'Deaths', 'Oxygen used',
                            'High point reached', 'Base Camp Only', 'Solo Attempt', 'Women']

parallel_axis_display_dict = dict(zip(display_col_names, display_col_names_labels))

with open(os.path.join("app", "data", "dash", "store_data_lists.pickle"), 'rb') as handle:
    lists_dict = pickle.load(handle)
    all_peaks_list = lists_dict['all_peaks_list']
    countries_list = lists_dict['countries_list']

layout = html.Div([
    dbc.Row([
        dbc.Col([
            dbc.Row(
                [
                    dbc.Col(), dbc.Col(
                    dbc.RadioButton(id="show_normalized",
                                    label='Show Normalized Data',
                                    labelStyle="block",
                                    value=0,
                                    className="rounded shadow"

                                    ))
                ]),
            dbc.Row(
                [

                    dbc.Col(
                        [
                            html.P("Countries with most members:", className="m-0"),
                            dcc.Dropdown(id="num_countries_dropdown",
                                         options=[
                                             {"label": f"Display {num_countries} Countries", "value": num_countries} for
                                             num_countries in
                                             range(10, 50, 10)], value=10, clearable=False,
                                         className="rounded shadow mb-2")
                        ]
                    ),
                    dbc.Col(
                        [
                            html.P("Add Country:", className="m-0"),
                            dcc.Dropdown(id="add_countries_dropdown",
                                         options=[{"label": country, "value": country} for country in countries_list],
                                         multi=True,
                                         value=None,
                                         clearable=True,
                                         className="rounded shadow mb-2")
                        ]
                    ),

                ]),
        ]),

        dbc.Col([html.P("View Values For:", className="m-0"),
                 dcc.Dropdown(id="parallel_axis",
                              multi=True,
                              options=[{"label": parallel_axis_display_dict[col_name],
                                        "value": col_name} for col_name in
                                       parallel_axis_display_dict.keys()], value='CITIZEN',
                              clearable=False,
                              className="rounded shadow")
                 ])
    ]),
    dbc.Row(
        dcc.Graph(
            id="parallel_coords_axis",
            className="rounded shadow" )),
    dbc.Row([html.P(["* The calculated (analysis) age is used for all reports and analyses in the Himalayas dataset in which the climber’s age is a factor.",
                     html.Br(),
                     "It is calculated as of the date of Summit, Death, Base Camp Arrival Date or Season Start Date, whichever is best applicable"])],className="rounded shadow g-5 small fst-italic")
])


@callback(Output("parallel_coords_axis", "figure"),
          [Input("num_countries_dropdown", "value"),
           Input("show_normalized", "value"),
           Input("parallel_axis", "value"),
           Input("add_countries_dropdown", "value")
           ])
def update_parallel_coord_chart(num_countries, show_normalized, chosen_cols, chosen_additional_countries):

    if show_normalized:
        df = members_norm_df
    else:
        df = members_counts_df


    df = df.sort_values(by="MEMBER_COUNT", ascending=False).reset_index(drop=True).reset_index().rename(
        columns={'index': 'country_id'})
    add_countries_df = df.copy()
    df = df.iloc[:num_countries, :].copy()

    # If countries in addition to the ones in the top n are chosen then add data for that country as well
    if chosen_additional_countries is None:
        add_countries_df.drop(add_countries_df.index, inplace=True)
    elif not chosen_additional_countries in list(df['CITIZEN'].unique()):
        if isinstance(chosen_additional_countries, str):
            chosen_additional_countries = [chosen_additional_countries]
        add_countries_df = add_countries_df[add_countries_df['CITIZEN'].isin(chosen_additional_countries)]
        df = pd.concat([df, add_countries_df], axis="rows").drop(
            columns=['country_id']).reset_index().reset_index().drop(
            columns=['index']).rename(
            columns={'level_0': 'country_id'})

    else:
        add_countries_df.drop(add_countries_df.index, inplace=True)

    choose_cols = ['CITIZEN', 'country_id']

    if not (isinstance(chosen_cols, str) and chosen_cols == "CITIZEN"):
        for col_name in chosen_cols:
            if col_name not in choose_cols:
                choose_cols.append(col_name)

    df = df[choose_cols].copy()
    num_countries = len(list(df['country_id'].unique()))
    colors = [COLOR_CHOICE_DICT[key] for key in COLOR_CHOICE_DICT.keys()][:num_countries]



    dim_list = list([
        dict(range=(df['country_id'].max(),
                    df['country_id'].min()),
             tickvals=df['country_id'], ticktext=df['CITIZEN'],
             label='Country', values=df['country_id'])])


    for col_name in choose_cols:
        if col_name != 'CITIZEN' and col_name != 'country_id':
            dim_list.append(
                dict(range=(df[col_name].min(), df[col_name].max()),
                     label=parallel_axis_display_dict[col_name],
                     values=df[col_name]))

    fig = go.Figure(
        data=go.Parcoords(line=dict(color=df['country_id'],
                                    colorscale=colors, showscale=False),
                          dimensions=dim_list

                          )

    )
    fig.update_layout({'plot_bgcolor': "black",
                       "paper_bgcolor": "black",
                       "font": dict(color=COLOR_CHOICE_DICT["mountain_cloud_light_blue"])})

    return fig
