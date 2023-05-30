from dash import Dash, Output, Input, State, html, dcc, callback, MATCH
from dash import dash_table
import uuid
from .genericInputWrapper import genericInputWrapper
import pandas as pd
from io import StringIO

generic_table_to_delete = pd.read_csv(StringIO('''X,empty,empty.1,empty.2,empty.3,empty.4,empty.5,empty.6,empty.7,empty.8,empty.9,empty.10,empty.11
F01,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty
F02,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty
F03,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty
F04,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty
F05,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty
F06,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty
F07,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty
F08,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty,empty'''))

class DataTableDisplay96WellAIO(html.Div):
    # Component
    class ids:
        table = lambda aio_id:{
        'component': 'DataTableDisplay96WellAIOTable',
        'subcomponent': 'table',
        'aio_id':aio_id
        }
        dropdown = lambda aio_id:{
        'component': 'DataTableDisplay96WellAIODropdown',
        'subcomponent': 'dropdown',
        'aio_id':aio_id
        }
        wrapping_div = lambda aio_id:{
        'component': 'DataTableDisplay96WellAIODropdown',
        'subcomponent': 'wrapping_div',
        'aio_id':aio_id
        }
        report_wrapper = lambda aio_id:{
        'component': 'DataTableDisplay96WellAIODropdown',
        'subcomponent': 'report_wrapper',
        'aio_id':aio_id
        }




    ids = ids

    def __init__(
        self,
        table = None,
        dropdown=False,
        dropdown_choices=None,
        initial_selection=None,
        display=True,
        reports=None,
        aio_id = None):
        """
        Generic component to display a 96 well plate. Gives the option to display a dropdown with a pre-defined initial selection. The aio_id refers to the dropdown's value
        """

        if table == None:
            table = generic_table_to_delete

        if dropdown_choices == None:
            dropdown_choices = []
        
        if aio_id is None:
            aio_id = str(uuid.uuid4())

        reports_string = '''Ops, something went wrong: 
        '''
        # If there are reports, structure the string
        # Check if there is something wrong!
        if reports and reports['something_wrong']:
            # If there are wells name to change, display that first
            if len(reports['to_change']) > 0:
                reports_string += f"""Please change the following sample name(s): {" ".join([x for x in reports["to_change"]])}"""
            # If total samples, and unique samples number differ, not every name is unique
            elif reports['total_samples'] != reports['unique_sample_names']:
                reports_string += 'The sample names are not unique'
            # There are blanks on the plate
            elif reports['blanks'] > 0:
                reports_string += 'Blanks were detected'
            else:
                reports_string += 'This plate is not valid'

        
        
        # Set data for table (extract prefixes)


        super().__init__([
            # Wrapping component
            genericInputWrapper([
                # Add dropdown only if required
                dcc.Dropdown(
                options=dropdown_choices,
                value=initial_selection,
                clearable=False,
                id=self.ids.dropdown(aio_id),
                style={'width': '15vw'}

                ) if dropdown else None,
                # Display data table
                dash_table.DataTable(
                    data = table.to_dict('records'), 
                    columns=[{'name': i, 'id': i} for i in table.columns], 
                    id=self.ids.table(aio_id),
                    css=[{'selector': 'table', 'rule': 'table-layout: fixed'}],
                    style_cell={'textAlign':'center', 'width':'8%'},
                    style_table={
                        'width': '100%',
                    },
                    

                    ),
                
                # Display report if any
                genericInputWrapper([
                    reports_string
                ],
                id=self.ids.report_wrapper(aio_id),
                style={'display':'block' if reports else 'none'},
                className = 'warning'
                ) #if report['something_wrong'] else None


            ], id=self.ids.wrapping_div(aio_id)
            , style={'display': 'flex' if display else 'none'}
            )
        ])





# Make a checkbox/button to access collapsable section to display the report








