# -*- coding: utf-8 -*-
"""
Created on Sat May 28 11:46:48 2022

@author: mberos
"""
#%% ----------------------------- ###
###         Script Settings       ###
### ----------------------------- ###


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
import gams
import os
from Workflow.Functions.GeneralHelperFunctions import symbol_to_df
# from formplot import newplot, fplot
# from scipy.optimize import curve_fit

style = 'report'

if style == 'report':
    plt.style.use('default')
    fc = 'white'
elif style == 'ppt':
    plt.style.use('dark_background')
    fc = 'none'
    
    
#%% ----------------------------- ###
###          Read Files           ###
### ----------------------------- ###

### Technical
delim = ','

### Scenario
SC = 'TR_Base'
# SC = 'TR_NoRESstor'
# SC = 'TR_NoRESstor-3rdROR'
SC = 'TR_50%lowerWTRFLH'
SC = 'TransportBase'
SC = '%scenario_name%'
# i = 0
# SC = SC + '_Iter%d'%i

### Load
wk_dir = r"C:\Users\mberos\gitRepos\balmorel-antares" + '/Balmorel/base/model'
# wk_dir = r"C:\Users\mberos\Danmarks Tekniske Universitet\PhD in Transmission and Sector Coupling - Dokumenter\Deliverables\Smart-coupling of Balmorel and Antares\Smaller Analyses\Transport Modelling"
ws = gams.GamsWorkspace()
db = ws.add_database_from_gdx(wk_dir + '/MainResults_%s.gdx'%SC)

fProd = symbol_to_df(db, "PRO_YCRAGFST", cols=['Y', 'C', 'RRR', 'AAA', 'G', 'FFF', 'SSS', 'TTT', 'COMMODITY', 'TECH_TYPE', 'UNITS', 'Val'])
fFlow = symbol_to_df(db, "X_FLOW_YCRST", cols=['Y', 'C', 'IRRRE', 'IRRRI', 'SSS', 'TTT', 'UNITS', 'Val'])
fElP  = symbol_to_df(db, "EL_PRICE_YCRST", cols=['Y', 'C', 'RRR', 'SSS', 'TTT', 'UNITS', 'Val']) 
fElD  = symbol_to_df(db, "EL_DEMAND_YCRST", cols=['Y', 'C', 'RRR', 'SSS', 'TTT', 'VARIABLE_CATEGORY', 'UNIT', 'Val'])  
# fHP = symbol_to_df(db, "", cols=)
# fHD = symbol_to_df(db, "", cols=)

# fProd = pd.read_csv(r'C:\Users\mberos\OneDrive - Danmarks Tekniske Universitet\Work\Balmorel Automation\Spatial Aggregation\PriceProdGraphs\ProductionHourly_%s.csv'%SC, delimiter=delim)
# fFlow = pd.read_csv(r'C:\Users\mberos\OneDrive - Danmarks Tekniske Universitet\Work\Balmorel Automation\Spatial Aggregation\PriceProdGraphs\FlowElectricityHourly_%s.csv'%SC, delimiter=delim)
# fElP = pd.read_csv( r'C:\Users\mberos\OneDrive - Danmarks Tekniske Universitet\Work\Balmorel Automation\Spatial Aggregation\PriceProdGraphs\PriceElectricityHourly_%s.csv'%SC, delimiter=delim)
# fHP = pd.read_csv('PriceHeatHourly_%s.csv'%SC, delimiter=delim)
# fHD = pd.read_csv('DemandHeatHourly_%s.csv'%SC, delimiter=delim)
# fElD = pd.read_csv(r'C:\Users\mberos\OneDrive - Danmarks Tekniske Universitet\Work\Balmorel Automation\Spatial Aggregation\PriceProdGraphs\DemandElectricityHourly_%s.csv'%SC, delimiter=delim)
# fH2 = pd.read_excel('H2 Production.xlsx')


#%% ----------------------------- ###
###           Parameters          ###
### ----------------------------- ###

# Choices
RorC = 'R' # Region or country level?
reg = 'DK1'
country = 'GERMANY'
countryR = 'DE'
Y = '2050'
typ = 'TECH_TYPE' # Should be a column, e.g. TECH_TYPE, RRR, AAA, G
resfactor = 13 # Factor on flows, to get yearly results 
elprice_agg = np.max # function for aggregation of regions - average or max ?
bypass_eps = 'Y' # Bypass EPS values in electricity prices? This could be fair, if you have regions with very small electricity demand, making EPS electricity prices (not wrong)


