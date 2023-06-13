import dash
from dash import Dash, html, dcc, callback, Input, Output, State
from ..components import genericCardWrapper, genericInputWrapper, SubmitButtonComponentAIO, TextInputWrapperComponentAIO
from ..functions.report_generation.report_generation_adapted import get_report
from base64 import b64decode
from io import StringIO, BytesIO

path = '/report_generator'

# Register page so to be mapped to the sidebar and href endpoint
dash.register_page(__name__, path=path, name='Report Generator', order='f', image='images/icons/report_icon.png')

layout = html.Div(
    [dcc.Markdown('# Report generator',),
    genericCardWrapper([
        html.Div([# First row has the upload for both gene count and mapped unmapped
            html.Div([
                # Gene count         
                dcc.Upload(
                    id='report_generator_gene_count_upload',
                    children=html.Div([
                        'Drop your count tables or ', html.A('Select Files')
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
                    }),
                    multiple=True
                ),
                # Div for showing which file was uploaded
                html.Div(id='report_generator_uploads_tracker_1', className='row'),
            ], className='six columns'),

            html.Div([
                # Mapped unmapped 
                dcc.Upload(
                    id='report_generator_mapped_unmapped_upload',
                    children=html.Div([
                        'Drop your mapped/unmapped files or ', html.A('Select Files')
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
                    }),
                    multiple=True
                ),
                # Div for output
                html.Div(id='report_generator_uploads_tracker_2', className='row'),
            ], className='six columns'),
            
        ], className='row', style={'alignItems': 'center'}),

        # Div with input for project id, pca and biospyder/bioclavis select
        html.Div([
            html.Div(TextInputWrapperComponentAIO('Project ID', aio_id='report_page_project_id_input'), className='four columns'),
            html.Div(genericInputWrapper(dcc.Checklist(['Get PCA Plot'], id='report_page_get_pca_input')), className='three columns'),
            html.Div(genericInputWrapper(
                [   
                    dcc.Markdown('**Company**'),
                    dcc.RadioItems([{'label':'BioSpyder', 'value':'biospyder'}, {'label':'BioClavis', 'value':'bioclavis'}], id='report_page_company_radio')]
                , style={'width':'60%'}), className='four columns')
        ], className='row'),


        # Div with optional annotation file input, start button to get the report
        html.Div([
            # Optional upload
            html.Div([
                # Gene count         
                dcc.Upload(
                    id='report_generator_annotation_file_upload',
                    children=html.Div([
                        'Drop your optional annotation file or ', html.A('Select Files')
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
                    })),
                # Div for output
                html.Div(id='report_generator_uploads_tracker_3', className='row'),
            ], className='seven columns'),
            
            # Generate button
            html.Div(
                [
                    html.Div(
                        [
                            SubmitButtonComponentAIO('Generate Report', aio_id='report_generator_submit_button'),
                            html.Div(id='report_generator_uploads_tracker_4'),
                        ], style={'display':'flex', 'flexDirection':'column','alignItems':'center'})
                ], 
                className='five columns', style={'display':'flex', 'justifyContent':'center', 'alignItems':'center'}
            )

        ], className='row'),


        # Stores and download component
        dcc.Store(id='report_generator_count_tables_store'),
        dcc.Store(id='report_generator_mapped_unmapped_store'),
        dcc.Store(id='report_generator_annotation_store'),

        dcc.Loading(
                    id='report_generator_loading_spinner',
                    type='default',
                    children=[
                        dcc.Download(id='report_generator_download_csv'),
                        dcc.Download(id='report_generator_download_docx'),
                    ],
                ),


    ]),
    
    
    
    ],
    className='mainDivPageGeneric'
)


# Get in the stuff, need to understand how to keep the tables/mapped unmapped in memory

