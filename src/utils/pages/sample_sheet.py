import dash
from dash import html, dcc, callback, Input, Output, State
from ..components import genericCardWrapper, TextInputWrapperComponentAIO, SubmitButtonComponentAIO, ClickablePlateSelectionAIO, genericInputWrapper, CollapsableCardWrapperAIO, DataTableDisplay96WellAIO
import pandas as pd
from io import StringIO
from ..functions.dash_sample_sheet_functions import wrapper_make_template, wrapper_handle_upload, wrapper_create_complete_sample_sheet
import base64
import json



path = '/sample_sheet'

dash.register_page(__name__, 
    path=path, 
    name='Sample Sheet Generator', 
    order='a', 
    image='images/icons/sample_sheet_icon.png',
    ) 


# Functions to extract prefix and suffix from names
# Basically they both get a list of strings and iteratively check if these strings have the same character(s) to start/end with (eg set==1)
def common_prefix(lst):
    for s in zip(*lst):
        if len(set(s)) == 1:
            yield s[0]
        else:
            return

# This returns the string inverted
def common_suffix(lst):
    #invert words in list
    lst = [x[::-1] for x in lst]
    for s in zip(*lst):
        if len(set(s)) == 1:
            yield s[0]
        else:
            return



# All the functions for the sample sheet get rendered straight onto one page
def layout(sub=None):
    # All allowed machineries
    machineries = ['mini_seq_standard_reagent', 'mi_seq', 'hi_seq_2500', 'hi_seq_2000','nova_seq_6000_v1.5', 'iSeq', 'next_seq_system', 'hi_seq_x', 'hi_seq_4000', 'hi_seq_3000', 'mini_seq_rapid_reagent', 'nova_seq_6000_v1.0']
    # Set the machineries labels to be capitalised and have spaces instead of underscores
    machineries = [{'label': ' '.join([y.capitalize() for y in x.split('_')]) , 'value':x} for x in machineries]

    title = 'Sample Sheet'
    layout = html.Div(
        [

        # Card wrapper encloses the whole page for aesthetic reasons
        genericCardWrapper([
            # This div encloses all the components relevant to creating and downloading a template
            genericInputWrapper(
                dcc.Markdown('### Download your template'), 
                style={'margin':'auto'}),
            
            # /// FIRST SECTION FOR TEMPLATE DOWNLOAD
            html.Div(
                children=[    
                
                # This first element is a div that contains all the text input, divided in three 'four columns' (totaling to twelve of the row wrapping class)
                html.Div(
                    className='row',
                    children=[
                        TextInputWrapperComponentAIO(
                            'Project Name', 
                            aio_id='project_name',
                            className='four columns',
                            ),
                        TextInputWrapperComponentAIO(
                            'Experiment Name', 
                            aio_id='experiment_name',
                            className='four columns',
                            ),
                        TextInputWrapperComponentAIO(
                            'Additional Comments',
                            aio_id='additional_comments',
                            className='four columns',
                            )]
                ),

                # Second Element contains the clickable layout
                ClickablePlateSelectionAIO(aio_id='plate_selection_store'),


                # Last Div for submit button to download project
                html.Div(className='flexer',
                children=SubmitButtonComponentAIO('Download Template', aio_id='download_template_btn', size='m')),
                
                # Download Component
                dcc.Download(id='template_download_component')                
                ]
            ),
        ]),


        # ///////////////////////
        
        # SECOND SECTION FOR TEMPLATE FILE UPLOAD AND SAMPLE SHEET DOWNLOAD
        # Second Div for the upload of the file! (Maybe different )
        genericCardWrapper([
            #Label
            genericInputWrapper(
                dcc.Markdown('### Upload your template to continue'), 
                style={'margin':'auto'}),
            # Section for uploading the file!
            html.Div([
                dcc.Upload(
                    id='upload_component_sample_sheet',
                    children=html.Div([
                        'Drag and Drop or ',
                        html.A('Select Files')
                    ]),
                    style={
                        'width': '100%',
                        'height': '60px',
                        'lineHeight': '60px',
                        'borderWidth': '1px',
                        'borderStyle': 'dashed',
                        'borderRadius': '5px',
                        'textAlign': 'center',
                        'margin': '10px'
                    },
                    # Allow multiple files to be uploaded
                    multiple=True
                ),
                
            ], style={'width': '60%', 'margin': 'auto'}),

            html.Div(id='for_output_upload_template', className='label warning'),
            #Section with the collapsable wrapper containing all the tables (starts collapsed)


            # Collapsable card section with tables
            CollapsableCardWrapperAIO([
                DataTableDisplay96WellAIO(
                    dropdown=True, 
                    dropdown_choices=[], 
                    aio_id='data_table_display_aio',
                    #report={'something_wrong': True},
                    # Starts as empty
                    display=False
                    ),
                html.Div(id='prefix_suffix_container', className='label')
                    
            ], 
            #Starts as collapsed
            collapsed=True, 
            # Indicate to the user what they're looking at!
            label='uploaded tables',
            aio_id='collapsable_wrapper_table'),


            # Output here if there are any issues (maybe wrap in card or something)

            genericInputWrapper([
                'Download Sample Sheet with ', 
                # This is ugly, find a way for the dropdown not to extend the page
                dcc.Dropdown(['Forward', 'Reverse'], 
                style={'width': '190px'}, 
                id='dropdown_machinery',
                clearable=False,
                # This determines the max height the dropdown assumes once expanded, useful so doesn't overlow the page
                #maxHeight=130,
                # This option is the height for the dropdown labels (required to be more as these are on 2 lines)
                #optionHeight=50
                ),
                'primer strand, in the ',
                dcc.Dropdown(['Classic', 'Extended'],
                style={'width': '100px'},
                id='dropdown_version',
                clearable=False
                ),
                ' version'
            ], className='flexer', style={'margin': '1.5rem'}
            ),

            # Button for downloading sample sheet (starts deactivated)
            SubmitButtonComponentAIO('Download Sample Sheet', size='m', wrapperStyle={'display':'flex', 'justifyContent':'center'}, aio_id='download_sample_sheet_button'),

            # Download component for complete sample sheet --- Wrapped in Loading component (no need for callback)
            html.Div(
                [
                    dcc.Loading(
                        id='loading_sample_sheet_download',
                        type='default',
                        children=[
                            dcc.Download(id='sample_sheet_download_component')
                        ],
                        # parent_style={'minWidth': 'fitContent'}
                    ),
                ],
                className='contain-spinner'
            ),
        
            
        
        ]),

        # In here add all the stores
        dcc.Store(id='store_upload_template')
        

        ],
        className='mainDivPageGeneric'
    )
    
    return layout




