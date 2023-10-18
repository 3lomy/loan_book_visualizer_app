#!/usr/bin/env python
# coding: utf-8

# ### Author: Elom Kwamin, FRM
# Date: 20.09.2023

# ### 0. importing required modules

# In[1]:


# import dash modules
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
import dash_loading_spinners as dls

# import graphing modules
import plotly.express as px
import plotly.graph_objects as go

# from dash.dash_table import FormatTemplate
from dash_bootstrap_templates import ThemeChangerAIO, template_from_url # for switching between templates
# from dash_bootstrap_templates import ThemeSwitchAIO
from dash.exceptions import PreventUpdate 


# import custom modules
from utils.stratification_tables import * # for creating tables
from utils.data_analyzer import *  # for data manipulation
# from utils.table_bars import * # for table formatting

# import windows modules
import base64
import io

# import general modules
import json
import numpy as np
import pandas as pd


# ### 1. setting the dash bootstap theme for the app layout & instantiating Dash

# In[2]:


dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates@V1.0.4/dbc.min.css"

FONT_AWESOME = ("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css")

# app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, dbc.icons.BOOTSTRAP])
#note that the icons could be dbc.icons.FONT_AWESOME

# app = Dash(__name__, external_stylesheets=[dbc.themes.MORPH, FONT_AWESOME, dbc.icons.BOOTSTRAP])

app = Dash(__name__,
           external_stylesheets=[dbc.themes.BOOTSTRAP, FONT_AWESOME, dbc.icons.BOOTSTRAP],
          meta_tags=[{'name': 'viewport', 'content': 'width=device-width, initial-scale=1,'}]) # maximum-scale=1.2, minimum-scale=0.5,'}])

app.title = "Loan Book Visualizer"

server = app.server # required line before upload to render

# app = Dash(__name__, external_stylesheets=[dbc.themes.SLATE, FONT_AWESOME, dbc.icons.BOOTSTRAP])

themes_options = [
    {"label": "Slate", "value": dbc.themes.SLATE},
    {"label": "Flatly", "value": dbc.themes.FLATLY},
    {"label": "Darkly", "value": dbc.themes.DARKLY},
    {"label": "Minty", "value": dbc.themes.MINTY},
    {"label": "Morph", "value": dbc.themes.MORPH},
    {"label": "Spacelab", "value": dbc.themes.SPACELAB},
    {"label": "Sketchy", "value": dbc.themes.SKETCHY},
]

theme_changer = ThemeChangerAIO(aio_id="theme",radio_props={ "value": dbc.themes.MORPH, "options": themes_options}, )


# theme_switch = ThemeSwitchAIO(
#     aio_id="theme", themes=[dbc.themes.MORPH, dbc.themes.SLATE])


# ### 2. global variables declaration

# In[3]:


# dictionary variable for storing stratification tables to be written to excel upon download.
OUTPUT_STRATIFICATION_TABLES = {}


# In[4]:


#load default input file
DEFAULT_DF = pd.read_excel('data/loan_portfolio_orig.xlsx', skiprows=[0]) 


# ### 3. dash app layout

# #### 3.1 creating cards for charts page [page 1]

# In[5]:


"""
===========================================================================================================================
CREATING CARDS FOR GRAPHS SHEET
===========================================================================================================================
"""
# 1. original term card

original_term_card = html.Div([

        html.H5("Original Term Strats", className="m-0 text-center text-sm-left", style={"display": "inline"}),
    
        dbc.RadioItems(
            id="input-radio-selected-original-term",
            options=[
                {'label': 'EUR', 'value': 'Amount'},
                {'label': '%', 'value': 'Percentage'},
            ],
            value='Amount',
            inline=True,
        ),

           dcc.Dropdown(
                id="input-original-term-range",
                options=[ 
                    {"label": "12 months interval", "value": 12},
                    {"label": "24 months interval", "value": 24},
                    {"label": "36 months interval", "value": 36},
                    {"label": "48 months interval", "value": 48},
                ],
                value=24,
            ),

        dcc.Graph(id="output-original-term-chart", figure={}, className="m-0"),
    
            dbc.Row([
                html.H6("Current balances distribution by original term"),
            ]),

],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)





# 2. remaining term card

