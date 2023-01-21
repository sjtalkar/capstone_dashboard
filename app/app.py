import sys
sys.path.append("..")

import dash
import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
from color_theme.color_dicts import COLOR_CHOICE_DICT

app = dash.Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.MORPH])
#Either morph or slate template

def make_empty_row(example_class_name):
    return dbc.Row(
        [
            dbc.Col(html.Div("", className="bg-dark")),
        ],
        className=example_class_name + " my-2 border",
    )

asset_url = dash.get_asset_url('pexels-ashok-sharma-11595461-cropped.jpg')
#print(f"Location of icon  image {asset_url}")

navbar = dbc.NavbarSimple(

    dbc.Row([
        dbc.Col([html.A(
            # Use row and col to control vertical alignment of logo / brand
            dbc.Row(
                [
                    dbc.Row([html.Img(src=asset_url, height="80px")],
                            ),
                    dbc.Row([html.H5("Himalayan Dataset Spring 2022", style={'color': '#c26a2d'})],
                            class_name='fst-italic'),
                  ],
                align="left",
                className="rounded shadow"
            ),
            href="",
            style={"textDecoration": "none"},
        ),
        ], width=10),

        dbc.Col([dbc.DropdownMenu(
            [
                dbc.DropdownMenuItem(page["name"], href=page["path"])
                for page in dash.page_registry.values()
                if page["module"] != "pages.not_found_404"
            ],
            nav=True,
            label="More Pages",
        )],width=2)
       ]),

    #brand="Himalayan Dataset Spring 2022",
    color=COLOR_CHOICE_DICT["dasboard_title_green"],
    dark=True,
    className="mb-2 shadow rounded",
)


#This layout must be in the main app.py file. Each page has either a function or a variable called layout as well
app.layout = dbc.Container(
    [make_empty_row("gx-2")
      ,navbar
     ,dash.page_container
     ,make_empty_row("gx-2")],
     fluid=True,
)

if __name__ == "__main__":
    #To run in Docker, set host
    #app.run_server(host="0.0.0.0", debug=True)
    #To run on local host
    app.run_server(host="127.0.0.1", debug=True)
