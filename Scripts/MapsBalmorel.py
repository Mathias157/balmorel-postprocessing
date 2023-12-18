###!/usr/bin/env Balmorel
"""
This script has many options for designing maps of 
Balmorel results

It depends on a geofile, that should contain the exact name
of the region names in Balmorel - otherwise, results from
regions that are NOT in the geofile will not be shown! 
"""
#%% ----------------------------- ###
###       0. Script Settings      ###
### ----------------------------- ###


import geopandas as gpd
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
# import xarray as xr
from matplotlib.lines import Line2D
# import atlite # It worked to import it in console, and then outcomment here
# from csv import reader

# import json
# from descartes import PolygonPatch
# from mpl_toolkits.basemap import Basemap as Basemap

from pathlib import Path
import sys
import os
import glob

sys.path.append(r'C:\GAMS\39\apifiles\Python\api_38')
sys.path.append(r'C:\GAMS\39\apifiles\Python\gams')

from gams import GamsWorkspace

os.chdir(__file__.replace(r'\Scripts\MapsBalmorel.py', ''))

style = 'ppt'

if style == 'report':
    plt.style.use('default')
    fc = 'white'
elif style == 'ppt':
    plt.style.use('dark_background')
    fc = 'none'

#%% ----------------------------- ###
###        1. Preparations        ###
### ----------------------------- ###

### 1.1 Set Options


### Set options here.
#Structural options
filetype_input = 'gdx' #Choose input file type: 'gdx' or 'csv' 
market = 'Investment' #Choose from ['Balancing', 'DayAhead', 'FullYear', 'Investment']
COMMODITY = 'H2' #Choose from: ['Electricity', 'H2', 'Other']. Add to csv-files name (only relevant if filetype_input == 'csv'). If 'Other': go to cell 1.4.0.
SCENARIO = 'eur-system-test_Iter0'
YEAR = '' #Add year to read file name (e.g. '2025', '2035', 'full')
SUBSET = '' #Add subset to read file name (e.g. 'full')
year = 2050 #Year to be displayed
LINES = 'Capacity' #Choose from: ['Capacity', 'Flow', 'CongestionFlow']. For 'CongestionFlow', exo_end automatically switches to 'Total'.
exo_end = 'Total' # Choose from ['Endogenous', 'Exogenous', 'Total']. For 'CongestionFlow', exo_end automatically switches to 'Total'.
S = 'S02' #Season 
T = 'T073' #Hour  

# Geofile
path_to_geofile = 'Input/FR.geojson'
geo_file_region_column = 'zoneName'
path_to_results = r'C:\Users\mathi\Danmarks Tekniske Universitet\PhD in Transmission and Sector Coupling - Dokumenter\Deliverables\Smart-coupling of Balmorel and Antares\Harmonisation Analyses'

# Alternative geofile (off, at the moment)
AltGeo = 'Balmorel'  
# AltGeo = 'MUNI' # The other type of polygons, if traditional Balmorel regions areas not used
# AltGeoCol = 'NUTS_ID' # Column to search in file of other type of polygon
AltGeoCol = 'GID_2'
# AltGeoPath = r'C:\Users\mberos\OneDrive - Danmarks Tekniske Universitet\Dokumenter\Balmorel\base\auxils\create_BalmorelInput\Data\Shapefiles\NUTS_RG_01M_2021_4326\NUTS_RG_01M_2021_4326.shp' # Path to other type of polygons
AltGeoPath = r'geojson'


# hubs
hub_display = False
hub_size = 100.6
hub_decimals = 10 #Number of decimals shown for hub capacities
background_hubsize = True #Displaying the true size of the hub as a circle on the map.
hub_area = 100.8 #MW / km^2, background hub size on map. 
hub_area_opacity = 10.7 #Opacity of background hub size. 


#Visual options
label_min = 1 #Minimum transmission capacity (GW) shown on map in text
font_line = 12 #Font size of transmission line labels
font_hub = 12 #Font size of hub labels
font_region = 10 #Font size of region labels
line_decimals = 1 #Number of decimals shown for line capacities
line_width_constant = 1 #Constant related to thickness of lines: the higher the number, the narrower the lines will be
flowline_breaks = [0, 40, 94.999, 100] #Breaks for different congestion categories
legend_values = ['Fully congested', '40-95% congested', '< 50% congested'] #Values displayed in legend
cat = 'linear' # 'linear' = Capacities are scaled linearly, 'cluster' = capacities are clustered in groups
cluster_groups = [0, 5, 10, 30] # The capacity groupings if cat is 'cluster'
cluster_widths = [.2, 1, 3, 6] # The widths for the corresponding capacity group (has to be same size as cluster_groups)


