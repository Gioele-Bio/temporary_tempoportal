import dash
from dash import html, dcc, callback, Input, Output, State, callback_context
from ...components import DataTableAIO, SampleSelectorAIO, redis_store
import pandas as pd
from io import StringIO
from base64 import b64decode
import pandas as pd
# This is the main page that renders for uploading the page in QC 
#from .._DataTableSelectColsAIO import DataTableSelectColsAIO


# Page has: 
# Select files or upload section
# Show the count table section#

df = pd.read_csv('./dash_app/utils/components/qc_subpages/gio_try_1_gene_counts2.csv')

def upload_page_layout():
    return html.Div(
        [
            # Section to select file or upload data
            html.Div(
                [
                    html.Div([
                        
                        dcc.Upload(
                            id='qc_upload_data',
                            children=html.Div([
                                'Drag and Drop or ', html.A('Select Files')
                            ],style={
                                'width': '90%',
                                'height': '6rem',
                                'lineHeight': '6rem',
                                'borderWidth': '0.1rem',
                                'borderStyle': 'dashed',
                                'borderRadius': '0.5rem',
                                'textAlign': 'center',
                                'margin': '1rem',
                                'alignItems': 'center'
                            })
                        ),
                    ], className='five columns'),

                    dcc.Markdown('##### or', 
                    className='one column'),
                    
                    # div for dropdown
                    html.Div([

                        dcc.Dropdown(
                            ['selectme'],
                            placeholder='Select your files from server'
                        )
                    ]
                    , 
                    className='six columns',
                    style={'padding': 'auto'}
                    
                    ),
                ], className='row', style={'alignItems': 'center'}
            ),


            # Section with the uploaded table
            html.Div([
            ], id='data_table_aio_div'),
            
            # NEW ATTEMPT
            html.Div([
                DataTableAIO(df, aio_id='datatable_qc_upload'),
                SampleSelectorAIO(selection=[x for x in df.columns], selected=[x for x in df.columns if x != 'GeneID'], aio_id='sample_selector_upload')
            ], id='quality_control_data_table_holder'),



            # OLD ATTEMPT
            # html.Div([
            #     dcc.Markdown('# THIS IS A BETA, TRY TO ADD THE CHECKMARKS FOR SELECTING COLUMNS!!!!!!!!!!'),
            #     SampleSelectorAIO(selection=[x for x in df.columns], #selected=['Sample1', 'Sample8','Sample2', 'Sample3', 'Sample4', 'Sample5', 'Sample6', 'Sample7', 'Sample9', 'Sample10', 'Sample11', 'Sample12', 'Sample13', 'Sample14', 'Sample15', 'Sample16']
            #                       ),
            #     DataTableAIO(df, aio_id='datatable_aio_upload'),
            #     html.Div(id='placeholder')
            # ])

            

            
        ]
    )

### NEW CALLBACKS


# NEED TO LINK SAMPLE SELECTOR and DATA TABLE TO GENERIC STORE!!



#Gets data from upload and loads it into the page
@callback(
    Output('quality_control_data_table_holder', 'children', allow_duplicate=True),
    # Get the other input from the dropdown
    Input('qc_upload_data', 'contents'),
    State('qc_upload_data', 'filename'),
    prevent_initial_call = True,
    
)
def handle_upload_qc_template(content, filename):
    # Handle file
    content_type, content_string = content.split(',')
    decoded_content = b64decode(content_string)
    file_content = StringIO(decoded_content.decode('utf-8')).readlines()


    # File, read it in with pandas and get the tables
    file_string = ''.join(file_content)
    # Read file in with pandas
    df = pd.read_csv(StringIO(file_string))
    # Handle Unnamed: 0 on upload
    if 'Unnamed: 0' in df.columns:
        df = df.rename({'Unnamed: 0': 'GeneID'}, axis=1)
    if 'GeneID' not in df.columns:
        return dcc.ConfirmDialog(message='This file doesnt have a GeneID field', displayed=True)

    # Sanity check on file
    # TO DO!!!!!!!!!!!!!!!


    # MIGHT BE WISE TO REMOVE PREFIX SUFFIX as TABLE TAKES TOO MUCH SPACE


    # THIS RETURNS THE WHOLE DATA TABLE AS A NEW COMPONENT; I BELIEVE IS EASIER ESPECIALLY SO YOU DONT HAVE TO UPDATE THE STORE, IF YOU FIND A BETTER SOLUTION PLS CHANGE IT
    
    return [DataTableAIO(df, aio_id='datatable_qc_upload'),
            SampleSelectorAIO(selection=[x for x in df.columns], selected=[x for x in df.columns if x != 'Unnamed: 0'], aio_id='sample_selector_upload')]



