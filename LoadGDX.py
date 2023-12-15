"""
Created on 11.11.2023

@author: Mathias Berg Rosendal, PhD Student at DTU Management (Energy Economics & Modelling)
"""
#%% ------------------------------- ###
###        0. Script Settings       ###
### ------------------------------- ###

import gams
import sys
import pandas as pd
import pickle
import tkinter as tk
from tkinter import ttk

### 0.0 Functions
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

def convert_to_list(input):
    if len(input) > 0:
        output = input.rstrip(']').lstrip('[').replace(' ','').split(',')
    else:
        output = input
    return output

### 0.1 Load Inputs
path    = r'%s'%sys.argv[1]
SCs     = convert_to_list(sys.argv[2])
iters   = convert_to_list(sys.argv[3])
symbols = convert_to_list(sys.argv[4])

#%% ------------------------------- ###
###         1. Open GDX File        ###
### ------------------------------- ###

### 1.1 Load DataFrames
ws = gams.GamsWorkspace()
dfs = {}

for symbol in symbols:
    dfs[symbol] = pd.DataFrame({})
    for SC in SCs:
        if len(iters) >= 1:
            for itr in iters:                
                SC_FULL = SC + '_Iter%s'%itr
                try:
                    db = ws.add_database_from_gdx(path + "/MainResults_%s.gdx"%SC_FULL)
                    
                    temp = symbol_to_df(db, symbol)
                    temp['SC'] = SC
                    temp['Iteration'] = itr
                    dfs[symbol] = pd.concat((dfs[symbol], temp))
                except:
                    print("%s doesn't exist"%SC_FULL)
        try:
            db = ws.add_database_from_gdx(path + "/MainResults_%s.gdx"%SC)
            
            temp = symbol_to_df(db, symbol)
            temp['SC'] = SC
            temp['Iteration'] = -1
            dfs[symbol] = pd.concat((dfs[symbol], temp))    
        except:
            print("%s doesn't exist"%SC)       
    dfs[symbol].to_csv('Output/%s.csv'%symbol, index=None)

with open('Output/df.pkl', 'wb') as f:
    pickle.dump(dfs, f)

#%%
# import pickle
# import pandas as pd

# with open('df.pkl', 'rb') as f:
#     dfs = pickle.load(f)