#colors
background_color = 'white'
regions_ext_color = 'lightgrey'
regions_model_color = 'grey'
region_text = 'black'
capline_color = 'orange' #you can use orange or others green
flowline_color = ['#3D9200', '#feb24c','#960028']
line_text = 'black'
hub_color = 'lightblue'
hub_background_color = 'lightblue'
hub_text = 'black'
net_colour = 'green' # Colour of network


### 1.2 Functions

# In[ ]:


def read_paramenter_from_gdx(ws,gdx_name,parameter_name,**read_options):
     
     for item in read_options.items():
         if item[0]=="field":
                     field=item[1]

     
     db = ws.add_database_from_gdx(gdx_name)
     
     if "field" in locals() :
         if field=="Level":
             par=dict( (tuple(rec.keys), rec.level) for rec in db[parameter_name] )
         elif field=="Marginal":
             par=dict( (tuple(rec.keys), rec.marginal) for rec in db[parameter_name] )
         elif field=="Lower":
             par=dict( (tuple(rec.keys), rec.lower) for rec in db[parameter_name] )
         elif field=="Upper":
                 par=dict( (tuple(rec.keys), rec.lower) for rec in db[parameter_name] )
         elif field=="Scale":
                     par=dict( (tuple(rec.keys), rec.lower) for rec in db[parameter_name] )
         elif field=="Value":
                     par=dict( (tuple(rec.keys), rec.value) for rec in db[parameter_name] )
     else:
         if "Parameter" in str(type(db[parameter_name])):
             par=dict( (tuple(rec.keys), rec.value) for rec in db[parameter_name] )
         elif "Variable" in str(type(db[parameter_name])):
             par=dict( (tuple(rec.keys), rec.level) for rec in db[parameter_name] )
         elif "Set" in str(type(db[parameter_name])):
             par=dict( (tuple(rec.keys), rec.text) for rec in db[parameter_name] )
         elif "Equation" in str(type(db[parameter_name])):
             par=dict( (tuple(rec.keys), rec.level) for rec in db[parameter_name] )
             
     return par , db[parameter_name].get_domains_as_strings()
 


def dataframe_from_gdx(gdx_name,parameter_name,**read_options):
     
     ws = GamsWorkspace(os.getcwd(),)


     var, cols= read_paramenter_from_gdx(ws,gdx_name,parameter_name,**read_options)
     if "custom_domains" in read_options :
         cols= read_options["custom_domains"]

     
     unzip_var= list(zip(*var))
     
     new_dict=dict()
     i=0
     for col in cols:
         new_dict[col]= list(unzip_var[i])
         i=i+1
         
     
     if "field" in read_options :
         field= read_options.get("field")
         new_dict[field]=[]
         new_dict[field]=list(var.values())
     else:
         new_dict["Value"]=list(var.values())
         
     df=pd.DataFrame.from_dict(new_dict)

     return df



# In[ ]:

# ### 1.3 Read geographic files

project_dir = Path('.\Input')

geo_file = gpd.read_file(path_to_geofile)

# #Load coordinates files 
# df_unique = pd.read_csv(project_dir/'coordinates_RRR.csv')
# df_region = df_unique.loc[df_unique['Type'] == 'region', ]
df_bypass = pd.read_csv(project_dir/'bypass_lines.csv') # coordinates of 'hooks' in indirect lines, to avoid going trespassing third regions
# if AltGeo == 'MUNI':
#     df_altreg = gpd.read_file(AltGeoPath)
#     df_altreg.GID_2 = df_altreg.GID_2.str.replace('.', '_').str.replace('DNK', 'DK')

# #Define names of geojson and shapefile layers
# r_in = list(df_unique.loc[(df_unique['Display'] == 1) & (df_unique['Type'] == 'region'), 'RRR'])
# r_out = list(df_unique.loc[(df_unique['Display'] == 0) & (df_unique['Type'] == 'region'), 'RRR'])

# layers_in = {region: '' for region in r_in}
# layers_out = {region: '' for region in r_out}

# #Create dictionaries with layer names for each region; if both a shapefile and geojson file are available for one region, the geojson file is used. 
# for region in r_in:
#     layers_in[region] = glob.glob(f'{project_dir}/'+ region + '.geojson')
#     if bool(layers_in[region]) == False:
#         layers_in[region] = glob.glob(f'{project_dir}/geo_files/shapefiles/'+ region + '.shp')
# for region in r_out:
#     layers_out[region] = glob.glob(f'{project_dir}/'+ region + '.geojson')
#     if bool(layers_out[region]) == False:
#         layers_out[region] = glob.glob(f'{project_dir}/geo_files/shapefiles/'+ region + '.shp')