# Callback for the count tables
@callback(
    Output('report_generator_count_tables_store', 'data'),
    Output('report_generator_uploads_tracker_1', 'children'),
    Input('report_generator_gene_count_upload', 'contents'),
    State('report_generator_gene_count_upload', 'filename'),
    prevent_initial_call = True
)
def transfer_count_tables(contents, filenames):
    #print(contents, filenames)
    uploads = {}

    for content, filename in zip(contents, filenames):
        content_type, content_string = content.split(',')
        decoded_content = b64decode(content_string)
        file_content = StringIO(decoded_content.decode('utf-8')).read()
        uploads[filename] = file_content
    print(len(uploads))
    return uploads, genericInputWrapper(f'{", ".join(filenames)} {"was" if len(filenames) == 1 else "were"} uploaded')


# Callback for the mapped unmapped
@callback(
    Output('report_generator_mapped_unmapped_store', 'data'),
    Output('report_generator_uploads_tracker_2', 'children'),
    Input('report_generator_mapped_unmapped_upload', 'contents'),
    State('report_generator_mapped_unmapped_upload', 'filename'),
    prevent_initial_call = True
)
def transfer_count_tables(contents, filenames):
    #print(contents, filenames)
    uploads = {}

    for content, filename in zip(contents, filenames):
        content_type, content_string = content.split(',')
        decoded_content = b64decode(content_string)
        file_content = StringIO(decoded_content.decode('utf-8')).read()
        uploads[filename] = file_content
    print(len(uploads))
    return uploads, genericInputWrapper(f'{", ".join(filenames)} {"was" if len(filenames) == 1 else "were"} uploaded')



# Callback for the annotation file
@callback(
    Output('report_generator_annotation_store', 'data'),
    Output('report_generator_uploads_tracker_3', 'children'),
    Input('report_generator_annotation_file_upload', 'contents'),
    State('report_generator_annotation_file_upload', 'filename'),
    prevent_initial_call = True
)
def transfer_count_tables(content, filename):
    #print(contents, filenames)
    content_type, content_string = content.split(',')
    decoded_content = b64decode(content_string)
    file_content = StringIO(decoded_content.decode('utf-8')).read()
    return {filename:file_content}, genericInputWrapper(f'{filename} was uploaded')



# Callback for the generate report button
@callback(
    Output('report_generator_download_csv', 'data'),
    Output('report_generator_download_docx', 'data'),
    Output('report_generator_uploads_tracker_4', 'children'),
    Input(SubmitButtonComponentAIO.ids.button('report_generator_submit_button'), 'n_clicks'),
    State('report_generator_count_tables_store', 'data'),
    State('report_generator_mapped_unmapped_store', 'data'),
    State('report_generator_annotation_store', 'data'),
    State(TextInputWrapperComponentAIO.ids.input('report_page_project_id_input'), 'value'),
    State('report_page_get_pca_input', 'value'),
    State('report_page_company_radio', 'value'),
    prevent_initial_call = True
)
def generate_report(click, count_tables, mapped_unmapped, annotation, project_id, pca_bool, company):
    check_vars = {'count tables': count_tables, 'mapped unmapped': mapped_unmapped, 'project id': project_id, 'company': company}
    if None in check_vars.values():
        return None, None, genericInputWrapper(f"You are missing: {', '.join([x for x,y in check_vars.items() if y == None])}; lease update the field(s) and try again")
    
    # Need to order the tables/mapped unmapped
    decided_order_tables = sorted([x for x in count_tables.keys()])
    # Feed the tables based on the decided order
    count_tables = [count_tables[x] for x in decided_order_tables]
    
    decided_order_mapped_unmapped = sorted([x for x in mapped_unmapped.keys()])
    # Feed the tables based on the decided order
    mapped_unmapped = [mapped_unmapped[x] for x in decided_order_mapped_unmapped]

    df, df_name, report, report_name = get_report(project_id, count_tables, mapped_unmapped, company, pca_bool, annotation)
    
    # Set the bytes buffer
    file_stream = BytesIO()
    # Save the docx in buffer
    report.save(file_stream)
    # Reset the buffer pointer
    file_stream.seek(0)

    # Return the CSV and DOCX
    return dcc.send_data_frame(df.to_csv, df_name), dcc.send_bytes(file_stream.getbuffer().tobytes(), report_name), None

