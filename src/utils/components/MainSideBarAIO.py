import dash
from dash import Dash, html, dcc, Output, Input, State, callback, MATCH
import uuid
from .SideBarLabelAIO import SideBarLabelAIO

# All in one component for sidebar
class MainSideBarAIO(html.Div):
    # Ids 
    # Not completely sure on what to add here as of now, might need to interact with some elements later on
    class ids:
        main_div = lambda aio_id:{
            'component': 'MainSideBarAioMainDiv',
            'subcomponent': 'main_div',
            'aio_id':aio_id
        }
        collapse_button = lambda aio_id:{
            'component': 'MainSideBarAioCollapseButton',
            'subcomponent': 'collapse_button',
            'aio_id':aio_id
        }

    # Make ids public
    ids = ids

    # Define initialising arguments
    def __init__(
        self,
        #This one sets the value opposite as the callback is set to activate on render changing the boolean
        collapsed = False,
        aio_id=None
    ):
        """
        Sidebar AIO component, you can toggle the collapse button with different settings as required
        """
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # Component layout
        super().__init__([
            html.Div(
                [
                    # This is the X to collapse the sidebar
                    html.Div(className='spinner-master', children=[
                        #'<input type="checkbox" id="spinner-form2" />',
                        html.Div(className='checked' if collapsed else 'unchecked', 
                        id=self.ids.collapse_button(aio_id),
                        style={'height': 'fitContent'},
                        children=[

                            html.Label([
                                html.Div(className='spinner2 diagonal part-1'),
                                html.Div(className='spinner2 horizontal'),
                                html.Div(className='spinner2 diagonal part-2')
                            ], className='spinner-spin2')
                        ]),
                    ]),

                    # This is the remainder of the sidebar
                    # This div's classname changes together with the collapsing of the sidebar, so that the rendering of the labels will be managed exclusively by the CSS and its selectors

                    html.Div(id=self.ids.main_div(aio_id), className='checkedDiv' if collapsed else 'uncheckedDiv', children=[
                        # IN HERE RENDER LABELS!
                        # For each page registered in the page registy, render a label (pass the whole dictionary which will be handled by the SideBarLabelAIO directly)
                        SideBarLabelAIO(page) for page in dash.page_registry.values()

                    ])




                ],
                # style={'height':'100%', 'bottom':'0'}
                ) 
                
               




                # At some point when there is the differentiation you need to finesse with
                #if not collapsed else 
            # html.Div(
            #     style={'backgroundColor':'blue', 'height':'50vh'}
            #     )
        ], style={'height':'100%'}
        )












