# -*- coding: utf-8 -*-
"""
Created on Wed Nov 23 16:42:35 2022

@author: jonpr
"""

# Regional social care use: England
import os
os.chdir(r"C:\Users\jonpr\Documents\Data projects\Python\FrontDoor")
path = os.getcwd()

import pandas as pd
import plotly.express as px
from plotly.offline import plot
import json

# Load SALT/ASCFR dataset 2016-2021
df = pd.read_csv(os.path.join(path, 'LA_dataset.csv'))

# Specify age range: either 18-64 or over 65
Age = '65' # '18_64' or '65'

# Specify variables of interest
AccessOptions = ['DischargefromHospital_'+Age,'Diversion_hosp_serv_'+Age,'self_deplet_funds_'+Age,'depl_fund_DP_'+Age, 'CommunityOtherRoute_'+Age,'Prison_'+Age]
DestinationOptions = ['ShortTermCaretomaximiseind_'+Age,'LongTermCareNursing_'+Age,'LongTermCareResidential_'+Age,'LongTermCareCommunity_'+Age,'LongTermCarePrison_'+Age,
                      'NHSFundedCare_'+Age,'EndofLife_'+Age,'OngoingLowLevelSupport_'+Age,'ShortTermCareothershortter_'+Age,'UniversalServicesSignpostedt_'+Age,
                      'NoServicesProvidedDeceased_'+Age,'NoServicesProvided_'+Age]
CareVs = ['ShortTermCaretomaximiseind_'+Age,'ShortTermCareothershortter_'+Age,'EndofLife_'+Age,'LongTermCareNursing_'+Age,'LongTermCareResidential_'+Age,'LongTermCareCommunity_'+Age,'LongTermCarePrison_'+Age,'NHSFundedCare_'+Age,'OngoingLowLevelSupport_'+Age]
NoCareVs = ['NoServicesProvided_'+Age,'NoServicesProvidedDeceased_'+Age,'UniversalServicesSignpostedt_'+Age]
STCareVs = ['ShortTermCaretomaximiseind_'+Age,'ShortTermCareothershortter_'+Age,'EndofLife_'+Age]
LTCareVs = ['LongTermCareNursing_'+Age,'LongTermCareResidential_'+Age,'LongTermCareCommunity_'+Age,'LongTermCarePrison_'+Age,'NHSFundedCare_'+Age,'OngoingLowLevelSupport_'+Age]
RegionalID = ['Geography_code','LAname'] 

# Convert social care access and destination variables to % of population
acc_df = pd.DataFrame()
acc_df[AccessOptions] = df[AccessOptions].apply(lambda x: x/df['Population_'+Age]*100)
acc_df = pd.concat([df[RegionalID],df['year'].astype(int), acc_df[AccessOptions]], axis=1)

dest_df = pd.DataFrame()
dest_df[DestinationOptions] = df[DestinationOptions].apply(lambda x: x/df['Population_'+Age]*100)
dest_df = pd.concat([df[RegionalID],df['year'].astype(int), dest_df[DestinationOptions]], axis=1)

# Drop 2016 due to missing population data
acc_df, dest_df = acc_df[acc_df['year'] != 2016], dest_df[dest_df['year'] != 2016]

# Create dataframe of totals
ScTotals = pd.concat([acc_df.iloc[:,:3],acc_df[AccessOptions].sum(axis=1, skipna=True), dest_df[DestinationOptions].sum(axis=1, skipna=True)], axis=1)
ScTotals.columns = ['AreaCD','AreaNM','Year','Access_rate','Destination_rate']
ScTotals['Care_rate'] = dest_df[CareVs].sum(axis=1, skipna=True)
ScTotals['NoCare_rate'] = dest_df[NoCareVs].sum(axis=1, skipna=True)
ScTotals['STCare_rate'] = dest_df[STCareVs].sum(axis=1, skipna=True)
ScTotals['LTCare_rate'] = dest_df[LTCareVs].sum(axis=1, skipna=True)
ScTotals['AC_Disparity'] = ScTotals['Care_rate'] - ScTotals['Access_rate']

# Take the mean across time within each region
ScTotals_by_region = ScTotals.groupby(['AreaCD','AreaNM']).mean().reset_index().drop('Year', axis=1)

# Load geoJSON file from ONS
with open(os.path.join(path, 'Counties_and_Unitary_Authorities_2015.geojson')) as fp:
    GeoData = json.load(fp)
    
# Plot social care data as map
def ukPlot(dataset, variable, label):
    fig = px.choropleth_mapbox(dataset, locations="AreaNM", featureidkey="properties.ctyua15nm", geojson=GeoData, 
                               color=variable, hover_name="AreaNM", mapbox_style="carto-positron", zoom=4, 
                               center = {"lat": 55, "lon": 0}, labels={variable:label})
    return fig

disparity_map = ukPlot(ScTotals_by_region,'AC_Disparity','Disparity (%)')
plot(disparity_map)