import dash
from dash import Dash, html, dcc


style = {
    
}

#For later on to map to navbar
dash.register_page(__name__, path='/', name='Homepage', image='images/icons/home_icon.png') #as it is homepage
#!!!!!! Give these an image/image link for the sidebar icons



#instead of returning things, we just declare the layout
layout = html.Div(
    [dcc.Markdown('# HOMEPAGE'),
    # html.Div('Hello there',
    # style={
    #     'height':'300px',
    #     'width':'90%',
    #     'backgroundColor':'blue'
    # }),
    # html.Div('Hello there',
    # style={
    #     'height':'300px',
    #     'width':'90%',
    #     'backgroundColor':'blue'
    # }),
    # html.Div('Hello there',
    # style={
    #     'height':'300px',
    #     'width':'90%',
    #     'backgroundColor':'blue'
    # }),
    # html.Div('Hello there',
    # style={
    #     'height':'300px',
    #     'width':'90%',
    #     'backgroundColor':'blue'
    # })
    ], 
    style=style,
    className='row')