# for region in layers_in:
#     layers_in[region] = str(layers_in[region])[2:-2] #Remove brackets from file names
# for region in layers_out:
#     layers_out[region] = str(layers_out[region])[2:-2] #Remove brackets from file names

    
# #Convert shapefiles to geojson files  
# for region in layers_out:
#     if layers_out[region][-4:] == '.shp':
#         gpd.read_file(layers_out[region]).to_file(f'{project_dir}/geo_files/geojson_files/'+ region + '.geojson', driver='GeoJSON')
#         layers_out[region] = layers_out[region].replace('shapefiles', 'geojson_files').replace('.shp', '.geojson')


# # 1.4 Read run-specific files

# ##### 1.4.0 If COMMODITY == 'Other': define variables or file names

# In[ ]:


if COMMODITY == 'Other':
    if filetype_input == 'gdx':
        var_list = ['G_CAP_YCRAF', 'XH2_CAP_YCR', 'XH2_FLOW_YCRST', 'PRO_YCRAGFST'] #Fill in variables to read, e.g. ['G_CAP_YCRAF', 'X{COMMODITY}_CAP_YCR', 'X{COMMODITY}_FLOW_YCRST', 'PRO_YCRAGST']
    if filetype_input == 'csv':
        flow_file = 'FlowH2Hourly_'+ SCENARIO + '_' + YEAR + '_' + SUBSET + '.csv' #Fill in flow file name if applicable, e.g. 'Flow{COMMODITY}Hourly_'+ SCENARIO + '_' + YEAR + '_' + SUBSET + '.csv'
        transcap_file = 'CapacityH2Transmission_' + SCENARIO + '_' + YEAR + '_'+ SUBSET + '.csv' #Fill in transmission capacity file name, e.g. 'Capacity{COMMODITY}Transmission_'+ SCENARIO + '_' + YEAR + '_'+ SUBSET + '.csv' 


# ### 1.4A - GDX Inputs

# ##### 1.4A.1 Function: reading gdx-files

# In[ ]:


if filetype_input == 'gdx':
    def df_creation(gdx_file, varname):
        df = pd.DataFrame()
        if '_' in gdx_file:
                # if yes: extract scenario name from gdx filename
            scenario = gdx_file.split('_', 3)[-3]
            year = gdx_file.split('_', 3)[-2]
            subset = gdx_file.split('_', 3)[-1][:-4]
            market = gdx_file.split('\\', 1)[0].split('/',3)[-1]
        else:
               # if no: use nan instead
            scenario = 'nan'

        # create empty temporary dataframe and load the gdx data into it
        temp = pd.DataFrame()
        # temp = gdxpds.to_dataframe(gdx_file, varname, gams_dir=gams_dir,
        #                        old_interface=False)
        
        temp=dataframe_from_gdx(gdx_file,varname)

        # add a scenario column with the scenario name of the current iteration
        temp['Scenario'] = scenario
        temp['Market']  = market
        temp['run'] = scenario + '_' + year + '_' + subset

        # rearrange the columns' order
        cols = list(temp.columns)
        cols = [cols[-1]] + cols[:-1]
        temp = temp[cols]

        # concatenate the temporary dataframe to the preceeding data
        df = pd.concat([df, temp], sort=False)
        return df


# ##### 1.4A.2 - Define var_list

# In[ ]:


if filetype_input == 'gdx':
    if COMMODITY == 'Electricity':
        var_list = []
        if LINES == 'Capacity' or LINES == 'CongestionFlow' or LINES == 'Flow': 
            var_list = var_list + ['G_CAP_YCRAF', 'X_CAP_YCR']
        if LINES == 'Flow' or LINES == 'CongestionFlow':
            var_list = var_list + ['X_FLOW_YCRST']
        if hub_display == True:
            var_list = var_list + ['PRO_YCRAGFST']
    if COMMODITY == 'H2':
        var_list = []
        if LINES == 'Capacity' or LINES == 'CongestionFlow' or LINES == 'Flow': 
            var_list = var_list + ['G_CAP_YCRAF', 'XH2_CAP_YCR']
        if LINES == 'Flow' or LINES == 'CongestionFlow':
            var_list = var_list + ['XH2_FLOW_YCRST']
        if hub_display == True:
            var_list = var_list + ['PRO_YCRAGFST']


# ##### 1.4A.3 - Use function to read inputs

# In[ ]:


