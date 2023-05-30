import dash
from dash import Dash, dcc, html, Output, Input, State, get_asset_url
# Protect routes
#from flask_login.utils import login_required
#from flask_login import current_user


def create_dash_application(flask_app, local=False):
    
    # If local the app is being run for local development!! (no relative imports)
    if local:
        from utils.components import MainSideBarAIO, SubmitButtonComponentAIO
        import dash_auth

        VALID_USERNAME_PASSWORD_PAIRS = {
            'hello': 'world'
        }


        dash_app = dash.Dash(
            __name__,
            use_pages=True,
            pages_folder='utils', 
            prevent_initial_callbacks=True,)
        
        auth = dash_auth.BasicAuth(
            dash_app,
            VALID_USERNAME_PASSWORD_PAIRS
        )
    
    else:
        from .utils.components import MainSideBarAIO, SubmitButtonComponentAIO
        # Initial app declaration, usepages true (THIS IS THE FLASK IMPLEMENTATION)
        dash_app = dash.Dash(
            # Declare server
            server=flask_app,
            # Base pathname
            name='DashApp',
            assets_folder='assets',
            url_base_pathname='/app/',
            use_pages=True, 
            pages_folder='dash_app/utils', 
            prevent_initial_callbacks=True,)#suppress_callback_exceptions=True



    # Set stylesheets
    dash_app.config.external_stylesheets = ['./style/base_style.css', './style/additional_style.css']


    # dash_app layout
    dash_app.layout = html.Div(
        [
            # Div for header where there is the static logo and dynamic login/logout
            html.Div(
                children=[
                    #dcc.Markdown('##### BioSpyder Logo'),
                    html.Div(
                        html.Img(src=get_asset_url('images/BioSpyderLogoMidTM.png'),
                        style={'height':'inherit'}), 
                    style={'height':'inherit', 'width': '30%'}),
                    
                    # Markdown to show the email of the user logged in
                    dcc.Markdown(id='user_logged'),
                    #Button and location for logout
                    #SubmitButtonComponentAIO('Logout', background_color='red', aio_id='logout_btn', size='s'),
                    dcc.Location(id='logout_location')
                ],
                id='pageHeader',
                
            ),

            # Div for rest of the page
            html.Div([
                html.Div(
                    MainSideBarAIO(aio_id='sidebarAIO_id'),
                    id='sidebarDiv',
                    style={'width':'15%'}
                ),

                html.Div(
                    dash.page_container,
                    id='contentDiv',
                    style={'marginLeft':'15%'} 
                )],
                id='mainPageDiv'
                )
        ],
        id='mainDiv',
        
        )

    


    #Callback for collapsing sidebar
    @dash_app.callback(
        Output(MainSideBarAIO.ids.collapse_button('sidebarAIO_id'), 'className'),
        Output(MainSideBarAIO.ids.main_div('sidebarAIO_id'), 'className'),
        Output('sidebarDiv', 'style'),
        Output('contentDiv', 'style'),
        Input(MainSideBarAIO.ids.collapse_button('sidebarAIO_id'), 'n_clicks'),
        State(MainSideBarAIO.ids.collapse_button('sidebarAIO_id'), 'className'),
        prevent_initial_call=False
    )
    def collapse_sidebar(click, style):
        if style == 'checked':
            return 'unchecked', 'uncheckedDiv', {'width':'5%'}, {'marginLeft':'5%'} 
        else:
            return 'checked', 'checkedDiv', {'width':'15%'}, {'marginLeft':'15%'}

    
    # # Callback for logging out!
    # @dash_app.callback(
    #     Output('logout_location', 'href'),
    #     Input(SubmitButtonComponentAIO.ids.button('logout_btn'), 'n_clicks')
    # )
    # def logout(click):
    #     return '/logout'


    # # Callback for displaying the name of the logged user!!
    # @dash_app.callback(
    #     Output('user_logged', 'children'),
    #     Input('logout_location', 'href'),
    # )
    # def check_user_logged(x):
    #     try:
    #         return f'###### Hello {current_user.email}'
    #     except:
    #         return ''
    
    

    # # Code to protect all routes inside dash app!!! (only needed if running inside flask)
    # if not local:
    #     for view_function in dash_app.server.view_functions:
    #         # If it has 'app' in front of it
    #         if view_function.startswith(dash_app.config.url_base_pathname):
    #             dash_app.server.view_functions[view_function] = login_required(dash_app.server.view_functions[view_function])

    return dash_app


    
# Run dash_app
if __name__ == '__main__':
    app = create_dash_application(__name__, local=True)
    app.run_server(port=9000, debug=True) 