# Callback for download of template
@callback(
    Output('template_download_component', 'data'),
    Input(SubmitButtonComponentAIO.ids.button('download_template_btn'), 'n_clicks'),
    State(TextInputWrapperComponentAIO.ids.input('project_name'), 'value'),
    State(TextInputWrapperComponentAIO.ids.input('experiment_name'), 'value'),
    State(TextInputWrapperComponentAIO.ids.input('additional_comments'), 'value'),
    State(ClickablePlateSelectionAIO.ids.store('plate_selection_store'), 'data'),
    prevent_initial_call=True
)
def handle_download_template(click, project, experiment, commments, store):
    # If no selection the button doesn't work
    selection = False
    for x in store.values():
        if x == True:
            selection = True
    if not selection:
        return None
    
    # Get filename and sample sheet string from wrapper
    filename, sample_sheet = wrapper_make_template(store, project, experiment, commments)
    # Send template and filename in dict form to dcc.Download
    return {'content':sample_sheet, 'filename':filename}
    #return f'{project} {experiment} {commments} {store}'






# Callback for file upload
@callback(
    Output('for_output_upload_template', 'children'),
    Output('store_upload_template', 'data'),
    Input('upload_component_sample_sheet', 'contents'),
    State('upload_component_sample_sheet', 'filename'),
    prevent_initial_call =True
)
def handle_upload_template(content, filename):
    # Check that the filename is in CSV format and that is not empty
    filename, content = filename[0], content[0] # for some reason they're returned as lists..

    # Sanity check on file
    if filename is not None and filename.split('.')[1] != 'csv':
        return "Please only upload 'csv' files", None
    if content is None:
        return 'The content of the file you uploaded is not valid', None


    #Here add read extension and different read in methods
    try:
        tables, check_tables, metadata_dict, report = wrapper_handle_upload(content, filename)
    except Exception as e:
        print(e)
        return 'Error processing the file', None

    # If in the general report there are two names that are the same and it's not blank, inform the user and block it from proceeding
    if report:
        # If blank in keys remove it
        if 'blank' in report.keys():
            report.pop('blank')
        
        # If the report has unwanted cells return the unwanted cells
        if 'unwanted' in report.keys():
            return f'Error, one or more cells have non-word characters, please change naming: {", ".join(report["unwanted"])}', None
                
        # If the report has still keys display it
        if len(report.keys()) > 0:
            return f'Error, two or more samples have the same name: {", ".join([f"{x} was repeated {y} times" for x,y in report.items()])}', None


    # Tables have to be in dictionary form to be json-serialisable, so handle that.
    tables_new = {key:value.to_dict() for key,value in tables.items()}

    # Store is set so to return a dictionary with all the data
    store = dict(tables=tables_new, check_tables=check_tables, metadata_dict=metadata_dict)

    # IF any of the table's reports has any issue, report it 
    something_wrong_string='Ops something wrong in this table(s): '
    something_wrong_bool = False
    for key,value in check_tables.items():
        if value.get('something_wrong', False):
            something_wrong_string += f'{key} '
            something_wrong_bool=True

    if something_wrong_bool:
        return something_wrong_string, json.dumps(store)
    else:
        # Store has to be in format json.dumps
        return '', json.dumps(store)




