import sys

sys.path.append("..")

import os
import dash
from dash import dcc, html, callback

dash.register_page(__name__)

file_path = os.path.join("..", "assets", "Everest_Visualization_Two_topics.html")
# Read the HTML file and store it in a variable

html_frame_content = html.Iframe(
    id="iframe-1",
    src=file_path,
    className="vh-100 vw-100",
    style={"display": "none"}  # Initial
)

layout = html.Div([
    html.Link(rel="preload", href=file_path),
    html.Div([
        html.P(["The visualizations on this page take a long time to load."
                   , html.Br()
                   , "Please be patient and click 'Wait' if page becomes unreponsive"
                   , html.Br()
                ])

    ]),
    html.Div([
        html.P(["How to read the chart"
                   , html.Br()
                   ,
                "Click on each of terms to reveal the tweets that fed the classifier with the frequency of these terms."
                   , html.Br()
                   , html.Br()
                   , "Terms are colored by their association."
                   , html.Br()
                   ,
                "Terms that are most characteristic of the both sets of documents are displayed on the far-right of the visualization."
                   , html.Br()
                   , html.Br()
                   , "How is an association made between a word and a category?"
                   , html.Br()
                   ,
                "Associated terms have a relatively high category-specific precision and category-specific term frequency (i.e., % of terms in category are term). Take the harmonic mean of precision and frequency (both have to be high)"
                   , html.Br()
                   , html.Br()
                   , "Reading from the scattertext graph:"
                   , html.Br()
                   ,
                "The words 'determination' and 'abandon' feature high up to the left and close to the Everest Frequency axis.The top left quandrant also contains words such as challenging, mountain_conquer, leadership, die, planning, courage, achieve and names of peaks such as annapurna, camp, sherpa. The bottom right is as far away from expedition axis and contains words such as florida, rollercoaster, disneyworld and swimming."
                   , html.Br()
                   , html.Br()
                ]),
        html.P(["Credits:"]),
        html.A("ScatterText Documentation", href="https://github.com/JasonKessler/scattertext", target="_blank"),
        html.Br(),
        html.A("ScatterText Scaled F-Score",
                  href="https://github.com/JasonKessler/scattertext#understanding-scaled-f-score", target="_blank"),
    ]),
    dcc.Loading(
        id="loading-1",
        children=[
            html.Iframe(
                id="iframe-1",
                src=file_path,
                className="vh-100 vw-100",
            ),
        ],
        type="dot",
        color="#ac0b45",
        fullscreen=True,
    ),

])


@callback(
    dash.dependencies.Output("iframe-1", "style"),
    [dash.dependencies.Input("iframe-1", "src")],
)
def show_iframe(srcDoc):
    return {"display": "block"}
