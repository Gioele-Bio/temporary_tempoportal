import dash
from dash import html, dcc
from ..components import PageTabsAIO

# Placeholder rendering function
def render():
    return html.Div('Returned')

subpages = [
    {'name': 'Upload Data', 'address': 'upload', 'function':render},
    {'name': 'New Plot', 'address': 'newplot', 'function':render},
    {'name': 'Otherplot', 'address': 'otherplot', 'function':render},
    ]

# Declare path
path = '/differential_expression'
# Register page
dash.register_page(__name__, path=path, name='Differential Expression', order='d', image='images/icons/differential_expression_icon.png', description=subpages)

layout = html.Div(
    dcc.Markdown('# DIFFERENTIAL EXPRESSION - Limited Version of TempoPortal')
)

# The keyword argument sub captures which subpage is selected from the url string eg /sample_sheet?sub=xxx, so that the layout function can render the correct subpage
def layout(sub=None):
    title = 'Differential Expression'
    layout = html.Div([
        dcc.Store(id='storageDifferentialExpression', storage_type='local'),
        dcc.Markdown(f'# {title}'),
        PageTabsAIO(subpages, path.removeprefix('/'), sub)
    ], className='mainDivPageGeneric', style={'padding':'0'}) # need the padding 0 as pagetabs would look bad otherwise
    return layout
