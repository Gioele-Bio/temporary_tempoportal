from dash import Dash, Output, Input, State, html, dcc, callback, MATCH
import uuid
from .genericInputWrapper import genericInputWrapper


# All in one components are suffixed AIO
# html.Div will be the 'parent' component
class TextInputWrapperComponentAIO(html.Div): 
    # Set of functions to create pattern-matching callbacks of the subcomponents 
    class ids:
        label = lambda aio_id:{
            'component': 'TextInputWrapperComponentAIOComponentValue',
            'subcomponent': 'label',
            'aio_id':aio_id
        }

        input = lambda aio_id:{
            'component': 'TextInputWrapperComponentAIOComponentValue',
            'subcomponent': 'input',
            'aio_id':aio_id
        }
    
    # make ids class a public class
    ids = ids

    # Define argument of the all in one component

    def __init__(
        self,
        label,
        aio_id=None,
        **kwargs):
        """
        In here you put the description of the class, as of now not much to be explained
        """

        # Set initial input if user doesn't set the one on its own (this can be done for styling and dictionaries also)

        # Allow to pass own aio_id if needed to bind own callbacks (we need this). Otherwise it makes one random to avoid collisions
        if aio_id is None:
            aio_id = str(uuid.uuid4())



        # Handle additional classnames
        className='genericTextInputComponentAIO'
    
        if 'className' in kwargs.keys():
            className = className + ' ' + kwargs['className']
            kwargs.pop('className')


        # Define component LAYOUT
        # Makes it so there is an html.Div as wrapper
        super().__init__([
            # Components of interest

            # Input field
            dcc.Input(
                placeholder=label,
                type='text',
                value='',
                id=self.ids.input(aio_id),
                style={'minWidth': '85%', 'maxWidth':'100%'},
                
        )
  

        ], className=className, **kwargs)


    # Define component pattern-matching callback, that will apply to every instance of this component
    # @callback(
    #     Output(ids.label(MATCH), 'children'),
    #     Input(ids.input(MATCH), 'value'),
    #     prevent_initial_call=True,

    # )
    # def update_label_text(value):
    #     print(value, 'coming from here')
    #     return value
        

    # This callback above was made just to try, and demonstrate how to (it had a separate label div which has become the placeholder)
























