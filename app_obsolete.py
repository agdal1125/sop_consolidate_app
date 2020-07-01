import os
import base64
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output 
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
curr_dir = os.getcwd()

image_directory = 'img/flowcharts/'
# list_of_images = [os.path.basename(x) for x in glob.glob('{}*.png'.format(image_directory))]
static_image_route = '/static/'

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



# Entity Extraction/Recognition





# APP
app = dash.Dash(__name__, assets_folder = 'assets')

server = app.server 

app.title = 'SOP clustering and searching'

app.layout = html.Div([
    html.H1('SOP clustering and searching for call takers'),
    
    html.Div([
        html.H2('Cross-situation clusters'),
        html.Img(id = 'situ_cluster_img'),
        html.P('Choose cross-situation cluster id:'),
        dcc.Slider(
            id = 'n_cluster',
            min = 0,
            max = 189,
            step = 1,
            marks = {int(i): str(int(i)) for i in np.linspace(0, 189, 20, endpoint = True)},
            value = 0,
            tooltip = {'always_visible': True, 'placement': 'topLeft'}
        ),
        dash_table.DataTable(
            id = 'situ_clusters', 
            columns = [{'name': i, 'id': i} for i in cols],
            style_cell = {
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ),
    ], style = {'width': '70%', 'margin-bottom': '20px', 'margin-top': '40px', 
                'background-color': '#d6e5d7'}),

    html.Div([
        html.H2('Cross-type clusters'),
        html.Img(id = 'type_cluster_img'),
        html.P('Choose cross-type cluster id:'),
        dcc.Slider(
            id = 'type_n_cluster',
            min = 0,
            max = 86,
            step = 1,
            marks = {int(i): str(int(i)) for i in np.linspace(0, 86, 20, endpoint = True)},
            value = 0,
            tooltip = {'always_visible': True, 'placement': 'topLeft'}
        ),
        dash_table.DataTable(
            id = 'type_clusters', 
            columns = [{'name': i, 'id': i} for i in type_display_cols],
            style_cell = {
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ),
    ], style = {'width': '70%', 'margin-bottom': '20px', 'margin-top': '40px', 
                'background-color': '#9addf4'}),

    # html.Div([
    #     html.H3('Search for SOPs'),
    #     dcc.Input(
    #         id = 'query',
    #         type = 'search',
    #         placeholder = 'Enter search keywords here',
    #         size = '60'
    #     ),
    # ], style = {'fontColor': 'blue'}),
    html.Div([
        html.H2('Search for call taker SOPs'),
        dcc.Input(
            id = 'query',
            type = 'search',
            placeholder = 'Enter search keywords here',
            size = '60',
            debounce = True
        ),
        dcc.Slider(
            id = 'n_rows',
            min = 0,
            max = 20,
            step = 1,
            marks = {int(i): str(int(i)) for i in np.linspace(0, 20, 5, endpoint = True)},
            value = 3,
            tooltip = {'always_visible': True, 'placement': 'topLeft'}
        ),
        html.P('Search in situations'),
        dash_table.DataTable(
            id = 'situ_query', 
            columns = [{'name': i, 'id': i} for i in cols],
            style_cell = {
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ),
        html.P('Search in SOPs'),
        dash_table.DataTable(
            id = 'type_query', 
            columns = [{'name': i, 'id': i} for i in type_display_cols],
            style_cell = {
                'whiteSpace': 'normal',
                'height': 'auto'
            }
        ),
    ], style = {'width': '70%', 'margin-bottom': '20px', 'margin-top': '80px', 
                'background-color': '#e6e6fa'}),

    dcc.Markdown('''
            __This is bold face__  
            _This is italic_  
            > indentation
        '''),
    html.Img(src = f'data:image/png;base64,{img1_enc}')
])

@app.callback(
    Output(component_id='situ_clusters', component_property='data'),
    [Input(component_id = 'n_cluster', component_property='value')]
)
def display_situ_df(n_cluster):
    return situ_clusters[situ_clusters['cluster'] == n_cluster].to_dict(orient = 'records')

@app.callback(
    Output(component_id='type_clusters', component_property='data'),
    [Input(component_id = 'type_n_cluster', component_property='value')]
)
def display_situ_df(n_cluster):
    return type_clusters[type_clusters['cluster'] == n_cluster].to_dict(orient = 'records')

@app.callback(
    Output(component_id='situ_query', component_property='data'),
    [Input(component_id = 'query', component_property='value'),
    Input(component_id = 'n_rows', component_property='value')]
)
def query_sop(query, nrows):
    if query is None:
        query = ''
    query_result = situ.query_situation(query, tfidf_situ, situ_dict, tfidf_mtx_situ, situ_clusters, nrows).drop(columns = 'situ_lst')
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
    return query_result.to_dict(orient = 'records')

@app.callback(
    dash.dependencies.Output('situ_cluster_img', 'src'),
    [dash.dependencies.Input('n_cluster', 'value')])
def update_image_src(n_cluster):
    return static_image_route + f"situ_cluster_{n_cluster}.png"

@app.callback(
    dash.dependencies.Output('type_cluster_img', 'src'),
    [dash.dependencies.Input('type_n_cluster', 'value')])
def update_image_src(n_cluster):
    return static_image_route + f"type_cluster_{n_cluster}.png"

@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.png'.format(image_path)
    # if image_name not in list_of_images:
    #     raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(image_directory, image_name)

if __name__ == '__main__':
    app.run_server(debug = True)