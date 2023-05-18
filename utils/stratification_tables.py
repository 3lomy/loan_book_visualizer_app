#!/usr/bin/env python
# coding: utf-8

# In[1]:


from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template

# for table formatting
from utils.table_bars import data_bars 


# In[ ]:


def orig_term_table(table):
    
    # format table entries
    amount = dash_table.FormatTemplate.money(2).symbol_prefix("€")
    percentage = dash_table.FormatTemplate.percentage(2)
    months = dash_table.FormatTemplate.money(2).symbol_prefix("")
    
    original_term_table = html.Div([
                
        dash_table.DataTable(
                       
#             columns=[{"name": i, "id": i} for i in table.columns],           
             columns=[
#                  dict(name: "OrigTerm bins", id: "OrigTerm bins", type='text'),
                 {"name": "OrigTerm bins", "id": "OrigTerm bins", 'type':'text'},
                 {"name": "Current Bank Balance", "id": "CurBankBal", 'type':'numeric', 'format':amount},
                 {"name": "% Current Bank Balance", "id": "% CurBankBal", 'type':'numeric', 'format':percentage},
                 {"name": "Weighted Average Coupon", "id": "WeightedAverageCoupon", 'type':'numeric', 'format':percentage},
                 {"name": "Weighted Average Spread", "id": "WeightedAverageSpread", 'type':'numeric','format':percentage},
                 {"name": "Weighted Average Original Term", "id": "WeightedAverageOrigTerm", 'type':'numeric','format':months},
                 {"name": "Weighted Average Remaining Term", "id": "WeightedAverageRemTerm", 'type':'numeric', 'format':months},
             ],

            data=table.to_dict('rows'), # populate table with filtered data frame
#             editable=True,              # allow editing of data inside all cells
            filter_action="none",     # allow filtering of data by user ('native') or not ('none')
#             sort_action="native",       # enables data to be sorted per-column by user or not ('none')
#             sort_mode="single",         # sort across 'multi' or 'single' columns
            page_action="native",       # all data is passed to the table up-front or not ('none')
            page_current=0,             # page number that user is on
            page_size=15,                # number of rows visible per page
            style_cell={                # ensure adequate header width when text is shorter than cell's text
                'minWidth': 95, 
                'maxWidth': 95, 
                'width': 95,
                'whiteSpace': 'normal',
                'font_size': '18px',
                'color': 'black',
#                 'text_align': 'left'
                },
            style_data={                # overflow cells' content into multiple lines
                'whiteSpace': 'normal',
                'height': 'auto'
                },
            style_header={
                'backgroundColor': 'navy',
                'fontWeight': 'bold',
                'font_size': '20px',
                'color': 'white',
                'text_align': 'center'
            },

            style_data_conditional=(
                [   

                # format column type

                {'if':{
                    'column_type': 'text'  # 'text' | 'numeric' | 'any' | 'datetime'
                    },
                    'textAlign': 'center'
                },

                # format active cell    

                {'if':{
                    'state': 'active'  # 'active' | 'selected'
                    },

                    'border': '3px solid rgb(0, 116, 217)'
                },

                # format editable columns   

                {'if':{
                    'column_editable': False  # 'False' | 'True'
                    },

                    'cursor': 'not-allowed'
                },

                ]

                +
                
                [   
                # Highlighting top three values in a column 
                {
                    'if': {
                        'filter_query': '{{WeightedAverageSpread}} = {}'.format(i),
                        'column_id': 'WeightedAverageSpread',
                    },
#                     'fontWeight': 'bold',
                    'color': 'black',
                    'backgroundColor' : 'limegreen',   # seagreen | olivedrab | mediumseagreen | forestgreen | darkgreen
                }
                    
                for i in table['WeightedAverageSpread'].nlargest(3)
                    
                ]
                
                 +
                
                [   
                # Highlighting bottom value in a column 
                {
                    'if': {
                        'filter_query': '{{WeightedAverageSpread}} = {}'.format(i),
                        'column_id': 'WeightedAverageSpread',
                    },
#                     'fontWeight': 'bold',
                    'color': 'black',
                    'backgroundColor' : 'indianred',    # maroon | srimson | firebrick | darkred
                }
                    
                for i in table['WeightedAverageSpread'].nsmallest(1)
                    
                ]
                
                +
                
                # Adding data bars to numerical columns 
                data_bars(table, 'CurBankBal')

              
            ),
         )
    ])
    
    return original_term_table