# THIS IS FINE!!
# Transfers store from the selection store to the storageQC store (generic store for quality control)
@callback(
    Output(DataTableAIO.ids.selection_store('datatable_qc_upload'), 'data'),
    Output('storageQC', 'data', allow_duplicate=True),
    Input(SampleSelectorAIO.ids.store_selection('sample_selector_upload'), 'data'),
    #Input('storageQC', 'data'),
    State(DataTableAIO.ids.selection_store('datatable_qc_upload'), 'data'),
    State(DataTableAIO.ids.store('datatable_qc_upload'), 'data'),
    prevent_initial_call = 'initial_duplicate',
    # suppress_callback_exceptions=True
    )
def transfer_store(sample_selection, data_table_store, df_store):
    # print('After upload, this is called')
    # print('sample',sample_selection, '\n\n\nstore', data_table_store, '\n\n\ndf', df_store)
    # trigger = callback_context.triggered[0]['prop_id']
    # This means that the store was updated in another tab, need to reflect it into the selection store
    # if trigger == 'storageQC.data':
    #     print('QCDATA TRIGGERED \n\n')
    #     #print(storage_qc)
    #     #print('SAMPLESELECTION NOT MODIFIED', sample_selection)
    #     sample_selection['selected'] = storage_qc['selected']
    #     #print('SAMPLESELECTION',sample_selection)
        
    #     return sample_selection, storage_qc
    
    data_table_store['selected'] = sample_selection['selected']
    data_table_store['df'] = df_store['df']
    #print('datatablestore_______', data_table_store)
    return data_table_store, data_table_store




# Callback checks on storage_qc, if it's updated, it updates the store selection
@callback(
    Output('quality_control_data_table_holder', 'children', allow_duplicate=True),
    Input('storageQC', 'data'),
    State(SampleSelectorAIO.ids.store_selection('sample_selector_upload'), 'data'),
    prevent_initial_call=True
)
def update_upload_page_selection(storage, selection):
    # If the selection hasn't changed, prevent the update
    if selection['selected'] == storage['selected']:
        raise dash.exceptions.PreventUpdate()
    else:
        # If the selection has changed, return the datatable and sample selector
        # (This solution is not the nicest, and with larger tables might consume more memory than needed, change it if you find a way to not overlap wildcards)
        df = redis_store.load(storage['df'])    
        return [DataTableAIO(df, aio_id='datatable_qc_upload'),
                SampleSelectorAIO(selection=selection['options'], selected=storage['selected'], aio_id='sample_selector_upload')]




# # -----------------
# ### OLD CALLBACKS


# # Callback to re-send the datatable
# @callback(
#         Output('placeholder', 'children'),
#         Input(DataTableAIO.ids.store('datatable_aio_upload'), 'modified_timestamp'),
#         Input(DataTableAIO.ids.store('datatable_aio_upload'), 'data')
# )
# def handle_store(timestamp, table_store):
#     # print(timestamp, table_store)
#     # print(redis_store.load(table_store['df']))

#     return SampleSelectorAIO(store=table_store)
#     pass


# # Callback to bind the sample selector store to the quality control one! (From upper level)




# @callback(
#     Output('data_table_aio_div', 'children'),
#     # Get the other input from the dropdown
#     Input('qc_upload_data', 'contents'),
#     State('qc_upload_data', 'filename'),
#     prevent_initial_call = True
# )
# def handle_upload_qc_template(content, filename):
#     # Handle file
#     content_type, content_string = content.split(',')
#     decoded_content = b64decode(content_string)
#     file_content = StringIO(decoded_content.decode('utf-8')).readlines()


#     # File, read it in with pandas and get the tables
#     file_string = ''.join(file_content)
#     # Read file in with pandas
#     df = pd.read_csv(StringIO(file_string))

#     # Sanity check on file
#     # TO DO!!!!!!!!!!!!!!!


#     # MIGHT BE WISE TO REMOVE PREFIX SUFFIX as TABLE TAKES TOO MUCH SPACE


#     # THIS RETURNS THE WHOLE DATA TABLE AS A NEW COMPONENT; I BELIEVE IS EASIER ESPECIALLY SO YOU DONT HAVE TO UPDATE THE STORE, IF YOU FIND A BETTER SOLUTION PLS CHANGE IT


#     return DataTableAIO(df)
