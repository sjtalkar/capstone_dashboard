import sys
sys.path.append("..")

import os
import dash
from dash import dcc, html, callback, Output, Input, State

dash.register_page(__name__)

file_path = os.path.join("..", "assets", "Everest_Visualization_Two_topics.html")
# Read the HTML file and store it in a variable

html_frame_content = html.Iframe(
            id = "iframe-1",
            src=file_path,
            className="vh-100 vw-100",
            style={"display": "none"}  #Initial
        )

layout = html.Div([
    html.Link(rel="preload", href=file_path),
    dcc.Loading(
        id="loading-1",
        children=[
            html.Iframe(
                id="iframe-1",
                src=file_path,
                className="vh-100 vw-100",
            )
        ],
        type="circle",
        fullscreen=True,
    ),
])

@callback(
    dash.dependencies.Output("iframe-1", "style"),
    [dash.dependencies.Input("iframe-1", "src")],
)
def show_iframe(srcDoc):
    return {"display": "block"}