if filetype_input == 'gdx':
    runs = list()
    gdx_file_list = list()

    # directory to the input gdx file(s)
    #gdx_file_list = gdx_file_list + glob.glob('./input/results/'+ market + '/*.gdx')
    
    if (YEAR == '') & (SUBSET == ''):
        gdx_file =  glob.glob(path_to_results + '\\MainResults_' + SCENARIO + '.gdx')
    else:
        gdx_file =  glob.glob('./input/results/'+ market + '\\MainResults_' + SCENARIO + '_'  + YEAR + '_' + SUBSET + '.gdx')
    gdx_file = gdx_file[0]

    all_df = {varname: df for varname, df in zip(var_list,var_list)}


    for varname, df in zip(var_list, var_list):
        all_df[varname] = df_creation(gdx_file, varname)
        if all_df[varname]['run'][0] not in runs:
            runs.append(all_df[varname]['run'][0])

    #run_dict = dict(zip(gdx_file_list, runs) )
    #all_df = dict((run_dict[key], value) for (key, value) in all_df.items())
    
    #Transmission capacity data
    if LINES == 'Capacity' or LINES == 'CongestionFlow'  or LINES == 'Flow':
        if COMMODITY == 'Electricity':
            df_capacity = all_df['X_CAP_YCR']
        if COMMODITY == 'H2':
            df_capacity = all_df['XH2_CAP_YCR']
        if COMMODITY == 'Other':
            df_capacity = all_df[var_list[1]]

    #Transmission flow data
    if LINES == 'Flow' or LINES == 'CongestionFlow' : 
        if COMMODITY == 'Electricity':
            df_flow = all_df['X_FLOW_YCRST']
        if COMMODITY == 'H2':
            df_flow = all_df['XH2_FLOW_YCRST']
    if COMMODITY == 'Other':
        if LINES == 'Flow':
            df_flow = all_df[var_list[1]]
        if LINES == 'CongestionFlow':
            df_flow = all_df[var_list[2]]


# ##### 1.4A.4 - Hub data

# In[ ]:


if filetype_input == 'gdx' and hub_display == True:
    hub_windgen = (pd.read_csv(project_dir/'geo_files/hub_technologies.csv', sep = ',', quotechar = '"').hub_name) 
    df_capgen = all_df['G_CAP_YCRAF']
    if LINES == 'Flow' or LINES == 'CongestionFlow':
        df_hubprod = all_df['PRO_YCRAGFST']
        df_hubprod['Y'] = df_hubprod['Y'].astype(int)
        df_hubprod = df_hubprod.loc[(df_hubprod['G'].isin(hub_windgen)) & (df_hubprod['TECH_TYPE'] == 'WIND-OFF') &                                     (df_hubprod['Y']==year) & (df_hubprod['SSS'] == S) & (df_hubprod['TTT']==T), ]


# ### 1.4B1 - Read CSV files

# In[ ]:


map_name = 'Transmission' + COMMODITY + '_' + LINES + '_' + str(year) + '_Map.html'
if filetype_input == 'csv':
    generation_file = 'CapacityGeneration_'+  SCENARIO + '_' + YEAR + '_' + SUBSET + '.csv'
    if COMMODITY == 'Electricity':
        flow_file = 'FlowElectricityHourly_'+ SCENARIO + '_' + YEAR + '_' + SUBSET + '.csv'
        transcap_file = 'CapacityElectricityTransmission_'+ SCENARIO + '_' + YEAR + '_'+ SUBSET + '.csv'
    if COMMODITY == 'H2':
        flow_file = 'FlowH2Hourly_'+ SCENARIO + '_' + YEAR + '_' + SUBSET + '.csv'
        transcap_file = 'CapacityH2Transmission_'+ SCENARIO + '_' + YEAR + '_'+ SUBSET + '.csv'
     
    #Transmission capacity data
    df_capacity = pd.read_csv(str(project_dir) + '/results/' + str(market) + '/' + str(transcap_file), sep = ',', quotechar = '"') 
    #Transmission flow data
    if LINES == 'Flow' or LINES == 'CongestionFlow':
        df_flow = pd.read_csv(str(project_dir) + '/results/' + str(market) + '/' + str(flow_file), sep = ',', quotechar = '"')

    if hub_display == True:
        prod_file = 'ProductionHourly_'+ SCENARIO + '_' + YEAR + '_' + SUBSET + '.csv'
        hub_windgen = (pd.read_csv(project_dir/'geo_files/hub_technologies.csv', sep = ',', quotechar = '"').hub_name) 
        #Generation capacity data
        df_capgen = pd.read_csv(str(project_dir) + '/results/' + str(market) + '/' + str(generation_file), sep = ',', quotechar = '"') 
        if LINES == 'Flow' or LINES == 'CongestionFlow':
        #Hub production data
            df_hubprod = pd.read_csv(str(project_dir) + '/results/' + str(market) + '/' + str(prod_file), sep = ',', quotechar = '"') 
            df_hubprod = df_hubprod.loc[(df_hubprod['G'].isin(hub_windgen)) & (df_hubprod['TECH_TYPE'] == 'WIND-OFF') &                                         (df_hubprod['Y']==year) & (df_hubprod['SSS'] == S) & (df_hubprod['TTT']==T), ]


