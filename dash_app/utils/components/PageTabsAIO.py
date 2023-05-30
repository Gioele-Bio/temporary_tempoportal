import dash
from dash import Dash, html, dcc, Output, Input, State, callback, MATCH
import uuid


# All in one component to structure tabs
# Made it so that the page that calls it gives a list of dictionaries in the form of
# [{'name': 'subpage name', 'address':'subpage url address', function: functionToRenderThePage}, ...]

class PageTabsAIO(html.Div):
    # Ids
    # May need to add something else
    class ids:
        main_div = lambda aio_id:{
            'component': 'PageTabsAIO',
            'subcomponent': 'main_div',
            'aio_id':aio_id
        }

        location = lambda aio_id:{
            'component': 'PageTabsAIO',
            'subcomponent': 'location',
            'aio_id':aio_id
        }

    # Make ids public
    ids = ids

    # Initialiser
    def __init__(
        self,
        subpages,
        this_page,
        selected = None,
        aio_id = None
        ):
        """
        All in one component to structure tabs. Takes in a list of dictionaries in the form of: [{'name': 'subpage name', 'address':'subpage url address', function: functionToRenderThePage}, ...]. This page requires the page path, so that it can be recognised by the tab location (Not the cleanest solution, but works)
        """
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # If no subpage is selected, just return the first one
        if selected is None:
            selected = subpages[0]['address']

        # Component layout 
        super().__init__([
            dcc.Tabs([
                dcc.Tab(
                    label = page['name'],
                    children= page['function'](),
                    value=page['address']
                ) for page in subpages
            ], value=selected,
            id=self.ids.main_div(aio_id),
            className=this_page) 
            # The classname with this page, is required by the callback below, if you find a different way to pass this variable, please change it
            ,

            # Location to set the href to correct reference
            dcc.Location(id=self.ids.location(aio_id), refresh=False)



        ], style={'height': 'inherit', 'width': '100%', 'backgroundColor': 'red'})


    @callback(
        Output(ids.location(MATCH), 'href'),
        Input(ids.main_div(MATCH), 'value'),
        Input(ids.location(MATCH), 'href'),
        Input(ids.main_div(MATCH), 'className') # classname is this page variable
    )
    def update_value(value, href, this_page):
        # print('value in ',value, href, this_page)
        # If it comes from this page (jumping pages causes issues)
        if this_page in href and value != None:    
            #remove value from sub
            current_href = href.split('?sub=')[0]
            # Append correct value
            return f'{current_href}?sub={value}'
        else:
            # send back unchanged href
            return href