remaining_term_card = html.Div([

        html.H5("Remaining Term Strats", className="m-0 text-center text-sm-left", style={"display": "inline"}),
             
        dbc.RadioItems(
           id="input-radio-selected-remaining-term",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            id="input-remaining-term-range",
            options=[ 
                {"label": "12 months interval", "value": 12},
                {"label": "24 months interval", "value": 24},
                {"label": "36 months interval", "value": 36},
                {"label": "48 months interval", "value": 48},],
            value=24,
        ),
        
#         html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-remaining-term-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
    
        dbc.Row([
            html.H6("Current balances distribution by remaining term"),
        ]),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)

# 3. loan seasoning card

seasoning_card = html.Div(
    [
#         html.H6("Seasoning Strats", className="mb-2"),
        html.H5("Season Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-seasoning",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            id="input-season-range",
            
            options=[ 
                {"label": "12 months interval", "value": 12},
                {"label": "24 months interval", "value": 24},
                {"label": "36 months interval", "value": 36},
                {"label": "48 months interval", "value": 48},],
            value=12,
            
            
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-season-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
         dbc.Row([
            html.H6("Current balances distribution by seasoning"),
        ]),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)
    
    
# 4. current coupon card

current_coupon_card = html.Div(
    [
#         dbc.CardHeader("Coupon Strats"),
        html.H5("Coupon Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-coupon",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            id="input-coupon-range",
            options=[
                {"label": "2.5%", "value": 0.025, "disabled": False}, #f"{cagr_result:.1%}"
                {"label": "5.0%", "value": 0.05, "disabled": False},
                {"label": "7.5%", "value": 0.075, "disabled": False},
                {"label": "10.0%", "value": 0.10, "disabled": False},
            ],
            value=0.025,
            
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-coupon-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by coupon"),
        ]),
        
#         dbc.CardFooter("Current balances distribution by coupon"),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)    



# 5. spread to index card

spread_card = html.Div(
    [
#         dbc.CardHeader("Spread to Index Strats"),
        html.H5("Spread to Index Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-spread",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            options=[
                {"label": "0.2%", "value": 0.002, "disabled": False}, #f"{cagr_result:.1%}"
                {"label": "0.25%", "value": 0.0025, "disabled": False},
                {"label": "0.5%", "value": 0.005, "disabled": False},
                {"label": "1.0%", "value": 0.01, "disabled": False},
            ],
            value=.005,
            id="input-spread-range",
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-spread-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by spread"),
        ]),
        
#         dbc.CardFooter("Current balances distribution by spread"),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
) 


# 6. LTV card

ltv_card = html.Div(
    [
#         dbc.CardHeader("Loan to Value Strats"),
        html.H5("Loan to Value Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-ltv",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            options=[
                {"label": "5.0%", "value": 0.05, "disabled": False}, #f"{cagr_result:.1%}"
                {"label": "10.0%", "value": 0.1, "disabled": False},
                {"label": "15.0%", "value": 0.15, "disabled": False},
                {"label": "20.0%", "value": 0.2, "disabled": False},
                {"label": "25.0%", "value": 0.25, "disabled": False},
                {"label": "50.0%", "value": 0.5, "disabled": False},
            ],
            value=.15,
            id="input-ltv-range",
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-ltv-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by LTV"),
        ]),
        
        
#         dbc.CardFooter("Current balances distribution by LTV"),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
) 

# 7. original balance card

original_balance_card = html.Div(
    [
#         dbc.CardHeader("Original Balance Strats"),
        html.H5("Original Balance Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-original-balance",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            options=[
                {"label": "100K", "value": 100000, "disabled": False}, 
                {"label": "150K", "value": 150000, "disabled": False},
                {"label": "200K", "value": 200000, "disabled": False},
                {"label": "250K", "value": 250000, "disabled": False},
            ],
            value=100000,
            id="input-original-balance-range",
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-original-balance-chart", figure={}),
        color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by original balance"),
        ]),
        
#         dbc.CardFooter("Current balances distribution by original balance"),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
) 



# 8. current balance card

current_balance_card = html.Div(
    [
#         dbc.CardHeader("Current Balance Strats"),
        html.H5("Current Balance Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-current-balance",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            options=[
                {"label": "100K", "value": 100000, "disabled": False}, 
                {"label": "150K", "value": 150000, "disabled": False},
                {"label": "200K", "value": 200000, "disabled": False},
                {"label": "250K", "value": 250000, "disabled": False},
            ],
            value=100000,
            id="input-current-balance-range",
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-current-balance-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by current balance"),
        ]),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
) 

# 9. Region card

region_card = html.Div([

        html.H5("State Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-region",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            options = [
                {"label": "state strats by current bal", "value": "CurBankBal", "disabled": False}, 
                {"label": "state strats by original bal", "value": "OrigBankBal", "disabled": False},
                {"label": "state strats by weighted average seasoning", "value": "WAvgSeason", "disabled": False}, # weighted average seasoning
#                 {"label": "state strats by remainng term", "value": "RemTerm", "disabled": False}, # put Wa remterm
            ],
            value="CurBankBal",
            
            id="input-region",
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-region-chart", figure={}),
             color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by state"),
        ]),
  
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
) 
    
    
    
# 10. Top loans card

top_loans_card = html.Div([
        
        html.H5("Top loans Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-top-loans",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        dcc.Dropdown(
            options=[
                {"label": "top 5", "value": 5, "disabled": False}, 
                {"label": "top 10", "value": 10, "disabled": False},
                {"label": "top 20", "value": 20, "disabled": False},
                {"label": "top 50", "value": 50, "disabled": False},
            ], 
            value=5,
            id="input-top-loans",
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-top-loans-chart", figure={}),
         color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        html.P(id="output-top-loans-info"),
        
        dbc.Row([
            html.H6("Current balances distribution by top loans"),
        ]),
        
#         dbc.CardFooter("Current balances distribution by top loans"), 
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)             



# 11. Origination Year

origination_year_card = html.Div([        
        
        html.H5("Origination Year Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-origination-year",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-origination-year-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by origination year"),
        ]),
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
) 


# 12. Maturity Year

maturity_year_card = html.Div([       

        html.H5("Maturity Year Strats"),
        
        dbc.RadioItems(
           id="input-radio-selected-maturity-year",
           options=[
               {'label': 'EUR', 'value': 'Amount'},
               {'label': '%', 'value': 'Percentage'},
           ],
           value='Amount',
           inline=True,
        ),
        
        html.Br(), 
        
        dls.Hash(
        dcc.Graph(id="output-maturity-year-chart", figure={}),
            color="#435278",
            speed_multiplier=2,
            size=100,
        ),
        
        dbc.Row([
            html.H6("Current balances distribution by maturity year"),
        ]),       
        
    ],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
) 


# #### 3.2 creating tables for tables page [page 2]

# In[6]:


"""
===========================================================================================================================
CREATING CARDS FOR TABLES SHEET
===========================================================================================================================
"""
remaining_term_table = html.Div([

    html.H4("Current balance stratification by remaining term"),
        
    dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-remaining-term-range-table",
                    options=[ 
                        {"label": "12 months interval", "value": 12},
                        {"label": "24 months interval", "value": 24},
                        {"label": "36 months interval", "value": 36},
                        {"label": "48 months interval", "value": 48},],
                    value=24,
                    ), 
            ]),width=3, xs=12, sm=12, lg=3),
    ],
    justify = "left"),   
    
    dls.Roller(
    html.Div(id='remaining-term-table-placeholder', style={"overflow": "scroll"}),
        color="#435278",
        width=100,
    ),

],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }

)

