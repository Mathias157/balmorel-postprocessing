"""
Created on 16.12.2023

@author: Mathias Berg Rosendal, PhD Student at DTU Management (Energy Economics & Modelling)
"""
#%% ------------------------------- ###
###        0. Script Settings       ###
### ------------------------------- ###

import pandas as pd


#%% ------------------------------- ###
###           1. Functions          ###
### ------------------------------- ###

### 1.0 Converting a GDX file to a pandas dataframe
def symbol_to_df(db, symbol, cols='None'):
    """
    Loads a symbol from a GDX database into a pandas dataframe

    Args:
        db (GamsDatabase): The loaded gdx file
        symbol (string): The wanted symbol in the gdx file
        cols (list): The columns
    """   
    df = dict( (tuple(rec.keys), rec.value) for rec in db[symbol] )
    df = pd.DataFrame(df, index=['Value']).T.reset_index() # Convert to dataframe
    if cols != 'None':
        try:
            df.columns = cols
        except:
            pass
    return df 

### 1.1 Converting input arguments to a python list
def convert_to_list(input):
    if len(input) > 0:
        output = input.rstrip(']').lstrip('[').replace(' ','').split(',')
    else:
        output = input
    return output