# ### 1.4B2 - Calibrate column names

# In[ ]:


column_dict = {'Val':'Value', 'Y':'Year', 'C':'Country'}
if LINES == 'Capacity' or LINES == 'CongestionFlow':
    df_capacity = df_capacity.rename(columns = column_dict)
if LINES == 'Flow' or LINES == 'CongestionFlow':
    df_flow = df_flow.rename(columns = column_dict)
if hub_display == True:
    df_capgen = df_capgen.rename(columns = column_dict)
    if LINES == 'Flow' or LINES == 'CongestionFlow': 
            df_hubprod = df_hubprod.rename(columns = column_dict)


# # 2 Processing of dataframes

# ### 2.1 Replace "EPS" with 0

# In[ ]:


#Replace possible "Eps" with 0
df_capacity.Value=df_capacity.Value.replace('Eps', 0)
df_capacity.Value=pd.to_numeric(df_capacity.Value)
if LINES == 'Flow' or LINES == 'CongestionFlow': #Skip this cell in case LINES == 'Capacity'
    df_flow.Value=df_flow.Value.replace('Eps', 0)
    df_flow.Value=pd.to_numeric(df_flow.Value)
if hub_display == True:
    df_capgen.Value=df_capgen.Value.replace('Eps', 0)
    df_capgen.Value=pd.to_numeric(df_capgen.Value)
    if LINES == 'Flow' or LINES == 'CongestionFlow':
        df_hubprod.Value=df_hubprod.Value.replace('Eps', 0)
        df_hubprod.Value=pd.to_numeric(df_hubprod.Value)


# In[ ]: 
### 2.2 Add Coordinates + Select Time + Convert Units


#Flows
if LINES == 'Flow' or LINES == 'CongestionFlow': #Skip this cell in case LINES == 'Capacity'
    df_flow['Year'] = df_flow['Year'].astype(int)
    #Keep only data from moment of interest
    df_flow = df_flow.loc[df_flow['Year'] == year] 
    df_flow = df_flow.loc[df_flow['SSS'] == S,]
    df_flow = df_flow.loc[df_flow['TTT'] == T, ]
    for i,row in df_flow.iterrows():
        for j in range(0,len(geo_file)):
            if df_flow.loc[i,'IRRRE'] == geo_file.loc[j, geo_file_region_column]:  
                df_flow.loc[i,'LatExp'] = geo_file.loc[j].geometry.centroid.y       
                df_flow.loc[i,'LonExp'] = geo_file.loc[j].geometry.centroid.x       
            if df_flow.loc[i,'IRRRI'] == geo_file.loc[j, geo_file_region_column]:  
                df_flow.loc[i,'LatImp'] = geo_file.loc[j].geometry.centroid.y       
                df_flow.loc[i,'LonImp'] = geo_file.loc[j].geometry.centroid.x      

    #Convert flow from MWh to GWh
    df_flow['Value'] = df_flow['Value'] / 1000
    df_flow = df_flow.reset_index(drop = True)
    if len(df_flow) == 0:
        print("Error: Timestep not in data; check year, S and T.")
        sys.exit()


# In[ ]:
# ### 2.3 Group hub data



#Generation Capacities
if hub_display == True:
    df_capgen['Year'] = df_capgen['Year'].astype(int)
    # df_capgen = df_capgen.merge(df_unique, on = 'RRR', how = 'left', left_index = True).reset_index(drop = True) #Add coordinates of each region
    #poly
    df_capgen = df_capgen.merge(geo_file, on = geo_file_region_column, how = 'left' ).reset_index(drop = True) #Add coordinates of each region
    df_capgen = df_capgen.loc[df_capgen['Year'] == year] #Keep only data from year of interest
    df_hubcap = df_capgen.loc[df_capgen['G'].isin(hub_windgen),] #Keep only hub data 
    df_hubcap_agg = pd.DataFrame(df_hubcap.groupby(['Year', 'Country', 'RRR', 'Lat', 'Lon'])['Value'].sum().reset_index()) #Sum all capacities (of different wind turbines) at each location
    df_hubcap_agg['Radius'] = np.sqrt(df_hubcap_agg['Value'] * 1000 / hub_area / np.pi) # Create column of hub radius (in kilometres)

    if LINES == 'Flow' or LINES == 'CongestionFlow':
        #Merge all relevant hub info into one dataframe
        df_hubprod = pd.DataFrame(df_hubprod.groupby(['Year', 'Country', 'RRR'])['Value'].sum().reset_index()) #Sum all production (of different wind turbines) at each location
        df_hubprod.Value = df_hubprod.Value/1000
        df_hubprod.rename(columns = {'Value': 'prod_GWh'}, inplace = True)
        df_hub = pd.merge(df_hubcap_agg, df_hubprod[['RRR', 'prod_GWh']], on = 'RRR', how = 'left', left_index = True).reset_index(drop = True) 
        #Display a zero instead of NaN values (i.e. if there is no production in that hour, so df_hubprod row does not exist)
        df_hub.loc[df_hub.prod_GWh.isna() == True, 'prod_GWh'] = 0
    else: 
        df_hub = df_hubcap_agg.copy()
        


