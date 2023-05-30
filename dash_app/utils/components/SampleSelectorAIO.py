import dash
from dash import callback, html, dash_table, dcc, Input, Output, State, MATCH, callback_context
import pandas as pd
import redis
import fakeredis
import uuid
from . import redis_store



# Basically I want this to be a reusable section to append at the bottom of tables or graphs. It can work with an array of input or a store (from which you derive a df)



class SampleSelectorAIO(html.Div):
    class ids:
        excluded_table = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'excluded_table',
            'aio_id': aio_id
        }

        included_table = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'included_table',
            'aio_id': aio_id
        }
        
        include_btn = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'include_btn',
            'aio_id': aio_id
        }
        
        exclude_btn = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'exclude_btn',
            'aio_id': aio_id
        }
        
        select_all_btn = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'select_all_btn',
            'aio_id': aio_id
        }

        store_selection = lambda aio_id: {
            'component': 'SampleSelectorAIO',
            'subcomponent': 'store_selection',
            'aio_id': aio_id
        }

    ids=ids
        
    def __init__(
            self, 
            selection=None, 
            store=None, 
            selected=None, 
            aio_id=None):
        """
        Tables for selection of samples, can be implemented for graphs and count tables. Either needs a 'Selection' eg an array of options, or a store from where to get a DataFrame's columns. Get the selection from the 'included_table' subcomponent. 
        """

        if aio_id is None:
            aio_id = str(uuid.uuid4())

        # Determine if there is a selection or a store or none       
        if selection:
            options = selection
        elif store:
            # THIS IS CONNECTED TO THE REDIS STORE SO TO PICK UP STUFF FROM THERE
            df = redis_store.load(store['df'])
            options = [x for x in df.columns]
        else:
            options = []

        # Remove GeneID if present
        options = [x for x in options if x != 'GeneID']

        # rework if anything is selected 
        if selected:
            unselected_options = [x for x in options if x not in selected]
            # If no unselected, put a none
            if len(unselected_options) < 1:
                unselected_options = ['None']
            selected_options = selected
        else:
            unselected_options = options
            selected_options = ['None']

        unselected_df = pd.DataFrame(unselected_options, columns=['Not-Selected'])
        selected_df = pd.DataFrame(selected_options, columns=['Selected'])
        
        super().__init__([
            
            # Structure for the selection
            html.Div([
                # First table for unselected
                html.Div(dash_table.DataTable(
                    unselected_df.to_dict('records'), 
                    row_selectable='multi',
                    id=self.ids.excluded_table(aio_id)
                    ), className='four columns'),

                # 3 buttons (select/deselect all - move to selected - move to unselected)
                html.Div([
                        # Button to move to selected
                        html.Button(
                            'Move to Selected', 
                            id=self.ids.include_btn(aio_id),
                            className='SubmitButtonComponentAIOButtonMedium'
                        ),

                        # Button to move to unselected
                        html.Button(
                            'Move to Unselected', 
                            id=self.ids.exclude_btn(aio_id),
                            className='SubmitButtonComponentAIOButtonMedium'
                        ),

                        # Select unselect all
                        html.Button(
                            'Select/Deselect all', 
                            id=self.ids.select_all_btn(aio_id),
                            className='SubmitButtonComponentAIOButtonMedium'
                        ),


                    ], 
                    className='three columns'),
                


                # Second table to be included
                html.Div(dash_table.DataTable(
                    selected_df.to_dict('records'), 
                    row_selectable='multi',
                    id=self.ids.included_table(aio_id)
                    ), className='four columns'),

            ], className='row'),

            # Store
            dcc.Store(id=self.ids.store_selection(aio_id), data={'options':options, 'selected':selected_options}) 
        ])

    def sort_columns(all_cols, this_list):
        #print('\n FROM SORT COLUMNS \n')
        #print(all_cols, this_list)
        #print('\n')

        # Understand what key is used (either Not-Selected or Selected)
        key = list(this_list[0].keys())[0]
        #print('key', key)
        this_list_values = [x[key] for x in this_list]

        to_return_list = [{key:x} for x in all_cols if x in this_list_values]

        return to_return_list
    
 

    @callback(
        Output(ids.included_table(MATCH), 'selected_rows'),
        Output(ids.excluded_table(MATCH), 'selected_rows'),
        Input(ids.select_all_btn(MATCH), 'n_clicks'),
        Input(ids.store_selection(MATCH), 'data'),
        State(ids.included_table(MATCH), 'selected_rows'),
        State(ids.excluded_table(MATCH), 'selected_rows'),
        State(ids.included_table(MATCH), 'data'),
        State(ids.excluded_table(MATCH), 'data'),
    )
    def select_deselect_all(click, store_selection, included_selection, excluded_selection, included_data, excluded_data):
        # If they're none, means it was just initialised and needs to get the empty lists
        if included_selection is None or excluded_selection is None:
            return [], []
        # If anything selected, deselect all, else select all

        if len(included_selection) < 1 and len(excluded_selection) < 1:
            included_selected = [x for x in range(len(included_data))]
            excluded_selected = [x for x in range(len(excluded_data))]
            return included_selected, excluded_selected
        else:
            return [], []



    @callback(
        Output(ids.included_table(MATCH), 'data'),
        Output(ids.excluded_table(MATCH), 'data'),
        Output(ids.store_selection(MATCH), 'data'),
        Input(ids.include_btn(MATCH), 'n_clicks'),
        Input(ids.exclude_btn(MATCH), 'n_clicks'),
        State(ids.store_selection(MATCH), 'data'),
        State(ids.included_table(MATCH), 'data'),
        State(ids.included_table(MATCH), 'selected_rows'),
        State(ids.excluded_table(MATCH), 'data'),
        State(ids.excluded_table(MATCH), 'selected_rows'),
        prevent_initial_call = True
    )
    def manage_swop(click1, click2, store_selection, included_data, included_selection, excluded_data, excluded_selection):
        # This unfortunately has to manage everything
        
        # Manipulate trigger string
        trigger = callback_context.triggered[0]['prop_id'].removeprefix('{').removesuffix('}.n_clicks')
        
        for bit in trigger.split(','):
            if 'subcomponent' in bit:
                s, btn = bit.split(':')
                # This is the name of the button that was clicked to call this callback (either move to selected or not selected)
                trigger = btn.strip('"')


        # Change selections to empty lists if they're none (eg empty lists)
        included_selection = included_selection or []
        excluded_selection = excluded_selection or []


        # If they clicked include
        if trigger == 'include_btn':
            # Handle empty selection
            if excluded_selection == []:
                #print('Nothing selected')
                raise dash.exceptions.PreventUpdate() # raise exception instead
                #return #included_data, excluded_data, store_selection # return everyhting
            else:
                # handle selection of 'none' 
                if len(excluded_selection) == 1:
                    if excluded_data[0]['Not-Selected'] == 'None':
                        return included_data, excluded_data, store_selection # return everything

                #print('excluded data', excluded_data, 'excluded selection',excluded_selection) #excluded selection is just the index of the list
                # Sort list for aesthetic reasons
                excluded_selection = sorted(excluded_selection)

                # List of rows to include in the included_data
                for x in excluded_selection:
                    # Include index in included data list
                    included_data.append({'Selected': excluded_data[x]['Not-Selected']})
                
                for x in excluded_selection[::-1]:
                    # Remove index from excluded data one (starting from behind so it doesn't mess up indexing)
                    excluded_data.pop(x)

                # Handle of 'None' in tables (if > 1 selected, remove None, if < 1 non selected include it)
                if len(included_data) > 1:
                    included_data = [x for x in included_data if x['Selected'] != 'None']

                if len(excluded_data) < 1:
                    excluded_data = [{'Not-Selected': 'None'}]

                
                #order lists
                included_data = SampleSelectorAIO.sort_columns(store_selection['options'], included_data)

                store_selection['selected'] = [x['Selected'] for x in included_data]
                
                #print('STORE SELECTION', store_selection)
                # included, incl_selection, excluded, excl_selection
                return included_data, excluded_data, store_selection #STORE



        # If they clicked exclude
        if trigger == 'exclude_btn':
            # If nothing selected, just return
            if included_selection == []:
                #print('Nothing selected')
                raise dash.exceptions.PreventUpdate()
                #return #included_data, excluded_data, store_selection # simply return everything as it is
            else:
                # handle selection of 'none' 
                if len(included_selection) == 1:
                    if included_data[0]['Selected'] == 'None':
                        return included_data, excluded_data, store_selection # return everything as it is


                # Sort list for aesthetic reasons
                included_selection = sorted(included_selection)

                # List of rows to include in the included_data
                for x in included_selection:
                    #print(included_data[x]['Selected'])

                    # Include index in included data list
                    excluded_data.append({'Not-Selected': included_data[x]['Selected']})
                
                for x in included_selection[::-1]:
                    # Remove index from excluded data one (starting from behind so it doesn't mess up indexing)
                    included_data.pop(x)

                # Handle of 'None' in tables (if > 1 selected, remove None, if < 1 non selected include it)
                if len(excluded_data) > 1:
                    excluded_data = [x for x in excluded_data if x['Not-Selected'] != 'None']

                if len(included_data) < 1:
                    included_data = [{'Selected': 'None'}]

                
                #print('included_data', included_data, 'included_selection',included_selection)
                
                #Order data
                #print('pre-excluded', excluded_data)
                excluded_data = SampleSelectorAIO.sort_columns(store_selection['options'], excluded_data)
                #print('post-excluded', excluded_data)

                store_selection['selected'] = [x['Selected'] for x in included_data]
                
                # included, incl_selection, excluded, excl_selection
                return included_data, excluded_data, store_selection




