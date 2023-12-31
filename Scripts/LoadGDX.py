"""
Created on 11.11.2023

@author: Mathias Berg Rosendal, PhD Student at DTU Management (Energy Economics & Modelling)
"""
### ------------------------------- ###
###        0. Script Settings       ###
### ------------------------------- ###
import traceback

try:
    
    import gams
    import sys
    import pandas as pd
    from Functions import symbol_to_df, convert_to_list

    ### 0.0 Load Arguments
    if len(sys.argv) > 2:
        path    = r'%s'%sys.argv[1]
        SCs     = convert_to_list(sys.argv[2])
        iters   = convert_to_list(sys.argv[3])
        symbols = convert_to_list(sys.argv[4])
        
    ### 0.1 If no arguments, then you are probably running this script stand-alone
    else:
        import os
        print('-------------------------------\n'+'           TEST MODE           \n'+'-------------------------------\n')
        os.chdir(__file__.replace(r'\Scripts\LoadGDX.py', ''))
        path = r'C:\Users\mberos\gitRepos\balmorel-antares\Balmorel\base\model'
        SCs = ['%scenario_name%']
        iters = []
        symbols = ['EL_PRICE_YCR']

    ### ------------------------------- ###
    ###         1. Open GDX File        ###
    ### ------------------------------- ###

    ### 1.1 Load DataFrames
    ws = gams.GamsWorkspace()
    dfs = {symbol : pd.DataFrame({}) for symbol in symbols}
    warning_message = ''

    for SC in SCs:
        search_exception = 0
        if len(iters) >= 1:
            for itr in iters:                
                SC_FULL = SC + '_Iter%s'%itr
                try:
                    print('\nTrying to load MainResults_%s.gdx..'%SC_FULL)
                    db = ws.add_database_from_gdx(path + "/MainResults_%s.gdx"%SC_FULL)
                    
                    for symbol in symbols:
                        try:
                            temp = symbol_to_df(db, symbol)
                            temp['SC'] = SC
                            temp['Iteration'] = itr
                            dfs[symbol] = pd.concat((dfs[symbol], temp))
                            print("Loaded %s"%(symbol))
                        except:
                            print("Couldn't load %s"%symbol)
                except gams.GamsException:
                    print("It doesn't exist, not loaded")
                    search_exception += 1
        try:
            print('\nTrying to load MainResults_%s.gdx..'%SC)
            db = ws.add_database_from_gdx(path + "/MainResults_%s.gdx"%SC)
            
            for symbol in symbols:
                try:
                    temp = symbol_to_df(db, symbol)
                    temp['SC'] = SC
                    temp['Iteration'] = -1
                    dfs[symbol] = pd.concat((dfs[symbol], temp)) 
                    print("Loaded %s"%(symbol))
                except:
                    print("Couldn't load %s"%symbol)
        except gams.GamsException:
            search_exception += 1
            print("It doesn't exist, not loaded") 
            
            if search_exception == 2:
                warning_message += "Couldn't find MainResults_%s.gdx or MainResults_%s.gdx in path:\n %s"%(SC_FULL, SC, path)   
            
    all_empty = 0
    for symbol in symbols:
        dfs[symbol].to_csv('Output/%s.csv'%symbol, index=None)
        if len(dfs[symbol]) == 0:
            all_empty += 1
    

    ### 1.2 Saves the dataframes as efficient pickle files that can be read in a python script 
    # import pickle
    # with open('Output/df.pkl', 'wb') as f:
    #     pickle.dump(dfs, f)

    ### 1.3 Opening a pickle file
    # with open('df.pkl', 'rb') as f:
    #     dfs = pickle.load(f)
    
    with open('Output/Log.txt', 'w') as f:
        if len(warning_message) == 0:
            f.write('No errors')
            print('\nSuccesful execution of LoadGDX.py')
        elif all_empty == len(symbols):
            f.write('Nothing loaded! Check path and MainResults files.')
            print('Nothing loaded! Check path and MainResults files.')
        else:
            f.write(warning_message)
            print(warning_message)

except Exception as e:
    message = traceback.format_exc()
    
    print('\nAn error occurred - check the Python environment')
    with open('Output/Log.txt', 'w') as f:
        f.write('Something went wrong. Make sure you typed an existing scenario, iteration, symbol, region, year, legend type and/or plot style.')
        f.write('\n\n' + message)