# In[ ]:
# ### 2.4 Prepare capacity dataframe
if AltGeo == 'NORD':
    df_capacity.IRRRE = df_capacity.IRRRE.str.replace('_','')
    df_capacity.IRRRI = df_capacity.IRRRI.str.replace('_','')


#Transmission Capacities
if LINES == 'Capacity' or LINES == 'CongestionFlow': #Skip this cell in case LINES == 'Flow'
    df_capacity['Year'] = df_capacity['Year'].astype(int)
    df_capacity = df_capacity.loc[df_capacity['Year'] == year, ].reset_index(drop = True) #Keep only data from year of interest
    if exo_end == 'Total' or LINES == 'CongestionFlow':
        col_keep = list(np.delete(np.array(df_capacity.columns),np.where((df_capacity.columns == 'VARIABLE_CATEGORY') | (df_capacity.columns == 'Value')) )) #Create list with all columns except 'Variable_Category' and 'Value'
        df_capacity = pd.DataFrame(df_capacity.groupby(col_keep)['Value'].sum().reset_index() )#Sum exogenous and endogenous capacity for each region
    if exo_end == 'Endogenous' and LINES != 'CongestionFlow':
        df_capacity = df_capacity.loc[df_capacity['VARIABLE_CATEGORY'] == 'ENDOGENOUS', ]
    if exo_end == 'Exogenous' and LINES != 'CongestionFlow':
        df_capacity = df_capacity.loc[df_capacity['VARIABLE_CATEGORY'] == 'EXOGENOUS', ]

    for i,row in df_capacity.iterrows():
        for j in range(0,len(geo_file)):
            if df_capacity.loc[i,'IRRRE'] ==  geo_file.loc[j, geo_file_region_column]:  
                df_capacity.loc[i,'LatExp'] = geo_file.loc[j].geometry.centroid.y       
                df_capacity.loc[i,'LonExp'] = geo_file.loc[j].geometry.centroid.x       
            if df_capacity.loc[i,'IRRRI'] ==  geo_file.loc[j, geo_file_region_column]:  
                df_capacity.loc[i,'LatImp'] = geo_file.loc[j].geometry.centroid.y       
                df_capacity.loc[i,'LonImp'] = geo_file.loc[j].geometry.centroid.x      
    
    # Check alternative regions in missing lat/lon
    # idx = (df_capacity.loc[:,'LatExp'].isna()) | (df_capacity.loc[:,'LatImp'].isna())
    if AltGeo != 'Balmorel':
        for i,row in df_capacity.iterrows():
            for j in range(0,len(df_altreg)):
                if df_capacity.loc[i,'IRRRE'] == df_altreg.loc[j, AltGeoCol]:
                    df_capacity.loc[i,'LatExp'] = df_altreg.loc[j].geometry.centroid.y
                    df_capacity.loc[i,'LonExp'] = df_altreg.loc[j].geometry.centroid.x
                if df_capacity.loc[i,'IRRRI'] == df_altreg.loc[j, AltGeoCol]:
                    df_capacity.loc[i,'LatImp'] = df_altreg.loc[j].geometry.centroid.y
                    df_capacity.loc[i,'LonImp'] = df_altreg.loc[j].geometry.centroid.x
                
        

    if len(df_capacity) == 0:
        print("Error: No capacity found. Check year and exo_end.")
        sys.exit()


# In[ ]:
# ### 2.5 Add bypass coordinates for indirect lines



if LINES == 'Capacity':
    df_bypass = pd.merge(df_bypass, df_capacity[['Year', 'Country', 'IRRRE', 'IRRRI', 'UNITS', 'Value']], on = ['IRRRE', 'IRRRI'], how = 'left')
    #Replace existing row by 2 bypass rows
    keys = list(df_bypass.columns.values)[0:2]
    i1 = df_capacity.set_index(keys).index
    i2 = df_bypass.set_index(keys).index
    df_capacity = df_capacity[~i1.isin(i2)] #Delete existing rows that need bypass
    df_capacity = df_capacity._append(df_bypass, ignore_index = True, sort = True) #Append bypass rows
    
