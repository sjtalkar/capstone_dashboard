import sys

sys.path.append("..")

import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Output, Input, callback
from color_theme.color_dicts import COLOR_CHOICE_DICT

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.MORPH])

##For Render: https://github.com/Coding-with-Adam/myrender-charmingdata-app/blob/main/src/app.py
server = app.server

# Either morph or slate template

def make_empty_row(example_class_name):
    return dbc.Row(
        [
            dbc.Col(html.Div("", className="bg-dark")),
        ],
        className=example_class_name + " my-2 border",
    )


asset_url = dash.get_asset_url('pexels-ashok-sharma-11595461-cropped.jpg')
# print(f"Location of icon  image {asset_url}")

navbar = dbc.NavbarSimple(

    dbc.Row([
        dbc.Col([html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Row([html.Img(src=asset_url, height="80px")],
                            ),
                    dbc.Row([html.H5(children=["Himalayan Dataset Spring 2022"], id="page_title",
                                     style={'color': '#c26a2d'})],
                            class_name='fst-italic'),
                ],
                align="left",
                className="rounded shadow"
            ),
            href="",
            style={"textDecoration": "none"},
        ),
        ], width=10),

        dbc.Col([
            dbc.Row([
                dbc.DropdownMenu(
                    [
                        dbc.DropdownMenuItem(page["name"], href=page["path"])
                        for page in dash.page_registry.values()
                        if page["module"] != "pages.not_found_404"
                    ],
                    nav=True,
                    label="More Pages",
                ), ]),
            #Empty row
            dbc.Row([html.Div(className='m-3')]),
            #Check this after making repo public
            dbc.Row([html.A(dbc.Button("Link to Insights ", title="Ctrl + Click for Insights",
                                       size='sm', color="info"),
                           # href="https://github.com/sjtalkar/capstone_dashboard/blob/main/docs/insights_from_eda.md"
                            href="https://dagshub.com/sjtalkar/capstone_himalayas/src/main/docs/insights_from_eda.md"
                            )
                     ]),

        ], width=2)
    ]),

    # brand="Himalayan Dataset Spring 2022",
    color=COLOR_CHOICE_DICT["dasboard_title_green"],
    dark=True,
    className="mb-2 shadow rounded",
)

# This layout must be in the main src.py file. Each page has either a function or a variable called layout as well
app.layout = dbc.Container(

    [
        # represents the browser address bar and doesn't render anything
        dcc.Location(id="url", refresh=False),
        make_empty_row("gx-2")
        , navbar
        , dash.page_container
        , make_empty_row("gx-2")
    ],
    fluid=True,
)


@callback(Output('page_title', 'children'),
          [Input('url', 'pathname')])
def display_page(pathname):
    title_string = "Himalayan Dataset Spring 2022"
    sub_title_string = "  (" + title_string + ")"
    if pathname == "/commerce-peak-distributions":
        page_name = "Distributions for Commercial versus Non-commercial Peaks" + sub_title_string
    elif pathname == "/parallel-coords" or pathname == "" or pathname == "/":
        page_name = " Members Analysis" + sub_title_string
    elif pathname == "/peak-commercial":
        page_name = " Commercial Peak Analysis" + sub_title_string
    elif pathname == "/topic-visualization":
        page_name = "Unsupervised Learning Topic Modeling" + sub_title_string
    elif pathname == "/peak-expeditions":
        page_name = "Peak Expedition Analysis" + sub_title_string
    elif pathname == "/spatial-analysis":
        page_name = "Geo-spatial Peak Analysis" + sub_title_string
    elif pathname == "/peak-routes":
        page_name = "Peak Route Analysis" + sub_title_string
    else:
        page_name = title_string

    return page_name


if __name__ == "__main__":
    # To run in Docker, set host
    #app.run_server(host="0.0.0.0", debug=True)
    # To run on local host
    #app.run_server(host="127.0.0.1", debug=True)
    #For Render Server
    app.run_server(debug=True)
