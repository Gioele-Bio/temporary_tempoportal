import dash
from dash import html, dcc, callback, Input, Output, State
from ...components import DataTableAIO, SampleSelectorAIO, redis_store, GraphXYSelectorAIO
import pandas as pd
from io import StringIO
from base64 import b64decode
import pandas as pd
import plotly.express as px


def line_plot_layout():
    return [html.Div(
        dcc.Markdown('### Looks like no data was uploaded, please upload a count table from the "Upload data" page'),
        id='line_plot_main_div'),
        html.Div(id='line_plot_div')
        ]


# Gets the data from the selection, sets the selector 
@callback(
    Output('line_plot_main_div', 'children'),
    Input('storageQC', 'data'),
    prevent_initial_call=True
)
def get_data(data):
    #print('\n\n\n this callback called \n\n\n')
    #print(data)
    #df = redis_store.load(data['df'])
    # get selection only from selected samples
    #selection = [x['name'] for x in data['all_columns']]
    # Account for spelling variations
    geneID = [x['name'] for x in data['all_columns'] if x['name'] in ['Geneid', 'GeneID', 'geneid']]
    selection = geneID + data['selected']

    # Display graph with pre-selected cols
    # Display cols selector
    #graph = px.scatter(df, x=df.columns[0], y=df.columns[1])

    layout = GraphXYSelectorAIO(selection, aio_id='line_plot_selector')
    

    return layout



# Change selection + plot data
@callback(
    Output('line_plot_div', 'children'),
    Input(GraphXYSelectorAIO.ids.selectionStore('line_plot_selector'), 'data'),
    State('storageQC', 'data'),
    prevent_initial_call = True,
    suppress_callback_exceptions=True
)
def refresh_graph(selection, store):
    x_sel = selection['x']
    y_sel = selection['y']

    # if 'GeneID' change it to unnamed to be consistent with df
    # x_sel = 'Unnamed: 0' if x_sel == 'GeneID' else x_sel

    # y_sel = 'Unnamed: 0' if y_sel == 'GeneID' else y_sel

    df = redis_store.load(store['df'])
    graph = px.scatter(df, x=x_sel, y=y_sel)
    return dcc.Graph(figure=graph)


# OKK you're able to get the store from the upload page, you need to 
# - GET the df!! (maybe pass it to the store from the upload page!
# - Display graph!
# - Handle if nothing is selected/uploaded, i'd say do a dcc.location to redirect to upload if anything#