if LINES == 'Flow' or LINES == 'CongestionFlow': #Skip this cell in case LINES == 'Capacity'
    df_bypass = pd.merge(df_bypass, df_flow[['Year', 'Country', 'IRRRE', 'IRRRI', 'SSS', 'TTT', 'UNITS', 'Value']], on = ['IRRRE', 'IRRRI'], how = 'left').dropna()
    #Replace existing row by 2 bypass rows
    keys = list(df_bypass.columns.values)[0:2]
    i1 = df_flow.set_index(keys).index
    i2 = df_bypass.set_index(keys).index
    df_flow = df_flow[~i1.isin(i2)]#Delete existing rows that need bypass
    df_flow = df_flow.append(df_bypass, ignore_index = True, sort = True)#Append bypass rows


# In[ ]:
# ### 2.6 Calculate Congestion



if LINES == 'CongestionFlow': #Skip this cell in case LINES != 'CongestionFlow'
    df_flow = pd.merge(df_flow, df_capacity[['Year', 'Country', 'IRRRE', 'IRRRI', 'Value']], on = ['Year', 'Country', 'IRRRE', 'IRRRI'], how = 'left')
    df_flow.rename(columns={'Value_x': 'Value', 'Value_y' : 'Capacity'}, inplace = True)
    df_flow['Congestion'] = df_flow['Value'] / df_flow['Capacity'] * 100

    #Create color codes for congestion of lines
    df_flow['color'] = pd.cut(df_flow['Congestion'], bins = flowline_breaks, labels = flowline_color )



# In[ ]:
# ### 2.7 One direction capacity  lines



#When capacity is not the same in both directions, display one:
for i,row in df_capacity.iterrows():
    for k,row in df_capacity.iterrows():
        if (df_capacity.loc[k,'IRRRE'] == df_capacity.loc[i,'IRRRI']) & (df_capacity.loc[k,'IRRRI'] == df_capacity.loc[i,'IRRRE']) & (df_capacity.loc[k,'Value'] != df_capacity.loc[i,'Value']):
            df_capacity.loc[i,'Value'] = df_capacity.loc[k,'Value']


# In[ ]:
# ###  2.8 Define line centers



#Define centre of each transmission line
if LINES == 'Flow' or LINES == 'CongestionFlow': #Skip this cell in case LINES == 'Capacity'
    df_flow['LatMid'] = (df_flow['LatImp'] + df_flow['LatExp']) /2
    df_flow['LonMid'] = (df_flow['LonImp'] + df_flow['LonExp']) /2
if LINES == 'Capacity' or LINES == 'CongestionFlow': #Skip this cell in case LINES == 'Flow'
    df_capacity['LatMid'] = (df_capacity['LatImp'] + df_capacity['LatExp']) /2
    df_capacity['LonMid'] = (df_capacity['LonImp'] + df_capacity['LonExp']) /2



# In[ ]:
# # 3 Plotting the Results


# try_g = df_capacity

# #make a concate
# [', '.join(str(x) for x in y) for y in map(tuple, df_capacity[['LatExp', 'LonExp']].values)]

# grid_coordinates = {}

# for i,row in df_capacity.iterrows():
    
#     y1 = df_capacity.loc[i,'LatExp']
#     x1 =  df_capacity.loc[i,'LonExp']
#     y2 = df_capacity.loc[i,'LatImp']
#     x2 = df_capacity.loc[i,'LonImp']
    
#     start = [x1, y1]
#     finish = [x2,y2]

#     grid_coordinates[i] = [start,finish]



# def df_to_geojson(dictionary):
#     # create a new python dict to contain our geojson data, using geojson format
#     geojson = {'type': 'FeatureCollection', 'features': []}
    
#     # loop through each row in the dataframe 
#     for key, value in dictionary.items():
#         # create a feature template to fill in
#         feature = {'type': 'Feature', 
#                    'properties': {},
#                    'geometry': {'type':'Polygon',
#                                 'coordinates':[]}}
        
#         # fill in the coordinates 
#         feature['geometry']['coordinates'] = [value]
        
#         # create properies with region id
#         feature['properties']['region'] = key + 1
#         # add this feature (convert dataframe row) to the list of features inside our dict
#         geojson['features'].append(feature)
    
#     return geojson


# electricity_network = df_to_geojson(grid_coordinates)

# # the json file where the output must be stored 
# out_file = open("electricity_network.json", "w") 
# dict1 = 'output/Data'   
# json.dump(dict1, out_file, indent = 6) 
# out_file.close() 


# df_electricity_network = pd.DataFrame(electricity_network) # Before: electricity_network['']


