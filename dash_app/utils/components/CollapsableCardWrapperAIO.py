import dash
from dash import Dash, html, dcc, Output, Input, State, MATCH, callback
import uuid

# Component styled to contain elements non-essential to the page, and that can be collapsed away
class CollapsableCardWrapperAIO(html.Div):
    # Ids of interest (none really... just one for the clickable button to collapse the whole wrapper)
    class ids:
        collapse_button = lambda aio_id:{
            'component': 'collapsableCardWrapperAIOButton',
            'subcomponent': 'collapse_button',
            'aio_id':aio_id
        }

        collapse_label = lambda aio_id:{
            'component': 'collapsableCardWrapperAIOLabel',
            'subcomponent': 'collapse_label',
            'aio_id':aio_id
        }

        button_label_wrapper = lambda aio_id:{
            'component': 'collapsableCardWrapperAIOLabel',
            'subcomponent': 'button_label_wrapper',
            'aio_id':aio_id
        }

        collapsing_div = lambda aio_id:{
            'component': 'collapsableCardWrapperAIODiv',
            'subcomponent': 'collapsing_div',
            'aio_id':aio_id
        }

    # Make ids public
    ids = ids

    # Define initialising arguments
    def __init__(
        self,
        children,
        label='content',
        collapsed = False,
        default_class = None,
        disabled=False,
        aio_id=None,
        **kwargs
    ):
        """
        Component styled to contain elements non-essential to the page, and that can be collapsed away. No need to handle any callback, but you can assign an aio_id if you want to artificially propagate clicks to collapse/reopen the wrapper (Target->button_label_wrapper). The object either takes a label describing the wrapper content or 'False' to display no label. The default class is the same of the genericCardWrapper, change it if you dare.
        """
        #Set aio_id
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        #Complete label
        complete_label = 'Expand to see ' + label if label else ''

        # Handle className
        default_class = default_class if default_class else 'collapsableCardWrapperDiv'

        # Handle collapsed
        collapsable_classname_label = 'collapsableCardWrapperLabel'
        collapsable_classname_div = 'collapsableCardWrapperDivCollapseSection'
        collapsable_classname_button = 'collapsableCardWrapperDivCollapseBtn'
        if collapsed:
            collapsable_classname_label += ' collapsed'
            collapsable_classname_div += ' collapsed'
            collapsable_classname_button += ' collapsed'

        extra_style = {'width': 'fitContent'}
        if 'style' in kwargs.keys():
            style = kwargs['style'] | extra_style
            kwargs.pop('style')
        else:
            style = extra_style
        


        # Constructor
        super().__init__([
            # Add a component to be clicked to collapse the whole situation

            # 'Header' section with label and button
            html.Div([
                html.A(
                    # Img enclosing the icon
                    html.Img(alt='collapse_icon', 
                    src=dash.get_relative_path('/assets/images/icons/open_collapse.png'),
                    #src=dash.get_asset_url('assets/images/icons/open_collapse.png')
                    ),
                    id=self.ids.collapse_button(aio_id), className=collapsable_classname_button
                    ),
                html.P(
                    complete_label if label else None, className=collapsable_classname_label, id=self.ids.collapse_label(aio_id)
                    ) 
            ], className='collapsableCardWrapperLabelDivWrapper',id=self.ids.button_label_wrapper(aio_id)),

            html.Div(
                children, 
                className=collapsable_classname_div,
                id=self.ids.collapsing_div(aio_id),
                style={'paddingTop': '1rem'})

        ], className=default_class, style=style, **kwargs)


    # Callback updates classes so to display or not the content
    @callback(
        Output(ids.collapse_button(MATCH), 'className'),
        Output(ids.collapsing_div(MATCH), 'className'),
        Output(ids.collapse_label(MATCH), 'className'),
        Input(ids.button_label_wrapper(MATCH), 'n_clicks'),
        State(ids.collapse_button(MATCH), 'className'),
        State(ids.collapsing_div(MATCH), 'className'),
        State(ids.collapse_label(MATCH), 'className'),
        prevent_initial_call = True
    )
    def update_store(click, button, div, label):
        if 'collapsed' in button:
            button = button.split(' ')[0]
            div = div.split(' ')[0]
            label = label.split(' ')[0]
        else:
            button += ' collapsed'
            div += ' collapsed'
            label += ' collapsed'

        return button, div, label



# collapsableCardWrapperDivCollapseBtn : collapsed
# collapsableCardWrapperDivCollapseSection : collapse