### Colours
c = {'IMPORT' : [150/255, 185/255, 252/255],
     'BIOGAS' : [128/255, 159/255, 121/255],
     'NATGAS' : [0.2, 0.2, 0.2],
     'COAL' : [0, 0, 0],
     'LIGHTOIL' : [0.4, 0.4, 0.4],
     'FUELOIL' : [.4, .4, .4],
     'WATER' : [63/255, 37/255, 1],
     'WIND' : [83/255, 243/255, 133/255],
     'SUN' : [255/255, 254/255, 0],
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
p1, = ax.plot(x, fD.values[:,0]/1e3, 'k-')
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


# %%% ----------------------------- ###
# ###              Heat             ###
# ### ----------------------------- ###

# # Choices
# sens_SC = ''
# reg = 'SE3_large'
# Y = 2050
# typ = 'FFF'


# ### Colours
# c = {'IMPORT' : [150/255, 185/255, 252/255],
#      'BIOGAS' : [128/255, 159/255, 121/255],
#      'NATGAS' : [0, 0, 0],
#      'WATER' : [63/255, 37/255, 1],
#      'WIND' : [83/255, 243/255, 133/255],
#      'SUN' : [255/255, 254/255, 0],
#      'MUNIWASTE' : [150/255, 150/255, 150/255],
#      'WOODCHIPS' : [233/255, 67/255, 67/255],
#      'STRAW' : [241/255, 135/255, 135/255],
#      'PEAT' : [.8, .8, .8],
#      'ELECTRIC' : [252/255, 1, 137/255],
#      'NUCLEAR' : [137/255, 224/255, 1],
#      'HEAT' : [150/255, 67/255, 30/255],
#      'WASTEHEAT' : [255/255, 120/255, 67/255]}


# for com in ['HEAT']:#, 'HEAT']:
 
#     # Production
#     idx = fProd['AAA'] == reg
#     idx = idx & (fProd['COMMODITY'] == com)
#     idx = idx & (fProd['Y'] == Y)
    
#     fPr = fProd[idx].pivot_table(values='Val', index=['SSS', 'TTT'], columns=[typ],aggfunc=sum)
#     fPr[np.isnan(fPr)] = 0
    
#     print(reg, 'Heat Demand: [TWh]')
#     dems = fHD[(fHD['Y']==Y) & (fHD['AAA'] == reg)]
#     for cat in np.unique(dems['VARIABLE_CATEGORY']):
#         print(cat, ' = ', round(dems[dems['VARIABLE_CATEGORY'] == cat]['Val'].sum()/1e6*13,2))
    
#     # f = f + fFlI - fFlE
#     # f_temp = pd.DataFrame([], index=fPr.index)
#     # f_temp['IMPORT'] = fFlI
#     # f_temp['EXPORT'] = -fFlE
#     # f_temp[np.isnan(f_temp)] = 0
    
#     # f[np.isnan(f)] = 0
#     # f.columns = ['IMPORT']
#     # f = pd.DataFrame([], index=fPr.index)
#     # f['IMPORT'] = f_temp.sum(axis=1)
    
#     # f[fPr.columns] = fPr
    
#     fP = fHP[fHP['AAA'] == reg]    
#     fD = fHD[fHD['AAA'] == reg]      
   
        
#     # Price
#     idx = fP['Y'] == Y
#     fP = fP[idx].pivot_table(values='Val', index=['SSS', 'TTT'], aggfunc=sum)

#     # Demand
#     idx = fD['Y'] == Y 
#     fD = fD[idx].pivot_table(values='Val', index=['SSS', 'TTT'], aggfunc=sum)

#     ### Graph
#     fig, ax = plt.subplots(figsize=(11,4))
#     x = np.arange(0, 672, 672/len(fD))
#     temp = np.zeros(len(fD))
#     ps = []
#     for col in fPr:
#         ps.append(ax.fill_between(x, temp, temp+fPr[col].values/1e3, label=col, facecolor=np.array(c[col]).round(2)))
#         temp = temp + fPr[col].values/1e3       
    
#     p1, = ax.plot(x, fD.values/1e3, 'k-')
#     ax2 = ax.twinx()
#     p2, = ax2.plot(x, fP.values, 'r--', linewidth=1.5)
#     # ax.legend()
    
#     names = pd.Series(fPr.columns).str.lower().str.capitalize()
#     names = list(names) + ['Demand', 'Price']
    
#     ax.legend(ps+[p1, p2], names,
#               loc='center', bbox_to_anchor=(.5, 1.25), ncol=5)
#     ax.set_title(SC + ' - ' + reg + ' - ' + str(Y))
#     ax.set_ylabel('Heat [GW]')
#     ax.set_xlabel('Time [days]')
#     xticks = np.hstack(np.arange(0, 673, 168))
#     ax.set_xticks(xticks)
#     ax.set_xticklabels((xticks/24).astype(int))
#     # ax.set_xticklabels(['S%s-1'%])
#     ax2.set_ylabel('Price [€ / MWh]')
#     ax2.set_ylim([0, 40])
#     ax.set_xlim([0, 672])
    
#     fig.savefig(SC+'_'+str(Y)+'_'+reg+'HeatGraph.pdf', bbox_inches='tight')
#     # ax.set_xlim([200, 250])

#     # ax.set_ylim(-15000, 5000)
