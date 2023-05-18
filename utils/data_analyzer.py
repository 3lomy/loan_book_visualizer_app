#!/usr/bin/env python
# coding: utf-8

# ## Modules for data manipulation

# ### 0. import general modules

# In[1]:


# data wrangling modules
import json
import numpy as np
import pandas as pd

# graphing modules
import plotly.express as px
import plotly.graph_objects as go


# ### 1. class modules for loans book transformation

# In[2]:


class StratificationCreator:
    
    def __init__(self, df, feature, selected_range):
        self.feature = feature
        self.selected_range = selected_range
        self.df = df 

        
    def produce_chart(self, selected_y_axis):
        # inclusive range
        start = 0
        step = self.selected_range
        stop = self.df[self.feature].max()+ step

        df_ = self.df
        
        df_ = df_.astype({'OrigBankBal': 'float64',
                         'CurBankBal': 'float64',
                         'OrigTerm': 'int64',
                         'RemTerm': 'int64',
                         'Season': 'int64',
                         'Spread': 'float64',
                         'Coupon': 'float64',
                         'LTV': 'float64',})

        # construct bins based on user selected range
        bkts = []

        bkts = np.arange(0. , df_[self.feature].max() + self.selected_range, step)

        if self.feature == 'Season' or self.feature == "OrigTerm" or self.feature=="RemTerm":
#             print(self.feature)

            bin_labels = [*(f'{round(a)}-{round(b)}'+' Months' for a, b in zip(bkts[:-1], bkts[1:]))]

        elif self.feature == 'Spread' or self.feature == "Coupon" or self.feature=="LTV":

            bin_labels = [*('{:,.1%}'.format(a) + '-' + '{:,.1%}'.format(b) for a, b in zip(bkts[:-1], bkts[1:]))]

        else: 
            bin_labels = [*(f'{round(a/1000)}-{round(b/1000)}'+'K' for a, b in zip(bkts[:-1], bkts[1:]))]

        bkt_cuts = pd.cut(df_[self.feature], bkts, labels=bin_labels)

        df_[self.feature + " bins"] = bkt_cuts
        
        # compute some weights for weigted average metrics
        df_['CurBankBal x Coupon'] = df_['CurBankBal']*df_['Coupon']
        df_['CurBankBal x Spread'] = df_['CurBankBal']*df_['Spread']
        df_['CurBankBal x OrigTerm'] = df_['CurBankBal']*df_['OrigTerm']
        df_['CurBankBal x RemTerm'] = df_['CurBankBal']*df_['RemTerm']


        if self.feature == "CurBankBal":
            df_adj = df_[[self.feature, self.feature + " bins", 'CurBankBal x Coupon', 'CurBankBal x Spread',
                          'CurBankBal x OrigTerm', 'CurBankBal x RemTerm']].groupby([self.feature + " bins"]).sum()
        else:
            df_adj = df_[[self.feature, self.feature + " bins", "CurBankBal", 'CurBankBal x Coupon', 'CurBankBal x Spread',
                          'CurBankBal x OrigTerm', 'CurBankBal x RemTerm']].groupby([self.feature + " bins"]).sum()

        df_adj['WeightedAverageCoupon'] = df_adj['CurBankBal x Coupon']/df_adj['CurBankBal']

        df_adj['WeightedAverageSpread'] = df_adj['CurBankBal x Spread']/df_adj['CurBankBal']

        df_adj['WeightedAverageOrigTerm'] = df_adj['CurBankBal x OrigTerm']/df_adj['CurBankBal']

        df_adj['WeightedAverageRemTerm'] = df_adj['CurBankBal x RemTerm']/df_adj['CurBankBal']

        df_adj['% CurBankBal'] = df_adj['CurBankBal']/df_adj['CurBankBal'].sum()


        if selected_y_axis == "Amount":

            fig = px.bar(df_adj, x=df_adj.index, y='CurBankBal')

        else:

            fig = px.bar(df_adj, x=df_adj.index, y='% CurBankBal')
            fig.layout.yaxis.tickformat = ',.1%'
            fig.update_traces(marker_color='indianred')

        return fig 
    
    def produce_table(self):
        # inclusive range
        start = 0
        step = self.selected_range
        stop = self.df[self.feature].max()+ step

        df_ = self.df

        # construct bins based on user selected range
        bkts = []

        bkts = np.arange(0. , df_[self.feature].max() + self.selected_range, step)

        if self.feature == 'Season' or self.feature == "OrigTerm" or self.feature=="RemTerm":
