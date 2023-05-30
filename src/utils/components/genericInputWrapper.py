import dash
from dash import Dash, html, dcc, Output, Input, State




def genericInputWrapper(children, **kwargs):
    className='genericInputWrapper'
    
    if 'className' in kwargs.keys():
        className = className + ' ' + kwargs['className']
        kwargs.pop('className')

    return html.Div(
        [children][0] if isinstance(children, list) else children,
        className=className,
        **kwargs
    )


