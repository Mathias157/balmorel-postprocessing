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
import time

class MyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tkinter Window with Process")
        self.root.geometry('300x60')
        self.root.title('Progressbar Demo')

        # Add your widgets or configurations here
        self.pb = ttk.Progressbar(
        root,
        orient='horizontal',
        mode='determinate',
        length=280
        )
        # place the progressbar
        self.pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
        
    ### 0.0 Functions
    def symbol_to_df(self, db, symbol, cols='None'):
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

    def convert_to_list(self, input):
        if len(input) > 0:
            output = input.rstrip(']').lstrip('[').replace(' ','').split(',')
        else:
            output = input
        return output
    
    def increment_progress_bar(self, inc):
        self.pb['value'] += inc

    def start_process(self):
        # Modify this line to start your specific process
        
        ### 0.1 Load Inputs
        path    = r'%s'%sys.argv[1]
        SCs     = self.convert_to_list(sys.argv[2])
        iters   = self.convert_to_list(sys.argv[3])
        symbols = self.convert_to_list(sys.argv[4])

        self.increment_progress_bar(10)

        ### ------------------------------- ###
        ###         1. Open GDX File        ###
        ### ------------------------------- ###

        ### 1.1 Load DataFrames
        ws = gams.GamsWorkspace()
        dfs = {}
        progress_delta = 90 / (len(symbols)*len(SCs)*len(iters)) # Increment value for progress bar

        for symbol in symbols:
            # time.sleep(5)
            dfs[symbol] = pd.DataFrame({})
            for SC in SCs:
                if len(iters) >= 1:
                    for itr in iters:                
                        SC_FULL = SC + '_Iter%s'%itr
                        try:
                            db = ws.add_database_from_gdx(path + "/MainResults_%s.gdx"%SC_FULL)
                            
                            temp = self.symbol_to_df(db, symbol)
                            temp['SC'] = SC
                            temp['Iteration'] = itr
                            dfs[symbol] = pd.concat((dfs[symbol], temp))
                        except:
                            print("%s doesn't exist"%SC_FULL)
                        # self.increment_progress_bar(progress_delta) # Incrementing progress bar
                try:
                    db = ws.add_database_from_gdx(path + "/MainResults_%s.gdx"%SC)
                    
                    temp = self.symbol_to_df(db, symbol)
                    temp['SC'] = SC
                    temp['Iteration'] = -1
                    dfs[symbol] = pd.concat((dfs[symbol], temp))    
                except:
                    print("%s doesn't exist"%SC)       
                self.increment_progress_bar(progress_delta) # Incrementing progress bar
            dfs[symbol].to_csv('Output/%s.csv'%symbol, index=None)

        with open('Output/df.pkl', 'wb') as f:
            pickle.dump(dfs, f)
        self.root.destroy()
        ##
        # import pickle
        # import pandas as pd

        # with open('df.pkl', 'rb') as f:
        #     dfs = pickle.load(f)


if __name__ == "__main__":
    root = tk.Tk()
    app = MyApp(root)

    root.after(100, app.start_process)
    root.mainloop()
    