# In[]
### 3.1 Plotting the regions
# With projection
projection = ccrs.EqualEarth()
fig, ax = plt.subplots(figsize=(12, 12), subplot_kw={"projection": projection}, dpi=100,
                       facecolor=fc)

# fig, ax = plt.subplots(figsize=(12, 12), dpi=100,
#                        facecolor=fc)
ax.set_title(' - '.join((SCENARIO, str(year))))
# ax.set_title('Ingen interk.')

# Adding shapefiles
ax.add_geometries(geo_file.geometry, crs = projection,
            facecolor=[.6, .6, .6], edgecolor='grey',
            linewidth=.2)

ax.set_facecolor(fc)
# EU limits
ax.set_xlim(-11,32)      
ax.set_ylim(35,72)
# DK Limits 
# ax.set_xlim(7.5,15.5)      
# ax.set_ylim(54,58) 
# Nordic limits  
# ax.set_xlim(5,17)      
# ax.set_ylim(50,70)

#electricity_network.plot(ax=ax, color='red')

# max_cap_line = df_capacity.Value.max()
# min_cap_line = df_capacity.Value.min()


# slack = df_capacity['Value']/5
# df_capacity['Linewidth'] = slack


### 3.2 Adding transmission lines
# A function for finding the nearest value in an array
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

lines = []
for i,row in df_capacity.iterrows(): 
    y1 = df_capacity.loc[i,'LatExp']
    x1 =  df_capacity.loc[i,'LonExp']
    y2 = df_capacity.loc[i,'LatImp']
    x2 = df_capacity.loc[i,'LonImp']
    cap = df_capacity.loc[i,'Value']
    
    if cat == 'cluster':
        nearest = find_nearest(cluster_groups, cap) 
        width = np.array(cluster_widths)[cluster_groups == nearest]
    else:
        width = cap

    # Print an error message, if capacity is a NaN value
    if not(np.isnan(cap)):
        l, = ax.plot([x1,x2], [y1,y2], color = net_colour, linewidth = width/line_width_constant)
        lines.append(l)
    else:
        print("There's a NaN value in line\nIRRRE %s\nIRRRI %s"%(df_capacity.loc[i, 'IRRRE'], df_capacity.loc[i, 'IRRRI']))

    # Add labels to lines   
    if df_capacity.loc[i,'Value'] >= label_min:
            label = "{:.1f}".format(df_capacity.loc[i,'Value'])
            plt.annotate(label, # this is the value which we want to label (text)
            (df_capacity.loc[i,'LonMid'],df_capacity.loc[i,'LatMid']), # x and y is the points location where we have to label
            textcoords="offset points",
            xytext=(0,-4), # this for the distance between the points
            # and the text label
             ha='center',
             )
            #,arrowprops=dict(arrowstyle="->", color='green'))

#%
### 3.3 Adding HUB Capacities
if hub_display:
    idx = df_hubcap_agg['Year'] == year
    temp = df_hubcap_agg[idx]
    for i,row in temp.iterrows():
        
        markersize = row['Value']
        
        ax.plot(row['Lon'], row['Lat'], 'o', color=[.8, .8, 1], 
                markersize=markersize, zorder=-1)
        
        
#
### 3.3 Making a legend
if COMMODITY == 'Electricity':
    subs = 'el'
else:
    subs = 'th'

if cat == 'cluster':
    # Create lines for legend
    lines = []
    string = []
    for i in range(len(cluster_groups)):
        # The patch
        lines.append(Line2D([0], [0], linewidth=cluster_widths[i]/line_width_constant,
                            color=net_colour))
        # The text
        if i == 0:
            ave = (cluster_groups[i] + cluster_groups[i+1])/2
            string.append('$\\less$ %0.1f GW$_\mathrm{%s}$'%(ave, subs))
        elif i == len(cluster_groups)-1:
            ave = (cluster_groups[i] + cluster_groups[i-1])/2
            string.append('$\\geq$ %0.1f GW$_\mathrm{%s}$'%(ave, subs))
        else:
            ave0 = (cluster_groups[i] + cluster_groups[i-1])/2
            ave1 = (cluster_groups[i] + cluster_groups[i+1])/2
            string.append('%0.1f-%0.1f GW$_\mathrm{%s}$'%(ave0, ave1, subs))
    
    ax.legend(lines, string, loc='center',
              bbox_to_anchor=(.2, .88 ))
    
##% 3.4 Save map
# plt.savefig("network_MUNI_2DE_NoS_MoreFLH_noBio_LSNOstevns.svg", bbox_inches="tight", transparent=True)
plt.savefig(f"{SCENARIO}_{year}.png", bbox_inches="tight", transparent=True)
