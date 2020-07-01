"""
This app creates a simple sidebar layout using inline style arguments and the
dbc.Nav component.

dcc.Location is used to track the current location. There are two callbacks,
one uses the current location to render the appropriate page content, the other
uses the current location to toggle the "active" properties of the navigation
links.

For more details on building multi-page Dash applications, check out the Dash
documentation: https://dash.plot.ly/urls
"""
import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import base64
import dash_table
from gensim.models import CoherenceModel, TfidfModel
import pandas as pd
import src.situ_helper as situ 
import numpy as np
import flask
import spacy
from spacy import displacy
from spacy.pipeline import EntityRuler

img1 = 'notebook/img/type_inertias.PNG'
img1_enc = base64.b64encode(open(img1, 'rb').read()).decode('ascii')

image_directory = 'img/flowcharts/'
static_image_route = '/static/'

sop_dir="/Users/Public/Desktop/SOPs/"

print('Prepare for cross-situation clusters...')
situ_clusters = pd.read_csv(
    'data/interim/situ_topics_kmeans_tfidf.csv',
    keep_default_na=False,
    converters={'sop': eval, 'situ_lst': eval}
    )
cols = list(situ_clusters.columns)
cols.remove('situ_lst')
situ_search_docs = situ_clusters.apply(lambda x: x['sop'] + x['situ_lst'], axis = 1).tolist()
situ_bow, situ_corpus, situ_dict = situ.get_dct_dtmatrix(situ_search_docs)
tfidf_situ = TfidfModel(situ_bow)
tfidf_mtx_situ = situ.bow2tfidf(situ_bow, tfidf_situ)
print('Done!')

print('Prepare for cross-type clusters...')
type_clusters = pd.read_csv(
    'data/interim/type_topics_kmeans_tfidf.csv',
    keep_default_na=False,
    converters={'sop': eval, 'situ_lst': eval}
    )
type_display_cols = type_clusters.columns.tolist()
type_display_cols.remove('sop')
type_bow, type_corpus, type_dict = situ.get_dct_dtmatrix(type_clusters['sop'])
tfidf_type = TfidfModel(type_bow)
tfidf_mtx_type = situ.bow2tfidf(type_bow, tfidf_type)
print('Done!')

# app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.
CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("E-COMM 911", className="display-4"),
        html.Hr(),
        html.P(
            "Data Science can help save lives", className="lead"
        ),
        dbc.Nav(
            [
                dbc.NavLink("Cross-type", href="/cross-type", id="cross-type-link"),
                dbc.NavLink("Cross-situation", href="/cross-situ", id="cross-situ-link"),
                dbc.NavLink("Keyword Search", href="/search", id="search-link"),
            ],
            vertical=True,
            pills=True,
        ),
    ],
    style=SIDEBAR_STYLE,
)

