from dash import callback, html, dash_table, dcc, Input, Output, State, MATCH, callback_context
import pandas as pd
import redis
import fakeredis
import uuid
from . import redis_store

# This is basically a reusable section to add on top of graphs that require samples specific to X and Y to be selected. It is going to be simply a double dropdown

class GraphXYSelectorAIO(html.Div):
    class ids:
        selectionX = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'selectionX',
            'aio_id': aio_id
        }

        selectionY = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'selectionY',
            'aio_id': aio_id
        }

        selectionStore = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'selectionStore',
            'aio_id': aio_id
        }

    ids=ids


    def __init__(
            self, 
            selection=None, 
            selectX=None, 
            selectY=None, 
            aio_id=None):
        """Reusable section to add on top of graphs that require samples specific to X and Y to be selected. It is going to be simply a double dropdown"""

        if aio_id is None:
            aio_id = str(uuid.uuid4())
        
        # If 'Unnamed: 0' in selection, replace it with 'geneid'
        if 'Unnamed: 0' in selection:
            selection.remove('Unnamed: 0')
            selection.insert(0, 'GeneID')
            

        # If selectX or selectY are not assigned, assign them to first and second cols of selection
        if selectX is None and selectY is None:
            if len(selection) > 3:
                selectX = selection[1]
                selectY = selection[2]
            else:
                selectX, selectY = selection[0], selection[0]

        if selectX is None:
            selectX = selection[1] or selection[0]
        
        if selectY is None:
            selectY = selection[1] or selection[0]
        

        super().__init__([
            html.Div(
                [
                    'Select for the X axis',
                    dcc.Dropdown(selection, selectX, clearable=False,  id=self.ids.selectionX(aio_id))
                ],
                className='five columns'),

            html.Div(
                [
                    'Select for the Y axis',
                    dcc.Dropdown(selection, selectY, clearable=False, id=self.ids.selectionY(aio_id))
                    ],
                className='five columns'),

            dcc.Store(id=self.ids.selectionStore(aio_id))

        ], className='row')
    
    @callback(
        Output(ids.selectionStore(MATCH), 'data'),
        Input(ids.selectionX(MATCH), 'value'),
        Input(ids.selectionY(MATCH), 'value'),
        State(ids.selectionX(MATCH), 'value'),
        State(ids.selectionY(MATCH), 'value'),
    )
    def save_selection(x_trigger, y_trigger, x_val, y_val):
        return {'x':x_val, 'y':y_val}