# Callback for handling the display of the table --- This callback has also the responsibility to actually remove the display none from the table wrapper!
# This callback also captures prefix-suffix from the sample names and displays them in a separate label so not to display a table that is too cluttered
@callback(
    # Give dropdown options
    Output(DataTableDisplay96WellAIO.ids.dropdown('data_table_display_aio'), 'options'),
    # Give data for table
    Output(DataTableDisplay96WellAIO.ids.table('data_table_display_aio'), 'data'),
    # Give columns for table
    Output(DataTableDisplay96WellAIO.ids.table('data_table_display_aio'), 'columns'),
    # Give value to dropdown
    Output(DataTableDisplay96WellAIO.ids.dropdown('data_table_display_aio'), 'value'),
    # Display table if not displaying already  
    Output(DataTableDisplay96WellAIO.ids.wrapping_div('data_table_display_aio'), 'style'),
    # Display reports if needed!
    Output(DataTableDisplay96WellAIO.ids.report_wrapper('data_table_display_aio'), 'children'),
    #Needed to change STYLE!!!
    Output(DataTableDisplay96WellAIO.ids.report_wrapper('data_table_display_aio'), 'style'),
    Output('prefix_suffix_container', 'children'),
    # This is to open the collapsable div on upload (Not really working)
    #Output(CollapsableCardWrapperAIO.ids.collapse_button('collapsable_wrapper_table'), 'n_clicks'),
    # Get data from store
    Input('store_upload_template', 'data'),
    # Get selection from the dropdown
    Input(DataTableDisplay96WellAIO.ids.dropdown('data_table_display_aio'), 'value'),
    State(DataTableDisplay96WellAIO.ids.wrapping_div('data_table_display_aio'), 'style'),
    prevent_initial_call = True
)
def return_table(data, value, style): #,current_options
    # You return the display options, the table df and the column names for it
    # in format [{'name': i, 'id': i} for i in table.columns]

    # #Extract json data
    data = json.loads(data)

    # Display options are the plate flavours uploaded
    options = [x for x in data['tables'].keys()]

    # Keep value if present, else give either 
    value = value if value else options[0]


    # Extract table to display
    display_table = data['tables'][value]
    
    # convert table to df and prepare it for display in AIO component
    display_df = pd.DataFrame.from_dict(display_table)
    
    # Columns to display
    cols = [{'name': i, 'id': i} for i in display_df.columns]

    # Make style to return
    style = {'display': 'flex'}

    # Make reports to return, if any
    reports = data['check_tables'][value]

    reports_string = '''Ops, something went wrong:'''

    # Check if there is something wrong!
    if reports['something_wrong']:
        # If there are wells name to change, display that first
        if len(reports['to_change']) > 0:
            reports_string += f"""Please change the following sample name(s) {", ".join([x for x in reports["to_change"]])}"""
        # If total samples, and unique samples number differ, not every name is unique
        elif reports['total_samples'] != reports['unique_sample_names']:
            reports_string += 'The sample names are not unique'
        # There are blanks on the plate
        elif reports['blanks'] > 0:
            reports_string += 'Blanks were detected'
        else:
            reports_string += 'This plate is not valid'


    # This logic seems backwards to me, but if it works, it works
    reports_style = {'display': 'none'} if not reports['something_wrong'] else {'display': 'block'}

    # Get the list of values to check if there is a prefix/suffix
    list_of_values = display_df.values.ravel()
    # Remove all 'blank' cells, as they interfere
    list_of_values = [x for x in list_of_values if x != 'blank']
    # Check if the strings have any prefixes-suffixes?
    prefix = ''.join(common_prefix(list_of_values))
    suffix = ''.join(common_suffix(list_of_values))[::-1] #need to invert this!

    # Get the DF to return
    df_to_return = display_df.to_dict('records')
    # Check if suffixes are there
    prefix_suffix_string = ''
    prefix_bool=False
    suffix_bool=False
    # If a prefix or suffix is found
    if prefix != '' or suffix != '':
        # Check that the prefix/suffix is worth including (eg > 3 chars)
        if len(prefix) > 2:
            prefix_bool=True
            prefix_suffix_string += f'Sample name prefix: {prefix} \t'

        if len(suffix) > 2:
            suffix_bool=True
            prefix_suffix_string += f'Sample name suffix: {suffix} \t'

    # If the prefix/suffix is found, remove them from the table sample name
    if len(prefix_suffix_string) > 1:
        # Iterate through DF to return and remove prefix/suffix
        # The DF is in format [{row:value, row:value, ...},{...}]
        new_df=[]
        strip_prefix = lambda x: x.strip(prefix) if prefix_bool else x
        strip_suffix = lambda x: x.strip(suffix) if suffix_bool else x
        strip_both = lambda x: strip_prefix(strip_suffix(x))
        for row in df_to_return:
            new_row = {key: strip_both(value) for key, value in row.items()}
            new_df.append(new_row)
        
        df_to_return = new_df

    return options, df_to_return, cols, value, style, reports_string, reports_style, prefix_suffix_string #, 1
   