# In[ ]:





# In[ ]:


def stratification_table(table, bins):
    
    # format table entries
    amount = dash_table.FormatTemplate.money(2).symbol_prefix("€")
    percentage = dash_table.FormatTemplate.percentage(2)
    months = dash_table.FormatTemplate.money(2).symbol_prefix("")
    
    strat_table = html.Div([
                
        dash_table.DataTable(
                       
#             columns=[{"name": i, "id": i} for i in table.columns],           
             columns=[
#                  dict(name: "OrigTerm bins", id: "OrigTerm bins", type='text'),
                 {"name": bins, "id": bins, 'type':'text'},
                 {"name": "Current Bank Balance", "id": "CurBankBal", 'type':'numeric', 'format':amount},
                 {"name": "% Current Bank Balance", "id": "% CurBankBal", 'type':'numeric', 'format':percentage},
                 {"name": "Weighted Average Coupon", "id": "WeightedAverageCoupon", 'type':'numeric', 'format':percentage},
                 {"name": "Weighted Average Spread", "id": "WeightedAverageSpread", 'type':'numeric','format':percentage},
                 {"name": "Weighted Average Original Term", "id": "WeightedAverageOrigTerm", 'type':'numeric','format':months},
                 {"name": "Weighted Average Remaining Term", "id": "WeightedAverageRemTerm", 'type':'numeric', 'format':months},
             ],

            data=table.to_dict('rows'), # populate table with filtered data frame
#             editable=True,              # allow editing of data inside all cells
            filter_action="none",     # allow filtering of data by user ('native') or not ('none')
#             sort_action="native",       # enables data to be sorted per-column by user or not ('none')
#             sort_mode="single",         # sort across 'multi' or 'single' columns
            page_action="native",       # all data is passed to the table up-front or not ('none')
            page_current=0,             # page number that user is on
            page_size=15,                # number of rows visible per page
            style_cell={                # ensure adequate header width when text is shorter than cell's text
                'minWidth': 95, 
                'maxWidth': 95, 
                'width': 95,
                'whiteSpace': 'normal',
                'font_size': '18px',
                'color': 'black',
#                 'text_align': 'left'
                },
            style_data={                # overflow cells' content into multiple lines
                'whiteSpace': 'normal',
                'height': 'auto'
                },
            style_header={
                'backgroundColor': 'navy',
                'fontWeight': 'bold',
                'font_size': '20px',
                'color': 'white',
                'text_align': 'center'
            },

            style_data_conditional=(
                [   

                # format column type

                {'if':{
                    'column_type': 'text'  # 'text' | 'numeric' | 'any' | 'datetime'
                    },
                    'textAlign': 'center'
                },

                # format active cell    

                {'if':{
                    'state': 'active'  # 'active' | 'selected'
                    },

                    'border': '3px solid rgb(0, 116, 217)'
                },

                # format editable columns   

                {'if':{
                    'column_editable': False  # 'False' | 'True'
                    },

                    'cursor': 'not-allowed'
                },

                ]

                +
                
                [   
                # Highlighting top three values in a column 
                {
                    'if': {
                        'filter_query': '{{WeightedAverageSpread}} = {}'.format(i),
                        'column_id': 'WeightedAverageSpread',
                    },
                    'fontWeight': 'bold',
                    'color': 'darkgreen',
                   # 'backgroundColor' : 'limegreen',   # seagreen | olivedrab | mediumseagreen | forestgreen | darkgreen
                }
                    
                for i in table['WeightedAverageSpread'].nlargest(3)
                    
                ]
                
                 +
                
                [   
                # Highlighting bottom value in a column 
                {
                    'if': {
                        'filter_query': '{{WeightedAverageSpread}} = {}'.format(i),
                        'column_id': 'WeightedAverageSpread',
                    },
                    'fontWeight': 'bold',
                    'color': 'maroon',
                   # 'backgroundColor' : 'indianred',    # maroon | srimson | firebrick | darkred
                }
                    
                for i in table['WeightedAverageSpread'].nsmallest(1)
                    
                ]
                
                +
                
                # Adding data bars to numerical columns 
                data_bars(table, 'CurBankBal')

              
            ),
         )
    ])
    
    return strat_table