original_term_table = html.Div([
    
    html.H4("Current balance stratification by original term"),
        
    dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-original-term-range-table",
                    options=[ 
                        {"label": "12 months interval", "value": 12},
                        {"label": "24 months interval", "value": 24},
                        {"label": "36 months interval", "value": 36},
                        {"label": "48 months interval", "value": 48},],
                    value=24,
                    ), 
            ]),width=3, xs=12, sm=12, lg=3),
    ],
    justify = "left"),   
    
    dls.Roller(
    html.Div(id='original-term-table-placeholder', style={"overflow": "scroll"}), 
        color="#435278",
        width=100,
    ),
    
],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }

)

seasoning_term_table = html.Div([
    
    html.H4("Current balance stratification by seasoning"),
        
     dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-seasoning-range-table",
                    options=[ 
                        {"label": "12 months interval", "value": 12},
                        {"label": "24 months interval", "value": 24},
                        {"label": "36 months interval", "value": 36},
                        {"label": "48 months interval", "value": 48},],
                    value=12,
                    ), 
            ]),width=3, xs=12, sm=12, lg=3),
    ],
    justify = "left"),   
    
    dls.Roller(
    html.Div(id='seasoning-table-placeholder', style={"overflow": "scroll"}), 
        color="#435278",
        width=100,
    ),
    
],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)

coupon_term_table = html.Div([
    
     html.H4("Current balance stratification by coupon"),
    
    dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-coupon-range-table",
                    options=[
                        {"label": "2.5%", "value": 0.025, "disabled": False}, #f"{cagr_result:.1%}"
                        {"label": "5.0%", "value": 0.05, "disabled": False},
                        {"label": "7.5%", "value": 0.075, "disabled": False},
                        {"label": "10.0%", "value": 0.10, "disabled": False},
                    ],
                    value=0.025,
                    ), 
            ]),width=3, xs=12, sm=12, lg=3),
    ],
    justify = "left"),   
    
    dls.Roller(
    html.Div(id='coupon-table-placeholder', style={"overflow": "scroll"}),  
        color="#435278",
        width=100,
    ),
    
],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)

spread_term_table = html.Div([
    
    html.H4("Current balance stratification by Spread"),
    
    dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-spread-range-table",
                    options=[
                        {"label": "0.2%", "value": 0.002, "disabled": False}, #f"{cagr_result:.1%}"
                        {"label": "0.25%", "value": 0.0025, "disabled": False},
                        {"label": "0.5%", "value": 0.005, "disabled": False},
                        {"label": "1.0%", "value": 0.01, "disabled": False},
                    ],
                    value=.005,
                    ), 
            ]),width=3, xs=12, sm=12, lg=3),
    ],
    justify = "left"),   
    
    dls.Roller(
    html.Div(id='spread-table-placeholder', style={"overflow": "scroll"}),
        color="#435278",
        width=100,
    ),
    
],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)

ltv_term_table = html.Div([
    
    html.H4("Current balance stratification by LTV"),
        
    dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-ltv-range-table",
                    options=[
                        {"label": "5.0%", "value": 0.05, "disabled": False}, #f"{cagr_result:.1%}"
                        {"label": "10.0%", "value": 0.1, "disabled": False},
                        {"label": "15.0%", "value": 0.15, "disabled": False},
                        {"label": "20.0%", "value": 0.2, "disabled": False},
                        {"label": "25.0%", "value": 0.25, "disabled": False},
                        {"label": "50.0%", "value": 0.5, "disabled": False},
                    ],
                    value=.15,
                    ), 
            ]),width=3, xs=12, sm=12, lg=3),
    ],
    justify = "left"), 
    
    dls.Roller(
    html.Div(id='ltv-table-placeholder', style={"overflow": "scroll"}),
        color="#435278",
        width=100,
    ),
    
],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)

original_balance_term_table = html.Div([
    
    html.H4("Current balance stratification by original balance"),
        
     dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-original-balance-range-table",
                    options=[
                        {"label": "100K", "value": 100000, "disabled": False}, 
                        {"label": "150K", "value": 150000, "disabled": False},
                        {"label": "200K", "value": 200000, "disabled": False},
                        {"label": "250K", "value": 250000, "disabled": False},
                    ],
                    value=100000,
                ), 
            ]),width=3, xs=12, sm=12, lg=3),
        ],
        justify = "left"), 
    
    dls.Roller(
    html.Div(id='original-balance-table-placeholder', style={"overflow": "scroll"}),
        color="#435278",
        width=100,
    ),
    
],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)