# Callback for sample sheet download

# sample_sheet_download_component
@callback(
    Output('sample_sheet_download_component', 'data'),
    Input(SubmitButtonComponentAIO.ids.button('download_sample_sheet_button'), 'n_clicks'),
    # Get data from store and the two dropdowns
    State('store_upload_template', 'data'),
    State('dropdown_machinery', 'value'),
    State('dropdown_version', 'value'),

    prevent_initial_call=True,
)
def handle_download_sample_sheet(click, store, strand, selection):

    # Return none if the store is null
    if store == None or strand == None or selection == None:
        return None

    # Change strand selection format
    strand = False if strand == 'Forward' else True

    # MACHINERY BECOMES FORWARD/REVERSE (false, true)

    # Change selection format
    complete = True if selection == 'Extended' else False

    # Extract data from the store
    # Need tables, project, experiment, comments
    data = json.loads(store)

    # Get tables from store
    tables = data['tables']
    # Convert it to dfs
    tables_dict={key: pd.DataFrame.from_dict(value) for key, value in tables.items()}

    # Get metadata from store
    metadata = data['metadata_dict']
    # Extract metadata
    project, experiment, comments = metadata['project_name'], metadata['experiment_name'], metadata['comments']

    # Call wrapper function
    filename, text = wrapper_create_complete_sample_sheet(tables_dict, complete, strand, project, experiment, comments)


    return {'content':text, 'filename':filename}