# This was the old callback

    # @callback(
    #     Output(ids.included_table(MATCH), 'data'),
    #     Output(ids.included_table(MATCH), 'selected_rows'),
    #     Output(ids.excluded_table(MATCH), 'data'),
    #     Output(ids.excluded_table(MATCH), 'selected_rows'),
    #     Output(ids.store_selection(MATCH), 'data'),
    #     Input(ids.include_btn(MATCH), 'n_clicks'),
    #     Input(ids.exclude_btn(MATCH), 'n_clicks'),
    #     Input(ids.select_all_btn(MATCH), 'n_clicks'),
    #     State(ids.store_selection(MATCH), 'data'),
    #     State(ids.included_table(MATCH), 'data'),
    #     State(ids.included_table(MATCH), 'selected_rows'),
    #     State(ids.excluded_table(MATCH), 'data'),
    #     State(ids.excluded_table(MATCH), 'selected_rows'),
    #     prevent_initial_call = True
    # )
    # def manage_swop(click1, click2, click3, store_selection, included_data, included_selection, excluded_data, excluded_selection):
    #     # This unfortunately has to manage everything
        
    #     # Manipulate trigger string
    #     trigger = callback_context.triggered[0]['prop_id'].removeprefix('{').removesuffix('}.n_clicks')
        
    #     for bit in trigger.split(','):
    #         if 'subcomponent' in bit:
    #             s, btn = bit.split(':')
    #             # This is the name of the button that was clicked to call this callback (either move to selected or not selected)
    #             trigger = btn.strip('"')


    #     # Change selections to empty lists if they're none (eg empty lists)
    #     included_selection = included_selection or []
    #     excluded_selection = excluded_selection or []


    #     # If they clicked include
    #     if trigger == 'include_btn':
    #         # Handle empty selection
    #         if excluded_selection == []:
    #             #print('Nothing selected')
    #             return included_data, included_selection, excluded_data, excluded_selection, store_selection # return everyhting
    #         else:
    #             # handle selection of 'none' 
    #             if len(excluded_selection) == 1:
    #                 if excluded_data[0]['Not-Selected'] == 'None':
    #                     return included_data, included_selection, excluded_data, excluded_selection, store_selection # return everything

    #             #print('excluded data', excluded_data, 'excluded selection',excluded_selection) #excluded selection is just the index of the list
    #             # Sort list for aesthetic reasons
    #             excluded_selection = sorted(excluded_selection)

    #             # List of rows to include in the included_data
    #             for x in excluded_selection:
    #                 # Include index in included data list
    #                 included_data.append({'Selected': excluded_data[x]['Not-Selected']})
                
    #             for x in excluded_selection[::-1]:
    #                 # Remove index from excluded data one (starting from behind so it doesn't mess up indexing)
    #                 excluded_data.pop(x)

    #             # Handle of 'None' in tables (if > 1 selected, remove None, if < 1 non selected include it)
    #             if len(included_data) > 1:
    #                 included_data = [x for x in included_data if x['Selected'] != 'None']

    #             if len(excluded_data) < 1:
    #                 excluded_data = [{'Not-Selected': 'None'}]

                
    #             #order lists
    #             included_data = SampleSelectorAIO.sort_columns(store_selection['options'], included_data)

    #             store_selection['selected'] = [x['Selected'] for x in included_data]
                
    #             #print('STORE SELECTION', store_selection)
    #             # included, incl_selection, excluded, excl_selection
    #             return included_data, [], excluded_data, [], store_selection #STORE



    #     # If they clicked exclude
    #     if trigger == 'exclude_btn':
    #         # If nothing selected, just return
    #         if included_selection == []:
    #             #print('Nothing selected')
    #             return included_data, included_selection, excluded_data, excluded_selection, store_selection # simply return everything as it is
    #         else:
    #             # handle selection of 'none' 
    #             if len(included_selection) == 1:
    #                 if included_data[0]['Selected'] == 'None':
    #                     return included_data, included_selection, excluded_data, excluded_selection, store_selection # return everything as it is


    #             # Sort list for aesthetic reasons
    #             included_selection = sorted(included_selection)

    #             # List of rows to include in the included_data
    #             for x in included_selection:
    #                 #print(included_data[x]['Selected'])

    #                 # Include index in included data list
    #                 excluded_data.append({'Not-Selected': included_data[x]['Selected']})
                
    #             for x in included_selection[::-1]:
    #                 # Remove index from excluded data one (starting from behind so it doesn't mess up indexing)
    #                 included_data.pop(x)

    #             # Handle of 'None' in tables (if > 1 selected, remove None, if < 1 non selected include it)
    #             if len(excluded_data) > 1:
    #                 excluded_data = [x for x in excluded_data if x['Not-Selected'] != 'None']

    #             if len(included_data) < 1:
    #                 included_data = [{'Selected': 'None'}]

                
    #             #print('included_data', included_data, 'included_selection',included_selection)
                
    #             #Order data
    #             #print('pre-excluded', excluded_data)
    #             excluded_data = SampleSelectorAIO.sort_columns(store_selection['options'], excluded_data)
    #             #print('post-excluded', excluded_data)

    #             store_selection['selected'] = [x['Selected'] for x in included_data]
                
    #             # included, incl_selection, excluded, excl_selection
    #             return included_data, [], excluded_data, [], store_selection


    #     # If they clicked to select/deselect all trigger
    #     if trigger == 'select_all_btn':
    #         #print(included_selection, excluded_selection)
    #         # If anything selected, deselect all, else select all
    #         if len(included_selection) > 0 or len(excluded_selection) > 0:
    #             return included_data, [], excluded_data, [], store_selection
    #         else:
    #             included_selected = [x for x in range(len(included_data))]
    #             excluded_selected = [x for x in range(len(excluded_data))]
    #             return included_data, included_selected, excluded_data, excluded_selected, store_selection

    #     #print(trigger, type(trigger))
