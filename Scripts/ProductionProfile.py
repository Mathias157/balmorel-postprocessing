# -*- coding: utf-8 -*-
"""
Created on 28.05.2022

@author: Mathias Berg Rosendal, PhD Student at DTU Management (Energy Economics & Modelling)
"""
#%% ----------------------------- ###
###       0. Script Settings      ###
### ----------------------------- ###

import traceback

try:
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import sys
    import gams
    from Functions import symbol_to_df
    
    ### 0.0 Load Arguments
    if len(sys.argv) > 2:
        wk_dir    = r'%s'%sys.argv[1]
        SC     = sys.argv[2]
        iter   = sys.argv[3]
        reg     = sys.argv[4]
        Y       = sys.argv[5]
        typ     = sys.argv[6] # Should be a column, e.g. TECH_TYPE, RRR, AAA, G
        style   = sys.argv[7].replace(' ', '').lower()
        
    ### 0.1 If no arguments, then you are probably running this script stand-alone
    else:
        import os
        print('-------------------------------\n'+'           TEST MODE           \n'+'-------------------------------\n')
        os.chdir(__file__.replace(r'\Scripts\LoadGDX.py', ''))
        wk_dir = r'C:\Users\mberos\Danmarks Tekniske Universitet\PhD in Transmission and Sector Coupling - Dokumenter\Deliverables\Smart-coupling of Balmorel and Antares\Smaller Analyses\Transport Modelling'
        SC = 'TransportBase'
        iter = '0'
        reg = 'TR'
        Y = '2050'
        typ = 'TECH_TYPE' # Should be a column, e.g. TECH_TYPE, RRR, AAA, G
        style = 'dark'

    ### 0.2 Set plot style
    if style == 'light':
        plt.style.use('default')
        fc = 'white'
        demcolor = 'k'
    elif style == 'dark':
        plt.style.use('dark_background')
        fc = 'none'
        demcolor = 'w'
            
        
    ### ----------------------------- ###
    ###        1. Read Files          ###
    ### ----------------------------- ###

    ### Technical
    delim = ','

    ### Try to load the non-iteration scenario suffix first
    ws = gams.GamsWorkspace()
    try:
        db = ws.add_database_from_gdx(wk_dir + '/MainResults_%s.gdx'%SC)
    except gams.GamsException:
        SC = SC + '_Iter%s'%iter  
        db = ws.add_database_from_gdx(wk_dir + '/MainResults_%s.gdx'%SC)

    fProd = symbol_to_df(db, "PRO_YCRAGFST", cols=['Y', 'C', 'RRR', 'AAA', 'G', 'FFF', 'SSS', 'TTT', 'COMMODITY', 'TECH_TYPE', 'UNITS', 'Val'])
    fFlow = symbol_to_df(db, "X_FLOW_YCRST", cols=['Y', 'C', 'IRRRE', 'IRRRI', 'SSS', 'TTT', 'UNITS', 'Val'])
    fElP  = symbol_to_df(db, "EL_PRICE_YCRST", cols=['Y', 'C', 'RRR', 'SSS', 'TTT', 'UNITS', 'Val']) 
    fElD  = symbol_to_df(db, "EL_DEMAND_YCRST", cols=['Y', 'C', 'RRR', 'SSS', 'TTT', 'VARIABLE_CATEGORY', 'UNIT', 'Val'])  


    ### ----------------------------- ###
    ###           Parameters          ###
    ### ----------------------------- ###

    # Choices
    RorC = 'R' # Region or country level?
    country = 'GERMANY'
    countryR = 'DE'
    resfactor = 13 # Factor on flows, to get yearly results 
    elprice_agg = np.max # function for aggregation of regions - average or max ?
    bypass_eps = 'Y' # Bypass EPS values in electricity prices? This could be fair, if you have regions with very small electricity demand, making EPS electricity prices (not wrong)


    ### Colours
    c = {'IMPORT' : [150/255, 185/255, 252/255],
        'BIOGAS' : [128/255, 159/255, 121/255],
        'CONDENSING' : [0.2, 0.2, 0.2],
        'NATGAS' : [0.2, 0.2, 0.2],
        'COAL' : [0, 0, 0],
        'LIGHTOIL' : [0.4, 0.4, 0.4],
        'FUELOIL' : [.4, .4, .4],
        'WATER' : [63/255, 37/255, 1],
        'HYDRO-RESERVOIRS' : [63/255, 37/255, 1],
        'HYDRO-RUN-OF-RIVER' : [63/255*0.8, 37/255*0.8, 1*0.8],
        'WIND' : [83/255, 243/255, 133/255],
        'WIND-ON' : [83/255, 243/255, 133/255],
        'WIND-OFF' : [83/255*0.8, 243/255*0.8, 133/255*0.8],
        'SUN' : [255/255, 254/255, 0],
        'SOLAR-PV' : [255/255, 254/255, 0],
        'MUNIWASTE' : [150/255, 150/255, 150/255],
        'WOODCHIPS' : [233/255, 67/255, 67/255],
        'WOODPELLETS' : [215/255, 60/255, 60/255],
        'STRAW' : [241/255, 135/255, 135/255],
        'PEAT' : [.8, .8, .8],
        'ELECTRIC' : [252/255, 1, 137/255],
        'HYDROGEN' : [137/255, 224/255, 1],
        'NUCLEAR' : [204/255, 0, 204/255],
        'WASTEHEAT' : [1,0,0]}


    ### ----------------------------- ###
    ###              Sort             ###
    ### ----------------------------- ###

    ### Sort
    com = 'ELECTRICITY'
    
    # Production
    if RorC == 'R':
        idx = fProd['RRR'] == reg
    elif RorC == 'C':
        idx = fProd['C'] == country
    idx = idx & (fProd['COMMODITY'] == com)
    idx = idx & (fProd['Y'] == Y)

    fPr = fProd[idx].pivot_table(values='Val', index=['SSS', 'TTT'], columns=[typ],aggfunc=sum)
    fPr[np.isnan(fPr)] = 0


    ### Import / Export
    # First aggregate regions in country, if country
    if RorC == 'C':
        # Export aggregation
        idx = fFlow.IRRRE.str.find(countryR) != -1
        print('Country model check, should be only one country-region: ', fFlow[idx].IRRRE.unique())
        fFlow.loc[idx, 'IRRRE'] = countryR
        
        # Import aggregation
        idx = fFlow.IRRRI.str.find(countryR) != -1
        print('Country model check, should be only one country-region: ', fFlow[idx].IRRRI.unique())
        fFlow.loc[idx, 'IRRRI'] = countryR
                
        # Remove all internal flows
        idx = (fFlow.IRRRE == countryR) & (fFlow.IRRRI == countryR)
        fFlow = fFlow[~idx]

    # Get year
    try:
        idx = fFlow['Y'] == Y

        if RorC == 'R':
            idx1 = fFlow['IRRRE'] == reg
            idx2 = fFlow['IRRRI'] == reg
        elif RorC == 'C':
            idx1 = fFlow['IRRRE'] == countryR
            idx2 = fFlow['IRRRI'] == countryR
            reg = countryR

        fFlE = fFlow[idx & idx1].pivot_table(values='Val', index=['SSS', 'TTT'], aggfunc=sum)    
        fFlI = fFlow[idx & idx2].pivot_table(values='Val', index=['SSS', 'TTT'], aggfunc=sum)

        print('\n' + reg + ' Main Export-To Regions: [TWh]')
        print(fFlow[idx & idx1].pivot_table(values='Val', index=['IRRRI'], aggfunc=sum)/1e6*resfactor  )
        print('\n')

        print(reg + ' Main Import-From Regions: [TWh]')
        print(fFlow[idx & idx2].pivot_table(values='Val', index=['IRRRE'], aggfunc=sum)/1e6*resfactor  )
        print('\n')
        no_trans_data = False
    except KeyError:
        no_trans_data = True
        print('No transmission data')


    ### Electricity Demand and price
    if RorC == 'C':
        fP = fElP.groupby(['Y', 'C', 'SSS', 'TTT'], as_index=False)
        fP = fP.aggregate({'Val' : elprice_agg}) # For aggregation of electricity price, max or average? (maybe max if nodal representation of a market?)
        fP = fP[fP.C == country]    
        
        fD = fElD.groupby(['Y', 'C', 'VARIABLE_CATEGORY', 'SSS', 'TTT'], as_index=False)
        fD = fD.aggregate({'Val' : np.sum}) 
        dems = fD[(fD['Y']==Y) & (fD['C'] == country)]
        fD = fElD[fElD.C == country] 
    elif RorC == 'R':
        dems = fElD[(fElD['Y']==Y) & (fElD['RRR'] == reg)]
        fP = fElP[fElP['RRR'] == reg]    
        fD = fElD[fElD['RRR'] == reg] 

    print('Electricity Demand: [TWh]')
    for cat in np.unique(dems['VARIABLE_CATEGORY']):
        print(cat, ' = ', round(dems[dems['VARIABLE_CATEGORY'] == cat]['Val'].sum()/1e6*resfactor,2))

    # Subtract import from export
    f = pd.DataFrame({'IMPORT' : np.zeros(len(fPr))}, index=fPr.index)
    if not(no_trans_data):
        if com == 'ELECTRICITY':
            # f = f + fFlI - fFlE
            f_temp = pd.DataFrame([], index=fPr.index)
            try:
                f_temp['IMPORT'] = fFlI
                f_temp['EXPORT'] = -fFlE
                f_temp[np.isnan(f_temp)] = 0
            except ValueError:
                # If no connections to this region
                pass
            
            # f[np.isnan(f)] = 0
            # f.columns = ['IMPORT']
            f = pd.DataFrame([], index=fPr.index)
            f['IMPORT'] = f_temp.sum(axis=1)
            
            f[fPr.columns] = fPr
                
        else:
            print('Need to make heat script')
    else:
        f = pd.DataFrame([], index=fPr.index)
        f[fPr.columns] = fPr
            
    # Price
    if bypass_eps.lower() == 'y':
        idx = fP.Val == 'Eps'
        fP.loc[idx, 'Val'] = 0 # If you chose to bypass eps values in el-price, it's probably because the actual prices are very small
        fP.Val = fP.Val.astype(float)
        
    idx = fP['Y'] == Y
    fP = fP[idx].pivot_table(values='Val', index=['SSS', 'TTT'], aggfunc=sum)

    # Demand
    idx = fD['Y'] == Y 
    fD = fD[idx].pivot_table(values='Val', index=['SSS', 'TTT'], aggfunc=sum)

    # x-axis
    x = np.arange(0, len(fD), 1)

    # H2 Production
    # idx = (fH2['Year'] == Y) & (fH2['Reg'] == reg) & (fH2['SC'] == SC)
    # H2 = fH2.loc[idx, 'Power [GWH2]']
    # if len(H2) == 0:
    #     H2 = np.zeros(len(x))

    ### Graph
    fig, ax = plt.subplots(figsize=(9,3), facecolor=fc)
    temp = np.zeros(len(fD))
    ps = []
    for col in f:
        try:
            ps.append(ax.fill_between(x, temp, temp+f[col].values/1e3, label=col, facecolor=np.array(c[col]).round(2)))
        except KeyError:
            print('No defined colour for %s'%col)
            ps.append(ax.fill_between(x, temp, temp+f[col].values/1e3, label=col))
        temp = temp + f[col].values/1e3       

    # p0, = ax.plot(x, H2, color=[76/255,128/255, 204/255])
    p1, = ax.plot(x, fD.values[:,0]/1e3, color=demcolor)
    ax2 = ax.twinx()
    try:
        p2, = ax2.plot(x, fP.values, 'r--', linewidth=1)
    except TypeError:
        print('\nThere could be "EPS" values in electricity prices - cannot plot')

    ax.set_facecolor(fc)
    names = pd.Series(f.columns).str.lower().str.capitalize()
    # names = list(names) + ['H$_2$ Production [GW$_\mathrm{H_2}$]', 'Demand', 'Price'] # With H2 production
    names = list(names) + ['Demand', 'Price'] # Without H2 production

    # ax.legend(ps+[p0, p1, p2], names, # With H2 production
    ax.legend(ps+[p1, p2], names, # Without H2 production
            loc='center', bbox_to_anchor=(.5, 1.28), ncol=5)
    ax.set_title(SC + ' - ' + reg + ' - ' + str(Y))
    ax.set_ylabel('Power [GW]')
    ax.set_xlabel('Time [h]')
    xticks = np.hstack(np.arange(0, len(fD), len(fD)/8)) # For H2-study resolution
    # xticks = np.hstack(np.arange(0, 673, 168)) # For 4 representative weeks
    # ax.set_xticks(xticks+12.5)
    # ax.set_xticklabels((xticks/24).astype(int)) # old
    # ax.set_xticklabels(['S02', 'S08', 'S15', 'S21', 'S28', 'S34', 'S41', 'S47']) # For 4 representative weeks
    ax2.set_ylabel('Price [€ / MWh]')
    ax2.set_ylim([0, 300])
    # ax.set_xlim([0, 192])
    # ax.set_xlim([2*168, 3*168])
    # ax.set_xlim([0, 4*168])
    ax.set_xlim([min(x), max(x)])

    # ax.set_ylim([-17, 14])

    # fig.savefig(SC+'_'+str(Y)+'_'+reg+'ElGraph.pdf', bbox_inches='tight',
    #             transparent=True)
    # ax.set_xlim([200, 250])

    # ax.set_ylim(-15000, 5000)
    fig.savefig('Output/productionprofile.png', bbox_inches='tight')

    with open('Output/Log.txt', 'w') as f:
        f.write('No errors')
        
except Exception as e:
    message = traceback.format_exc()
    
    with open('Output/Log.txt', 'w') as f:
        f.write('Something went wrong. Make sure you typed an existing scenario, iteration, symbol, region, year, legend type and/or plot style.')
        f.write('\n\n' + message)