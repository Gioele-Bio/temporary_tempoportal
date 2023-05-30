import dash
from dash import Dash, html, dcc, Output, Input, State, callback, MATCH
import uuid


# Probably need sublabel class too

class SideBarLabelAIO(html.Div):
    # IDS
    class ids:
        label = lambda aio_id:{
            'component': 'SideBarLabelAIOLabel',
            'subcomponent': 'label',
            'aio_id':aio_id
        }

    # Make ids public
    ids = ids

    # Define function for sublabel wrapper with same classname (for styling consistency. No need to make an AIO just for this)
    def SidebarSubLinkWrapper(self, subpages:dict, main_path, **kwargs):
        # Unpack dictionary data for subpages
        sublabel = subpages['name']
        address = subpages['address']
        return html.Div([
                    dcc.Link(sublabel, href=f'{main_path}?sub={address}')
            ], className='sidebarSubLinkLabel')


    # Initialising arguments
    def __init__(
        self,
        page,
        aio_id = None
    ):
        """
        SideBar label AIO component. This will handle the main labels styling depending on if the sidebar is collapsed or not. It will also handle the adding of the sublabels in case there is any.
        """

        # Unpack dictionary data for subpages
        # sublabel = dictionary['name']
        # address = dictionary['address']
        # function = dictionary['function']



        # If no id is assigned, assign a random one
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        
    

        # Unpack page dictionary
        label = page['name']
        # Get relative path as link
        path = dash.get_relative_path(page['path'])
        image_path = page['image']
        subpages = page['description']

        super().__init__([
            ### Label component, this is already enclosed in a div which is the super component of the SideBarLabelAIO, so the declaration starts with the Link (so to make the whole label clickable)
            dcc.Link(
                className='sidebarLabelLink',
                href=path,
                children=[
                    # Span enclosing the icon image for the label. If there is no supplied image path, an I is rendered as place holder
                    html.Span(
                        className='sidebarLabelIcon',
                        children=[
                            html.Img(src=dash.get_asset_url(image_path))
                            if image_path else
                            html.I()
                        ]
                    ),

                    # 'P' enclosing the text of the label
                    html.P(
                        className='sidebarLabelText',
                        children=label
                    ),

                    


                ]
            ),

            # Div enclosing sublinks, which iteratively renders sublabels, if any. Else returns empty div
            html.Div(className='sidebarSublinkDiv') if subpages == '' else
            # Render sublinks
            html.Div(
                className='sidebarSublinkDiv',
                children=[self.SidebarSubLinkWrapper(subpage, path) for subpage in subpages]
            )


            
        ], className='sidebarMainLabel')




















