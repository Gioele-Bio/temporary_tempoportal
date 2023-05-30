import dash
from dash import html, dcc, callback, Input, Output, State
from ...components import DataTableAIO, SampleSelectorAIO, redis_store, GraphXYSelectorAIO
import pandas as pd
from io import StringIO
from base64 import b64decode
import pandas as pd
import plotly.express as px


def bar_plot_layout():
    return [html.Div(
        dcc.Markdown('### Looks like no data was uploaded, please upload a count table from the "Upload data" page'),
        id='bar_plot_main_div'),
        html.Div(id='bar_plot_div')
        ]

# This is where you return the sample selector
@callback(
    Output('bar_plot_main_div', 'children'),
    Input('storageQC', 'data'),
    prevent_initial_call=True
)
def get_data(data):
    #print('\n\n\n this callback called \n\n\n')
    #print(data)
    #df = redis_store.load(data['df'])

    selection = [x['name'] for x in data['all_columns']]
    selected = data['selected']

    # Display graph with pre-selected cols
    # Display cols selector
    #graph = px.scatter(df, x=df.columns[0], y=df.columns[1])

    #layout = GraphXYSelectorAIO(selection, aio_id='bar_plot_selector')
    
    layout = SampleSelectorAIO(selection=selection, selected=selected, aio_id='bar_plot_selector')

    return layout


# This is where the data is actually plotted
@callback(
    Output('bar_plot_div', 'children'),
    Output('storageQC', 'data', allow_duplicate=True),
    Input(SampleSelectorAIO.ids.store_selection('bar_plot_selector'), 'data'),
    State('storageQC', 'data'),
    prevent_initial_call = 'initial_duplicate',
    #suppress_callback_exceptions=True
)
def refresh_bar_graph(selection, store):
    #print('store in',store)

    # Get df
    df = redis_store.load(store['df'])
    # Get sum as series
    res = df.sum()
    # Drop the geneid row and make it a DF
    res = res.drop('GeneID').to_frame('Count')
    # Add sample col from index
    res['Sample'] = res.index

    # Filter rows based on selection
    res = res.loc[res['Sample'].isin(selection['selected'])]

    # print(type(res), res)

    # graph = px.scatter(df, x=x_sel, y=y_sel)


    graph = px.bar(res, y='Count', x='Sample')

    store['selected'] = selection['selected']

    #print('store out',store)


    return dcc.Graph(figure=graph), store






# So basically what happens is:
# You cannot get the selection store from barplot to upload page
# You need to make sure the selection is resetted once the page is changed again (also that when the things are selected/unselected it gets refreshed and unselects everything)






