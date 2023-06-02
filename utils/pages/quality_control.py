import dash
from dash import html, dcc, callback, Input, Output
from ..components import PageTabsAIO
# from ..components.qc_subpages import upload_page_layout, line_plot_layout, bar_plot_layout

# Placeholder rendering function
def render():
    return html.Div('Limited version of Tempo-Portal')


# Subpages are fed in a list of dictionaries with keys: Subpage Name, Subpage address and Subpage rendering function
subpages = [
    {'name': 'Upload Data', 'address': 'upload', 'function':render},
    {'name': 'Line Plot', 'address': 'lineplot', 'function':render},
    {'name': 'Bar Plot', 'address':'barplot', 'function': render},
    {'name': 'HeatMap', 'address': 'heatmap', 'function':render},
    ]

path = '/qc_tools'
dash.register_page(__name__, path=path, name='Quality Control', order='c', image='images/icons/quality_control_icon.png', description=subpages) #order to be declared in alphabetical order


# The keyword argument sub captures which subpage is selected from the url string eg /sample_sheet?sub=xxx, so that the layout function can render the correct subpage
def layout(sub=None):
    title = 'Quality Control'
    layout = html.Div([
        dcc.Store(id='storageQC', storage_type='local'),
        dcc.Markdown('# Quality control'),
        PageTabsAIO(subpages, path.removeprefix('/'), sub)
    ], className='mainDivPageGeneric', style={'padding':'0'}) # need the padding 0 as pagetabs would look bad otherwise
    return layout