#             print(self.feature)

            bin_labels = [*(f'{round(a)}-{round(b)}'+' Months' for a, b in zip(bkts[:-1], bkts[1:]))]

        elif self.feature == 'Spread' or self.feature == "Coupon" or self.feature=="LTV":

            bin_labels = [*('{:,.1%}'.format(a) + '-' + '{:,.1%}'.format(b) for a, b in zip(bkts[:-1], bkts[1:]))]

        else: 
            bin_labels = [*(f'{round(a/1000)}-{round(b/1000)}'+'K' for a, b in zip(bkts[:-1], bkts[1:]))]

        bkt_cuts = pd.cut(df_[self.feature], bkts, labels=bin_labels)

        df_[self.feature + " bins"] = bkt_cuts
        
        # compute some weights for weigted average metrics
        df_['CurBankBal x Coupon'] = df_['CurBankBal']*df_['Coupon']
        df_['CurBankBal x Spread'] = df_['CurBankBal']*df_['Spread']
        df_['CurBankBal x OrigTerm'] = df_['CurBankBal']*df_['OrigTerm']
        df_['CurBankBal x RemTerm'] = df_['CurBankBal']*df_['RemTerm']

    #     df['Denominator'] =  df['CurBankBal'] 

        if self.feature == "CurBankBal":
            df_adj = df_[[self.feature, self.feature + " bins", 'CurBankBal x Coupon', 'CurBankBal x Spread',
                          'CurBankBal x OrigTerm', 'CurBankBal x RemTerm']].groupby([self.feature + " bins"]).sum()
        else:
            df_adj = df_[[self.feature, self.feature + " bins", "CurBankBal", 'CurBankBal x Coupon', 'CurBankBal x Spread',
                          'CurBankBal x OrigTerm', 'CurBankBal x RemTerm']].groupby([self.feature + " bins"]).sum()

        df_adj['WeightedAverageCoupon'] = df_adj['CurBankBal x Coupon']/df_adj['CurBankBal']

        df_adj['WeightedAverageSpread'] = df_adj['CurBankBal x Spread']/df_adj['CurBankBal']

        df_adj['WeightedAverageOrigTerm'] = df_adj['CurBankBal x OrigTerm']/df_adj['CurBankBal']

        df_adj['WeightedAverageRemTerm'] = df_adj['CurBankBal x RemTerm']/df_adj['CurBankBal']

        df_adj['% CurBankBal'] = df_adj['CurBankBal']/df_adj['CurBankBal'].sum()
        
        return df_adj.drop(columns=['CurBankBal x Coupon', 'CurBankBal x Spread',
                                    'CurBankBal x OrigTerm', 'CurBankBal x RemTerm']).reset_index()
        
        


# ### 2. module specific for regional strats

# In[3]:


### Global Variables
# SETUP GEJSON FILE
GERMANY_REGIONS_GEOJSON = json.load(open("data/regions_of_germany.json",'r'))

# GERMANY_REGIONS_GEOJSON['features'][0].keys()

STATE_ID_MAP ={} # map ids to cols in dataframe

for feature in GERMANY_REGIONS_GEOJSON['features']:
    feature['id'] = feature['properties']['ID_1']
    STATE_ID_MAP[feature['properties']['NAME_1']] = feature['id']
    
dict_state_shortcode_to_name ={
    "BA" : "Bayern",
    "BD" : "Brandenburg",
    "BE" : "Berlin",
    "BR" : "Bremen",
    "BW" : "Baden-Wuerttemberg",
    "HE" : "Hessen",
    "HH" : "Hamburg",
    "LS" : "Niedersachsen", 
    "MV" : "Mecklenburg-Vorpommern",
    "NW" : "Nordrhein-Westfalen",
    "RP" : "Rheinland-Pfalz",
    "SA" : "Sachsen-Anhalt",
    "SH" : "Schleswig-Holstein",
    "SR" : "Saarland",
    "SX" : "Sachsen",
    "TH" : "Thueringen"
    }


def create_state_df(df):
    
    dff = df.copy()

    dff['Season*CurBankBal'] =  dff['Season']*dff['CurBankBal']

    df_state = dff[['State','CurBankBal', 'OrigBankBal', 'Season*CurBankBal']].groupby("State").sum().reset_index()

    df_state['WAvgSeason'] = dff['Season*CurBankBal']/dff['CurBankBal']

    df_state['% CurBankBal'] = df_state['CurBankBal']/df_state['CurBankBal'].sum()

    df_state.replace({"State": dict_state_shortcode_to_name}, inplace=True)

    df_state['id'] = df_state['State'].apply(lambda x: STATE_ID_MAP[x])
    
    return df_state



