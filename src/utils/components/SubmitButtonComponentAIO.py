from dash import Dash, Output, Input, State, html, dcc, callback, MATCH
import uuid

class SubmitButtonComponentAIO(html.Div):
    # Component
    class ids:
        button = lambda aio_id:{
            'component': 'SubmitButtonComponentAIOButton',
            'subcomponent': 'button',
            'aio_id':aio_id
        }

    # Make ids public
    ids = ids

    # Define starting arguments
    def __init__(
        self,
        label,
        background_color=None,
        aio_id=None,
        size = None,
        style=None,
        className=None, 
        disabled=False,
        classNameWrapper=None,
        wrapperStyle={}
        ):
        """Standardised button, can decide the label, colour (rgba or text), size (s, m, l) and add any other style inline as required"""

        # Set style dict for background color
        background_color = background_color if background_color else 'whitesmoke'
        colour_dict = {'backgroundColor': background_color}

        # Merge to style dictionary if any
        style_dict = style | colour_dict if style else colour_dict


        # Set default size
        size = size if size else 'm'
        #Set aio_id if none
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # These correspond to different styling per class in the extra_style.css file
        sizing_classname = {
            's':'SubmitButtonComponentAIOButtonSmall',
            'm':'SubmitButtonComponentAIOButtonMedium',
            'l':'SubmitButtonComponentAIOButtonLarge'
        }

        super().__init__([
            html.Button(
                label, 
                id=self.ids.button(aio_id),
                style=style_dict,
                disabled=disabled,
                # Handle the possibility to have 2 classnames
                className=f'{sizing_classname[size]} {className}' if className else sizing_classname[size]
                )
        ], className=classNameWrapper, style=wrapperStyle)


