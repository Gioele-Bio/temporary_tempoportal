import dash
from dash import Dash, html, dcc, Output, Input, State


def genericCardWrapper(children, **kwargs):
    return html.Div(
        [children][0] if isinstance(children, list) else children,
        className='genericCardDiv',
        **kwargs
    )


