import dash
from dash import Dash, html, dcc

path = '/support'

# Register page so to be mapped to the sidebar and href endpoint
dash.register_page(__name__, path=path, name='Support Page', order='e', image='images/icons/support_icon.png')

layout = html.Div(
    dcc.Markdown('# SUPPORT PAGE'),

    className='mainDivPageGeneric'
)