cross_situation = [
    html.Div([
        html.H2('Cross-situation clusters'),
        html.Img(id = 'situ_cluster_img'),
        html.Div([
            html.P('Choose cross-situation cluster id:'),
            dcc.Slider(
                id = 'n_cluster',
                min = 0,
                max = 189,
                step = 1,
                marks = {int(i): str(int(i)) for i in range(190) if i % 10 == 0},
                value = 0,
                tooltip = {'always_visible': True, 'placement': 'topLeft'}
            )
        ], style = {'margin-bottom': '40px'}),
        dash_table.DataTable(
            id = 'situ_clusters', 
            columns = [{'name': i, 'id': i} for i in cols],
            style_cell = {
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ),
    ], style = {'width': '70%', 'margin-bottom': '20px', 'margin-top': '40px', 
                'background-color': '#d6e5d7'})
]

cross_type = [
    html.Div([
        html.H2('Cross-type clusters'),
        html.Img(id = 'type_cluster_img'),
        html.Div([
            html.P('Choose cross-type cluster id:'),
            dcc.Slider(
                id = 'type_n_cluster',
                min = 0,
                max = 86,
                step = 1,
                marks = {int(i): str(int(i)) for i in range(87) if i % 5 == 0},
                value = 12,
                tooltip = {'always_visible': True, 'placement': 'topLeft'}
            )
        ], style = {'margin-bottom': '40px'}),
        dash_table.DataTable(
            id = 'type_clusters', 
            columns = [{'name': i, 'id': i} for i in type_display_cols],
            style_cell = {
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        )
    ], style = {'width': '70%', 'margin-bottom': '20px', 'margin-top': '40px', 
                'background-color': '#9addf4'})
]

search = [
    html.Div([
        html.Div([
            html.H2('Search for call taker SOPs'),
            dcc.Input(
                id = 'query',
                type = 'search',
                placeholder = 'Enter search keywords here',
                size = '60',
                debounce = True
            ),
            html.P(''),
            html.P('Choose number of rows to display'),
            dcc.Slider(
                id = 'n_rows',
                min = 1,
                max = 20,
                step = 1,
                marks = {int(i): str(int(i)) for i in range(21) if i % 5 == 0},
                value = 3,
                tooltip = {'always_visible': True, 'placement': 'left'}
            )
        ], style = {'margin-bottom': '40px'}),
        html.Hr(),
        html.Div([
            html.P('Search in situations'),
            dash_table.DataTable(
                id = 'situ_query', 
                columns = [{'name': i, 'id': i} for i in cols],
                style_cell = {
                    'whiteSpace': 'normal',
                    'height': 'auto'
                }
            ),
            html.Ul(id = 'situ-query-list'),
            html.Hr(),
            html.P('Search in SOPs'),
            dash_table.DataTable(
                id = 'type_query', 
                columns = [{'name': i, 'id': i} for i in type_display_cols],
                style_cell = {
                    'whiteSpace': 'normal',
                    'height': 'auto'
                }
            ),
            html.Ul(id = 'type-query-list')
        ])
    ], style = {'width': '70%', 'margin-bottom': '20px', 'margin-top': '80px', 
                'background-color': '#e6e6fa'})
]

content = html.Div(id="page-content", style=CONTENT_STYLE)

app.layout = html.Div([dcc.Location(id="url"), sidebar, content])

tabs = ['cross-type', 'cross-situ', 'search']
# this callback uses the current pathname to set the active state of the
# corresponding nav link to true, allowing users to tell see page they are on
@app.callback(
    [Output(f"{tab}-link", "active") for tab in tabs],
    [Input("url", "pathname")],
)
def toggle_active_links(pathname):
    if pathname == "/":
        # Treat cross-type as the homepage / index
        return True, False, False
    return [pathname == f"/{tab}" for tab in tabs]


@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname in ["/", "/cross-type"]:
        return cross_type
    elif pathname == "/cross-situ":
        return cross_situation
    elif pathname == "/search":
        return search
    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


@app.callback(
    Output(component_id='type_clusters', component_property='data'),
    [Input(component_id = 'type_n_cluster', component_property='value')]
)
def display_type_df(n_cluster):
    return type_clusters[type_clusters['cluster'] == n_cluster].to_dict(orient = 'records')

@app.callback(
    dash.dependencies.Output('type_cluster_img', 'src'),
    [dash.dependencies.Input('type_n_cluster', 'value')])
def update_type_image(n_cluster):
    return static_image_route + f"type_cluster_{n_cluster}.png"

@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    return flask.send_from_directory(image_directory, image_name)


@app.callback(
    Output(component_id='situ_clusters', component_property='data'),
    [Input(component_id = 'n_cluster', component_property='value')]
)
def display_situ_df(n_cluster):
    return situ_clusters[situ_clusters['cluster'] == n_cluster].to_dict(orient = 'records')

@app.callback(
    dash.dependencies.Output('situ_cluster_img', 'src'),
    [dash.dependencies.Input('n_cluster', 'value')])
def update_situ_image(n_cluster):
    return static_image_route + f"situ_cluster_{n_cluster}.png"


@app.callback(
    Output(component_id='situ_query', component_property='data'),
    [Input(component_id = 'query', component_property='value'),
    Input(component_id = 'n_rows', component_property='value')]
)
def query_situ(query, nrows):
    if query is None:
        query = ''
    query_result = situ.query_situation(query, tfidf_situ, situ_dict, tfidf_mtx_situ, situ_clusters, nrows).drop(columns = 'situ_lst')
    # query_result = situ_clusters.iloc[nrows : nrows+6].copy()
    return query_result.to_dict(orient = 'records')

@app.callback(
    Output(component_id='type_query', component_property='data'),
    [Input(component_id = 'query', component_property='value'),
    Input(component_id = 'n_rows', component_property='value')]
)
def query_type(query, nrows):
    if query is None:
        query = ''
    query_result = situ.query_situation(query, tfidf_type, type_dict, tfidf_mtx_type, type_clusters, N = nrows)
    # query_result = type_clusters.iloc[nrows : nrows+6].copy()
    return query_result.to_dict(orient = 'records')

@app.server.route('/sop/<sop_name>')
def download_sop(sop_name):
    return flask.send_from_directory(sop_dir, sop_name, 
        mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')

def sop_link(sop_name):
    location = f'/sop/{sop_name}'
    return html.A(sop_name, href = location)

@app.callback(
    Output('situ-query-list', 'children'),
    [Input('situ_query', 'data')]
)
def update_situlist(df_record):
    return [html.Li(sop_link(dct['filename'])) for dct in df_record]

@app.callback(
    Output('type-query-list', 'children'),
    [Input('type_query', 'data')]
)
def update_typelist(df_record):
    return [html.Li(sop_link(dct['filename'])) for dct in df_record]

if __name__ == "__main__":
    app.run_server(port=8686)