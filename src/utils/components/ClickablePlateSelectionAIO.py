
# This element is working just fine, unfortunately, the handling of the 24/48 (eg mutually exclusive for selection) doesn't make it easy at all, so have to hard code it


import dash
from dash import Dash, html, dcc, Output, Input, State, callback, MATCH, ALL
import uuid

def return_button():
    return html.Div(

        style={
            'backgroundColor': 'blue',
            'width':'19%'
        },
        #className='three columns'
    )



# All in one component for sidebar
class ClickablePlateSelectionAIO(html.Div):
    # Ids 
    # Not completely sure on what to add here as of now, might need to interact with some elements later on
    class ids:
        store = lambda aio_id:{
            'component': 'ClickablePlateSelectionAIOStore',
            'subcomponent': 'store',
            'aio_id':aio_id
        }
        
    # Make ids public
    ids = ids

    # Define initialising arguments
    def __init__(
        self,
        #This one sets the value opposite as the callback is set to activate on render changing the boolean
        aio_id=None
    ):
        """
        Clickable Plate Selection AIO (Not sure it'll be re-used but having it here definitely makes it easier to read and mantain the code)
        """
        if aio_id is None:
            aio_id = str(uuid.uuid4())


        #Declare cells ids to be retrieved later
        cells = {
            'Plate_E': 'Plate E',
            'Plate_F': 'Plate F',
            'Plate_G': 'Plate G',
            'Plate_H': 'Plate H',
            'Plate_24': 'Plate 24 Well',
            'Plate_I': 'Plate I',
            'Plate_J': 'Plate J',
            'Plate_K': 'Plate K',
            'Plate_L': 'Plate L',
            'Plate_48': 'Plate 48 Well',
        }

        # Component layout
        super().__init__([
            # Make grid layout 
            html.Div(
                className='containerTenByTen',
                # Declare children dynamically so to be able to append callback to it
                children=[
                    html.Div(
                        value, 
                        # Pattern for matching index
                        id={
                            'type':'clickable_selector',
                            'index': key
                        },
                        className='clickableBox inactive'
                    
                    ) 
                    
                    for key, value in cells.items()]
            ),
            # Store that parent component can refer to
            dcc.Store(id=self.ids.store(aio_id), storage_type='session'),


            # In between store that is required for pattern matching (this store's update triggers the updating of the other. I know it seems silly but to access the other store you need to use MATCH, which cannot be used together with the MATCH of the selectors)
            dcc.Store(id='bypass_temporary_store', 
                #Initialising dictionary, not needed but better for handling!
                data={x:False for x in cells.keys()}),


        ])


        
        
    # Callback to store result in local store AND change the classname
    @callback(
        Output('bypass_temporary_store', 'data'),
        Output({'type':'clickable_selector','index': ALL}, 'className'),
        Input({'type':'clickable_selector','index': ALL}, 'n_clicks'),
        State('bypass_temporary_store', 'data'),
        State({'type':'clickable_selector','index': ALL}, 'className'),
        prevent_initial_call = True
    )
    def update_selection(values, store, classes):
        # Get index of button that called
        triggered_index = dash.ctx.triggered_id.index
        
        # CHECK - check that the triggered index is not triggered by a deactivated button (eg None). If it is return the state as it was
        if store[triggered_index] == None:
            return store, classes

        # Invert the button's boolean in the store
        store[triggered_index] = not store[triggered_index]

        # Handle the deactivation of the 24/48
        # Check if this click makes the plate active, if so make the other deactivated (null in store). If plate goes inactive, make the other inactive too (so is not deactivated). If the store is null return deactivated. (has noth)
        if triggered_index == 'Plate_24':
            # Check if active 
            if store['Plate_24']:
                # Make 48 deactivated
                store['Plate_48'] = None
            else:
                # If not active means it's inactive, and other store can be inactivated too
                store['Plate_48'] = False

        # Same but opposite
        if triggered_index == 'Plate_48':
            if store['Plate_48']:
                store['Plate_24'] = None
            else:
                store['Plate_24'] = False

        

        # Get input list so to make a dictionary out of its keys to return to the classname list
        input_list = dash.callback_context.inputs_list[0]
        classNames=[]
        for plate in input_list:
            index = plate['id']['index']
            # Handle specific Plate_24/Plate_48 case
            if index == 'Plate_24' or index == 'Plate_48':
                className = 'clickableBox '
                # Compose classname and append it to list
                if store[index] == True:
                    className += 'active'
                elif store[index] == False:
                    className += 'inactive'
                elif store[index] == None:
                    className += 'deactivated'
                
                classNames.append(className)

            else:                
                # Regular handling (active if true, inactive if false)
                className = 'clickableBox '+ ('active' if store[index] else 'inactive')
                classNames.append(className)

        return store, classNames



    # Callback to update generally accessible store (To be honest there has to be a better way of doing this, instead of using the updating of a store to mark the update of an other....... look for it pls!)
    @callback(
        Output(ids.store(MATCH), 'data'),
        Input('bypass_temporary_store', 'data')
    )
    def update_store(store):
        # Change None to False
        store = {x:y if y != None else False for x,y in store.items()}
        # Change keys 24-Plate_48 to tf-fe (needed for the handling function)
        store['Plate_24'] = store.pop('Plate_24')
        store['Plate_48'] = store.pop('Plate_48')
        # print(store)
        return store





  

