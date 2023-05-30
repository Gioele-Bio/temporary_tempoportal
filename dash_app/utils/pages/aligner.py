import dash
from dash import html, dcc

path = '/aligner'

dash.register_page(__name__, 
    path=path, 
    name='Aligner', 
    order='b', 
    image='images/icons/aligner_icon.png'
    )


# Layout for picking the aligner and run alignment
def layout():
    # Main Div of the page 
    return html.Div(
        dcc.Markdown('# Aligner Page - Limited version of TempoPortal')
    )
        