current_balance_term_table = html.Div([
    
    html.H4("Current balance stratification by current balance"),

    dbc.Row([
        dbc.Col(
            dbc.InputGroup([
                dbc.InputGroupText("Select bins:",style={'font-weight': 'bold', "text-align": "center"}),
                dbc.Select(
                   id="input-current-balance-range-table",
                    options=[
                        {"label": "100K", "value": 100000, "disabled": False}, 
                        {"label": "150K", "value": 150000, "disabled": False},
                        {"label": "200K", "value": 200000, "disabled": False},
                        {"label": "250K", "value": 250000, "disabled": False},
                    ],
                    value=100000,
                ), 
            ]),width=3, xs=12, sm=12, lg=3),
    ],
    justify = "left"), 
    
    dls.Roller(
    html.Div(id='current-balance-table-placeholder', style={"overflow": "scroll"}),
        color="#435278",
        width=100,
    ),
    
],style={"border": "0px ridge silver",  # outset, groove
             'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px"  }
)


# #### 3.3 creating the side bar

# In[7]:


# the style arguments for the sidebar. We use position:fixed and a fixed width
SIDEBAR_STYLE = {
    "margin-top":"10px",
    "margin-bottom":"10px",
    "margin-left":"10px",
    "margin-right":"10px",
#     "text-align":"center",
}

# the styles for the main content position it to the right of the sidebar and
# add some padding.


CONTENT_STYLE = {
    #"position": "fixed",
#     "margin-top":"5rem",
#     "margin-left": "5rem",
#     "margin-right": "5rem",
    "padding": "2rem 2rem",
}

sidebar = html.Div(
    [
        html.Hr(),
        
        dbc.Row([
            
            dbc.Col([
                
                # these are utilized in the callback to render the pages
                dbc.Nav([
                    dbc.NavLink("Home", href="/", active="exact"),
                    dbc.NavLink("Charts", href="/charts-page", active="exact"),
                    dbc.NavLink("Tables", href="/tables-page", active="exact"),
                    
#                     dbc.NavLink("Home", href="/", active="exact"),
#                     dbc.NavLink("Graphs", href="/page-1", active="exact"),
#                     dbc.NavLink("Tables", href="/page-2", active="exact"),
                ],
                vertical=True,
                pills=True,
                ),
                
             ], width=12), #xs=3, sm=3, md=3, lg=12, xl=12),
            
        ]),

        html.Hr(),
    ],
    
    style=SIDEBAR_STYLE,
)


# #### 3.4 home page content

# In[8]:


green_button_style = {'background-color': 'mediumseagreen',
                      'color': 'black',
                      'height': '50px',
                      'width': '100%',
                      'lineHeight': '60px',
                      'borderWidth': '4px',
                      'borderStyle': 'dashed',
                      'borderRadius': '5px',
                      'textAlign': 'center',
                      'margin': '10px',
                     }

red_button_style = {'background-color': 'indianred',
                    'color': 'white',
                    'height': '50px',
                    'width': '100%',
                    'lineHeight': '60px',
                    'borderWidth': '4px',
                    'borderStyle': 'dashed',
                    'borderRadius': '5px',
                    'textAlign': 'center',
                    'margin': '10px',
                   }

contact_style = {
    'margin-right': '5px',
    'font-size': '18px',
    'color': '#666666',
    'margin-top': '10px',
    'display': 'flex',
    'align-items': 'center',  # Aligns the logo and text vertically
    'justify-content': 'center'  # Centers the text horizontally
}


header_style = {
    'background': 'linear-gradient(to right, #b0c4de, #1e90ff)',
    'padding': '20px 15px',  # Increased padding for top and bottom, decreased for left and right
    'text-align': 'center',
    'font-size': '40px',
    'font-weight': 'bold',
    'color': '#333333',
    'box-shadow': '0 8px 12px rgba(0, 0, 0, 0.2)',
    'font-family': 'Goudy Old Style, sans-serif'  # Custom font
}


home_page_content = dbc.Container([ 
        
        html.Hr(),

        dbc.Row([
            theme_changer,
        ],
        justify = "end"
        ),
        
        html.Br(),
        
        dbc.Row([
            
            dbc.Col([
            
                html.H5('User file input:', style={'textAlign':'right', "margin-top":"5px","padding":"10px"}),
                
            ], width=2),
            
            dbc.Col(
                [
                    dbc.Card(
                       dcc.Upload(id='upload-data', children=html.Div(['Drag and Drop or ',html.A('Select Files')]),
                                  style = red_button_style, disabled=True),
                    )
                ], width=6 #xs=12, sm=12, md=12, lg=6, xl=6 
            ),
         ],
        justify = "center"
        ),

        html.Br(),
        
        html.P(id="output-user-input-info"),  # signals if default data or user data is being displayed

        dbc.Row(
            [
            dbc.Col([
                html.Div(id='output-data-upload'), # if we want to output it into a dcc.Table
            ], width= 12), #responsive column size #xs=10, sm=10, md=10, lg=10, xl=12),
                
            ], 
            justify = "center"
        ),   


        html.Br(),

        html.Hr(),
               
    ],
    
    fluid=True,
    className="dbc",
    id="home-page-content",
)    


# #### 3.5 page one content

# In[9]:


page_one_content = dbc.Container([
    
    html.Hr(),
        
#     theme_changer,
        
    dbc.Row([
        
        dbc.Col(theme_changer, align="start"),
        
        dbc.Col(dbc.Button(
#             children = [html.I(className="fa fa-download mr-1"), "Download"],
            children = [html.I(className="fa fa-cloud-download mr-1"), "Download"],
            
            id = "btn-charts",
            href="",
            download="",
            external_link=True,
            color="primary", # info
            size="sm",
            className="me-md-2",
            n_clicks=0,
            style={
                    "marginLeft": "80%",
#                     "width": "20%",
#                     "height": "50%",
                    "fontSize": "1em",
                    "background-color": "white",
                    "color": "black",
                    "border-radius": "4px",
                    "border": "4px solid dodgerblue",
                }
        ),align="end"
#         ),
        ),
        
        dcc.Download(id="download-charts"),
        
    ],
    
        justify="center"
    
    ), 
        
    html.Br(),
    
    dbc.Row(
        [
            dbc.Col([original_term_card], xs=12, sm=12, md=6, lg=6, xl=5),
            dbc.Col([remaining_term_card], xs=12, sm=12, md=6, lg=6, xl=5),
        ],
        justify = "around",
        style={"height": "80"},     
    ),
                
    html.Br(),
             
    html.Hr(),
        
    html.Br(),
        
    dbc.Row([
        dbc.Col([seasoning_card], xs=12, sm=12, md=6, lg=6, xl=5),
        dbc.Col([current_coupon_card], xs=12, sm=12, md=6, lg=6, xl=5),
        ],
        justify = "around",
        style={"height": "80"}, 
    ),
        
    html.Br(),
             
    html.Hr(),
        
    html.Br(),
        
    dbc.Row([
        dbc.Col([spread_card], xs=12, sm=12, md=6, lg=6, xl=5),
        dbc.Col([ltv_card], xs=12, sm=12, md=6, lg=6, xl=5),
        ],
        justify = "around",
        style={"height": "80"}, 
    ),
           
    html.Br(),
             
    html.Hr(),
        
    html.Br(),
        
    dbc.Row([
        dbc.Col([original_balance_card], xs=12, sm=12, md=6, lg=6, xl=5),
        dbc.Col([current_balance_card], xs=12, sm=12, md=6, lg=6, xl=5),
        ],
        justify = "around",
        style={"height": "80"}, 
    ),
        
    html.Br(),
             
    html.Hr(),
        
    html.Br(),
        
    dbc.Row([
        dbc.Col([region_card], xs=12, sm=12, md=6, lg=6, xl=5),
        dbc.Col([top_loans_card], xs=12, sm=12, md=6, lg=6, xl=5),
        ],
        justify = "around",
        style={"height": "80"}, 
    ),
        
    html.Br(),
             
    html.Hr(),
        
    html.Br(),
        
    dbc.Row([
        dbc.Col([origination_year_card], xs=12, sm=12, md=6, lg=6, xl=5),
        dbc.Col([maturity_year_card], xs=12, sm=12, md=6, lg=6, xl=5),
        ],
        justify = "around",
        style={"height": "80"}, 
    ),   
    
    html.Br(),
        
    html.Br(),
        
#     html.Div(id="populate-table"),
        
    ],
    
    fluid=True,
    className="dbc",
    id="page-one-content",
#     style = CONTENT_STYLE
)


# #### 3.6 page two content - tables

# In[10]:


page_two_content = dbc.Container([
    
    html.Hr(),
        
    dbc.Row([
        
        dbc.Col(theme_changer, align="start"),
        
        dbc.Col(dbc.Button(
            children = [html.I(className="fa fa-cloud-download mr-1"), "Download"],
            
            id = "btn-tables-csv",
            href="",
            download="",
            external_link=True,
            color="primary", # info
            size="sm",
            className="me-md-2",
            n_clicks=0,
            style={
                    "margin-left": "80%",
                    "fontSize": "1em",
                    "background-color": "white",
                    "color": "black",
                    "border-radius": "4px",
                    "border": "4px solid dodgerblue",
                }
        ),align="end"
        ),
        
        dcc.Download(id="download-datafame-tables-csv"),        
        
    ],justify="end"),     
        
    html.Br(),
            
### STRATIFICATION TABLES

# 1. remaining term stratifications
    
    remaining_term_table, 
        
    html.Br(),

# 2. original term stratifications
    
    original_term_table,
        
    html.Br(),
        
# 3. seasoning stratifications
        
    seasoning_term_table,
        
    html.Br(),
        
# 4 coupon stratifications
    
    coupon_term_table,
        
    html.Br(),
        
# 5 spread to index startifications
        
    spread_term_table,
        
    html.Br(),
        
# 6. LTV stratifications
        
    ltv_term_table,
        
    html.Br(),
        
# 7. Original balance stratifications
        
    original_balance_term_table,
        
    html.Br(),
        
# 8. Current balance stratifications
        
    current_balance_term_table,
        
    html.Br(),
      
    ],
    
    fluid=True,
    className="dbc",
    id="page-two-content",
)


# #### 3.7 main layout of app

# In[11]:


# set up content of the web application
content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

# controlled by a callback function => render_page_content
# storage could be local or memory


#app.layout = html.Div([dcc.Store(id='store-info', storage_type='session'),
#                       dcc.Location(id="url"), 
#                       sidebar, 
#                       content]) 

app.layout =  html.Div([
    dcc.Store(id='store-info', storage_type='session'),
    dcc.Location(id="url"), 
    
    dbc.Row([     
            html.Div([
                html.H1('LOAN BOOK VISUALIZER', style = {'textAlign' : 'center', 
                                                         "margin-top":"40px",
                                                         "margin-bottom":"30px",
                                                         "fontWeight": "bold",
                                                        }),    
        ],style={"border": "5px ridge silver",  # outset, groove
#              'box-shadow': '10px 10px 10px 10px rgba(0, 0, 0, 0.2)',
             'background':'light grey',
             "padding": "10px" ,
             }),
                
    ], className='row sticky-top', 
        style={'background': 'linear-gradient(to right, #b0c4de, #1e90ff)'}),
    
    
    dbc.Row([
        
        dbc.Col([
            
            html.I(className="bi bi-envelope-fill me-1 text-primary text-center"),
                    html.A("data.with.elom@gmail.com", 
#                            href="http://linkedin.com/in/elom-tettey-kwamin-frm®-53029468",
#                            target="_blank", 
                           style={'text-decoration':'none', "padding": "2px", "font-weight": "bold",
                                 "margin-right":"5px"},
                          ),
            
            html.I(className="bi bi-youtube me-1 text-primary text-center"),
                    html.A("Data with Elom", 
                           href="https://www.youtube.com/@DatawithElom",
                           target="_blank", 
                           style={'text-decoration':'none', "padding": "2px", "font-weight": "bold",
                                 "margin-right":"5px"},
                          ),
            
             html.I(className="bi bi-instagram me-1 text-primary text-center"),
                    html.A("data.with.elom", 
                           href="http://instagram.com/data.with.elom",
                           target="_blank", 
                           style={'text-decoration':'none', "padding": "2px", "font-weight": "bold",
                                  "margin-right":"5px"},
                          ),
            
             html.I(className="bi bi-linkedin me-1 text-primary text-center"),
                    html.A("Elom Kwamin, FRM", 
                           href="http://linkedin.com/in/elom-tettey-kwamin-frm®-53029468",
                           target="_blank", 
                           style={'text-decoration':'none', "padding": "2px", "font-weight": "bold",
                                 "margin-right":"5px"},
                          ),
            
            
        ],style={'text-align':"right"}),
    ], justify="right"),
    
    dbc.Row([
        dbc.Col([
            html.Div([
                sidebar,
            ],
            style={"border": "0px ridge silver",  # outset, groove
             'background':'light grey',
             "padding": "10px" ,
             }),
        ], lg={'size':2, 'offset':0}, sm=12),
        
        dbc.Col([
            html.Div([
                content,
            ]),
        ], lg={'size':10, 'offset':0}, sm=12)         
    ],justify="center"),
    
    html.Br(),
    
    html.Hr(),
      
])


# ### 4. callback functions 

# #### 4.1 callback for page rendering

# In[12]:


"""
===========================================================================================================================
Side bar activation based on user page selected.
===========================================================================================================================
"""
@app.callback(
    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):
    
    if pathname == "/":
        return home_page_content
    
    elif pathname == "/charts-page":
        return page_one_content
    
    elif pathname == "/tables-page":
        return page_two_content

    # If the user tries to reach a different page, return a 404 message
    return dbc.Jumbotron(
        [
            html.H1("404: Not found", className="text-danger"),
            html.Hr(),
            html.P(f"The pathname {pathname} was not recognised..."),
        ]
    )


# #### 4.2 callback for storing data in Tables on home page

# In[13]:


"""
===========================================================================================================================
Collecting user input and storing data in dcc.Table.
===========================================================================================================================
"""
# process data and store
@app.callback(Output('store-info', 'data'),
              Output('upload-data', 'style'),
              Output("output-user-input-info",'children'),
#               Input('store-info', 'data'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
# def update_output(stored_data, contents, list_of_names, list_of_dates):
def update_output(contents, list_of_names, list_of_dates):
    
    # if last modified is not null don't update
    
    user_input_info_default_data = "Default data loaded..."
    
    user_input_info_uploaded_data = "User input data successfully loaded..."
    
    user_input_info_stored_data = "Default data / User input data successfully loaded..."
    
#     if stored_data != None:
        
#         return stored_data, green_button_style, user_input_info_stored_data
    
    if contents is None:
        
        json_file = DEFAULT_DF.to_json(date_format='iso', orient='split')
        
        return json_file, red_button_style, user_input_info_default_data
    
#         raise PreventUpdate
    else:

        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        
#         print(list_of_dates)
        print(list_of_names)
        
        try:
            if '.csv' in list_of_names:
                # Assume that the user uploaded a CSV file
                USER_DF = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
            elif '.xls' in list_of_names:
                # Assume that the user uploaded an excel file
                USER_DF = pd.read_excel(io.BytesIO(decoded))
                
        except:
            USER_DF = DEFAULT_DF
            user_input_info_uploaded_data = 'User input data failed to load...'
            json_file = USER_DF.to_json(date_format='iso', orient='split')                
            return json_file, red_button_style, user_input_info_uploaded_data

#         USER_DF = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        json_file = USER_DF.to_json(date_format='iso', orient='split')

        return json_file, green_button_style, user_input_info_uploaded_data
    



# populate the home page with the output

@app.callback(
    Output('output-data-upload', 'children'),
    Input('store-info', 'data')
)
def output_from_store(stored_data):
    
    if stored_data != {}:
    
        df = pd.read_json(stored_data, orient='split')

        return dash_table.DataTable(
                df.to_dict('records'), [{'name': i, 'id': i} for i in df.columns], 
                page_current=0,             # page number that user is on
                page_size=50,               # number of rows visible per page

                style_table={'overflowX': 'auto'},

                style_cell={
                    'height': 'auto',
                     # all three widths are needed
                    'minWidth': '180px', 
                     'width': '180px', 
                     'maxWidth': '180px',
                    'color': 'black',
                     'font_size': '18px',
                    'whiteSpace': 'normal'},
            
                 style_header={
                    'backgroundColor': 'navy',
                    'fontWeight': 'bold',
                    'font_size': '20px',
                    'color': 'white',
                    'text_align': 'center'
                },
                )
    
    else:
        
        return pd.DatatFrame()


# #### 4.3 callback for updating graphs

# In[14]:


"""
===========================================================================================================================
Updating Graphs page
===========================================================================================================================
"""
### Updating Each Strats Chart

import os

if not os.path.exists("images"):
    ## save images here and use call back to download
    os.mkdir("images")
    
    

# >> original term chart
@app.callback(
    Output("output-original-term-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-original-term-range", "value"),
    Input("input-radio-selected-original-term", "value"),
)

def update_orig_term_chart(stored_data, range_selected, y_axis_value):
    # grab stored data
    DF = pd.read_json(stored_data, orient='split')
        
    orig_tem_fig = StratificationCreator(DF, "OrigTerm", range_selected).produce_chart(y_axis_value)
    
    orig_tem_fig.write_image(r'images\orig_term_fig.png', height= 600, width=800, scale=6)
    
    return orig_tem_fig 
        

# >> remaining term chart
@app.callback(
    Output("output-remaining-term-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-remaining-term-range", "value"),
    Input("input-radio-selected-remaining-term", "value"),
)

def update_rem_term_chart(stored_data, range_selected, y_axis_value):
    # grab stored data 
    DF = pd.read_json(stored_data, orient='split')
    
    rem_term_fig = StratificationCreator(DF, "RemTerm", range_selected).produce_chart(y_axis_value)
    
    rem_term_fig.write_image(r'images\rem_term_fig.png', height= 600, width=800, scale=6)
        
    return rem_term_fig 
        
        
# >> seasoning chart

@app.callback(
    Output("output-season-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-season-range", "value"),
    Input("input-radio-selected-seasoning", "value"),
)

def update_season_chart(stored_data, range_selected, y_axis_value):
        
    DF = pd.read_json(stored_data, orient='split')

    season_fig = StratificationCreator(DF, "Season", range_selected).produce_chart(y_axis_value)
    
    season_fig.write_image(r'images\season_fig.png', height= 600, width=800, scale=6)
    
    return season_fig


# >> coupon chart

@app.callback(
    Output("output-coupon-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-coupon-range", "value"),
    Input("input-radio-selected-coupon", "value"),
)

def update_coupon_chart(stored_data, range_selected, y_axis_value):
    
    DF = pd.read_json(stored_data, orient='split')

    coupon_fig = StratificationCreator(DF, "Coupon", range_selected).produce_chart(y_axis_value)
    
    coupon_fig.write_image(r'images\coupon_fig.png', height= 600, width=800, scale=6)
    
    return coupon_fig


# >> spread chart

@app.callback(
    Output("output-spread-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-spread-range", "value"),
    Input("input-radio-selected-spread", "value"),
)

def update_spread_chart(stored_data, range_selected, y_axis_value):
    
    DF = pd.read_json(stored_data, orient='split')

    spread_fig = StratificationCreator(DF, "Spread", range_selected).produce_chart(y_axis_value)
    
    spread_fig.write_image(r'images\spread_fig.png', height= 600, width=800, scale=6)   
    
    return spread_fig


#  >> LTV chart

@app.callback(
    Output("output-ltv-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-ltv-range", "value"),
    Input("input-radio-selected-ltv", "value"),
)

def update_ltv_chart(stored_data, range_selected, y_axis_value):
    
    DF = pd.read_json(stored_data, orient='split')

    ltv_fig = StratificationCreator(DF, "LTV", range_selected).produce_chart(y_axis_value)
    
    ltv_fig.write_image(r'images\ltv_fig.png', height= 600, width=800, scale=6) 
        
    return ltv_fig

# >> original bal chart

@app.callback(
    Output("output-original-balance-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-original-balance-range", "value"),
    Input("input-radio-selected-original-balance", "value"),
    
)

def update_original_balance_chart(stored_data, range_selected, y_axis_value):
    
    DF = pd.read_json(stored_data, orient='split')
    
    orig_bal_fig = StratificationCreator(DF, "OrigBankBal", range_selected).produce_chart(y_axis_value)
    
    orig_bal_fig.write_image(r'images\orig_bal_fig.png', height= 600, width=800, scale=6) 
    
    return orig_bal_fig


# # >> current balance chart

@app.callback(
    Output("output-current-balance-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-current-balance-range", "value"),
    Input("input-radio-selected-current-balance", "value"),
)

def update_current_balance_chart(stored_data, range_selected, y_axis_value):
    
    DF = pd.read_json(stored_data, orient='split')
    
    curr_bal_fig = StratificationCreator(DF, "CurBankBal", range_selected).produce_chart(y_axis_value)
    
    curr_bal_fig.write_image(r'images\curr_bal_fig.png', height= 600, width=800, scale=6) 
    
    return curr_bal_fig


# >> Regions chart

@app.callback(
    Output("output-region-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-region", "value"),
    Input("input-radio-selected-region", "value"),
)

def update_region_chart(stored_data, strat_value, y_axis_value):
    
    DF = pd.read_json(stored_data, orient='split')

    df_state = create_state_df(DF)
    
    state_fig = transform_data_by_state(df_state, strat_value, y_axis_value)
    
    state_fig.write_image(r'images\state_fig.png', height= 600, width=800, scale=6)
    
    return state_fig


# >> Top loans chart

@app.callback(
    Output("output-top-loans-chart", "figure"),
    Output("output-top-loans-info", "children"),
    Input('store-info', 'data'),
    Input("input-top-loans", "value"),
    Input("input-radio-selected-top-loans", "value"),
)

def update_top_loans_chart(stored_data, value, y_axis_value):
    
    DF = pd.read_json(stored_data, orient='split')

    top_loans_fig, top_loans = get_top_n_positions(DF, value, y_axis_value)
    
    top_loans_fig.write_image(r'images\top_loans_fig.png', height= 600, width=800, scale=6)    
        
    return top_loans_fig, top_loans
  

# >> Origination year chart

@app.callback(
    Output("output-origination-year-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-radio-selected-origination-year", "value"),
)

def update_origination_year_chart(stored_data, value):
    
    DF = pd.read_json(stored_data, orient='split')
    
    orig_year_fig = transform_data_by_year(DF, 'OrigYear', value)
    
    orig_year_fig.write_image(r'images\orig_year_fig.png', height= 600, width=800, scale=6)
    
    return orig_year_fig

# >> Maturity year chart

@app.callback(
    Output("output-maturity-year-chart", "figure"),
    Input('store-info', 'data'),
    Input("input-radio-selected-maturity-year", "value"),
)

def update_maturity_year_chart(stored_data, value):
    
    DF = pd.read_json(stored_data, orient='split')
    
    mat_year_fig = transform_data_by_year(DF,'MatYear', value)
    
    mat_year_fig.write_image(r'images\mat_year_fig.png', height= 600, width=800, scale=6)
    
    return mat_year_fig


# #### 4.4 callback for updating tables

# In[15]:


"""
===========================================================================================================================
Updating Tables page
===========================================================================================================================
"""
# >> original term table

@app.callback(
    Output("original-term-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-original-term-range-table", "value"),
)

def update_orig_term_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'OrigTerm', int(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["OrigTerm bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    # update the global disctionary to be printed by the user upon request
    OUTPUT_STRATIFICATION_TABLES["orig_term"] = table
    
    # format table to include bars in cells
    orig_term_table = stratification_table(table, "OrigTerm bins")
    
    return orig_term_table


# >> remaining term table
    
@app.callback(
    Output("remaining-term-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-remaining-term-range-table", "value"),
)

def update_rem_term_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'RemTerm', int(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["RemTerm bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    OUTPUT_STRATIFICATION_TABLES["rem_term"] = table
    
    # format table to include bars in cells
    rem_term_table = stratification_table(table, "RemTerm bins")
    
    return rem_term_table

# >> seasoning table
    
@app.callback(
    Output("seasoning-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-seasoning-range-table", "value"),
)

def update_season_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'Season', int(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["Season bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    OUTPUT_STRATIFICATION_TABLES["season"] = table
    
    seasoning_table = stratification_table(table, "Season bins")
    
    return seasoning_table


# >> coupon stratifications

@app.callback(
    Output("coupon-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-coupon-range-table", "value"),
)

def update_coupon_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'Coupon', float(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["Coupon bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    OUTPUT_STRATIFICATION_TABLES["coupon"] = table
    
    coupon_table = stratification_table(table, "Coupon bins")
    
    return coupon_table


# >> spread stratifications

@app.callback(
    Output("spread-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-spread-range-table", "value"),
)

def update_spread_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'Spread', float(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["Spread bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    OUTPUT_STRATIFICATION_TABLES["spread"] = table
    
    spread_table = stratification_table(table, "Spread bins")
    
    return spread_table


# >> ltv stratifications

@app.callback(
    Output("ltv-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-ltv-range-table", "value"),
)

def update_ltv_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'LTV', float(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["LTV bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    OUTPUT_STRATIFICATION_TABLES["ltv"] = table
    
    ltv_table = stratification_table(table, "LTV bins")
    
    return ltv_table

# >> original bal stratifications

@app.callback(
    Output("original-balance-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-original-balance-range-table", "value"),
)

def update_orig_balance_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'OrigBankBal', int(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["OrigBankBal bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    OUTPUT_STRATIFICATION_TABLES["orig_bal"] = table
    
    orig_bal_table = stratification_table(table, "OrigBankBal bins")
    
    return orig_bal_table

# >> current bal stratifications

@app.callback(
    Output("current-balance-table-placeholder", "children"),
    Input('store-info', 'data'),
    Input("input-current-balance-range-table", "value"),
)

def update_curr_balance_table(stored_data, range_selected):
    
    DF = pd.read_json(stored_data, orient='split')
    
    # note: when using the select dropdown, we need to convert the user selected input into integer.
    table = StratificationCreator(DF, 'CurBankBal', int(range_selected)).produce_table()
    
    # select columns to display in table
    table = table[["CurBankBal bins","CurBankBal", "% CurBankBal", "WeightedAverageCoupon","WeightedAverageSpread",
                   "WeightedAverageOrigTerm", "WeightedAverageRemTerm"]]
    
    OUTPUT_STRATIFICATION_TABLES["curr_bal"] = table
    
    curr_bal_table = stratification_table(table, "CurBankBal bins")
    
    return curr_bal_table
    


# #### 4.5 callback for images download

# In[16]:


"""
=================================================================================================================
Charts Download button
=================================================================================================================
"""
import zipfile

@app.callback(
    Output("download-charts", "data"),
    Input("btn-charts", "n_clicks"),
    prevent_initial_call=True,
)

def download_charts(n_clicks):
    
    zip_file_name = "stratification_charts.zip"
    
    items = os.listdir('images')
    
    with zipfile.ZipFile(zip_file_name, mode="w") as zf:
        for item in items: 
            print(item)
            
            zf.write('images' + '\\' + item)
#             zf.write(item)
            
        zf.close()
        
    return dcc.send_file(zip_file_name)


# In[ ]:





# #### 4.5 callback for tables download

# In[17]:


"""
=================================================================================================================
Tables Download button
=================================================================================================================
"""
# Note that it is possible to use the export feature of the data table instead of creating a download button.

@app.callback(
    Output("download-datafame-tables-csv", "data"),
    Input("btn-tables-csv", "n_clicks"),
    prevent_initial_call=True,
)

def download_tables(n_clicks):

    writer = pd.ExcelWriter("export.xlsx", engine='xlsxwriter')
    
    workbook = writer.book  
    
    for df_name , df in OUTPUT_STRATIFICATION_TABLES.items():
        
        df.to_excel(writer, sheet_name=df_name, index=False)
        
        worksheet = writer.sheets[df_name]
        
        format = workbook.add_format({'num_format': '#,##00.0'})
        worksheet.set_column('B:B', None, format)

    writer.save()
            
    return dcc.send_file("export.xlsx", "stratification_tables.xlsx")    
    
@app.callback(
    Output('table', 'children'), 
    Input('intermediate-original-term-info', 'data'))

def update_orig_term_table(jsonified_cleaned_data):
    dff = pd.read_json(jsonified_cleaned_data, orient='split')
    table = create_table(dff)
    return table


# ### 5. run dash app

# In[18]:


if __name__ == '__main__':
    app.run_server(debug=False)