def transform_data_by_state(df, strat_value, y_axis_label): 
    
    # uses as input customized df created by def create_state_df
    
    if strat_value == "WAvgSeason":
        fig = go.Figure(data=go.Choropleth(
        locations=df['id'], # Spatial coordinates 
        z = df[strat_value].astype(float), # Data to be color-coded
        locationmode = 'geojson-id', # set of locations match entries in `locations`
        geojson=GERMANY_REGIONS_GEOJSON,
        text=df['State'],
        colorscale = 'Blues',
        autocolorscale=False,
        reversescale=False,
        marker_line_color='darkgray',
        marker_line_width=0.5,
        colorbar_title = 'Months',
        ))

        fig.update_geos(fitbounds="locations", visible=False)

        fig.update_layout( 
        title_text = strat_value + ' by German State',
        geo_scope='europe', # limite map scope to europe
        ) 
    
    else:
        
        if y_axis_label == "Amount":
    
            fig = go.Figure(data=go.Choropleth(
            locations=df['id'], # Spatial coordinates 
            z = df[strat_value].astype(float), # Data to be color-coded
            locationmode = 'geojson-id', # set of locations match entries in `locations`
            geojson=GERMANY_REGIONS_GEOJSON,
            text=df['State'],
            colorscale = 'Blues',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
            colorbar_tickprefix = '€',
            colorbar_title = 'Millions EUR',
            ))

            fig.update_geos(fitbounds="locations", visible=False)

            fig.update_layout( 
            title_text = strat_value + ' by German State',
            geo_scope='europe', # limite map scope to europe
            )
            
        else:
            
            
            fig = go.Figure(data=go.Choropleth(
            locations=df['id'], # Spatial coordinates 
            z = (df['% CurBankBal']*100).astype(float), # Data to be color-coded
            locationmode = 'geojson-id', # set of locations match entries in `locations`
            geojson=GERMANY_REGIONS_GEOJSON,
            text=df['State'],
            colorscale = 'Reds',
            autocolorscale=False,
            reversescale=False,
            marker_line_color='darkgray',
            marker_line_width=0.5,
#             colorbar_tickprefix = '€',
            colorbar_title = '% CurBankBal',
            ))

        fig.update_geos(fitbounds="locations", visible=False)

        fig.update_layout( 
        title_text = strat_value + ' by German State',
        geo_scope='europe', # limite map scope to europe
        )
            
    return fig


# ### 3. module for top loans strats

# In[4]:


def get_top_n_positions(df, num, y_axis_value):
    
    df_ = df.sort_values(by=['CurBankBal'], axis=0, ascending = False)
    
    df_new = df_.iloc[:num]
    
    df_new.reset_index(inplace=True)
    
    df_new = (df_new.rename(index=lambda s: "top " + str(s + 1)))
    
    df_new.index.name = 'Top loans'
    
    df_new['% CurBankBal'] = df_new['CurBankBal'] / df_['CurBankBal'].sum()
    
    
    if y_axis_value == "Amount":
        
        ratio_of_top_loans_selected = ' >>> Top ' + str(num) + '  loans represents ' + '{:,.2f}'.format(df_new['CurBankBal'].sum()) + ' of pool'
        
        fig = px.bar(df_new, x=df_new.index, y='CurBankBal')
  
    
    else:
        
        ratio_of_top_loans_selected = ' >>> Top ' + str(num) + '  loans represents ' + '{:,.1%}'.format(df_new['% CurBankBal'].sum()) + ' of pool'
        
        fig = px.bar(df_new, x=df_new.index, y='% CurBankBal')
        
        fig.layout.yaxis.tickformat = ',.1%'
        
    return fig, ratio_of_top_loans_selected


# ### 4. module for origination and maturity year strats

# In[5]:


def transform_data_by_year(df, feature, value):
    
    df_by_year = df[[feature,'CurBankBal']].groupby(feature).sum().reset_index()
    
    df_by_year['Percentage'] = df_by_year['CurBankBal']/df_by_year['CurBankBal'].sum()
    
    if value == "Percentage":
        
        fig = px.bar(df_by_year, x=feature, y='Percentage')
        
        fig.layout.yaxis.tickformat = ',.1%'
        
    else:
        fig = px.bar(df_by_year, x=feature, y='CurBankBal')
        
    return fig       

