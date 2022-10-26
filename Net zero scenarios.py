# -*- coding: utf-8 -*-
"""
Created on Mon Jun 27 09:15:23 2022

@author: dafnomilii
"""
import numpy as np
import pyam
import matplotlib.pyplot as plt
import matplotlib.transforms as mtransforms
from matplotlib.colors import ListedColormap
from matplotlib.ticker import MaxNLocator
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


#GWP constants (100y, IPCC AR4)
gwp_ch4 = 25
gwp_hfc = 1430
gwp_n2o = 298
gwp_pfc = 7390
gwp_sf6 = 22800

#Import data (RT results)
df_nz = pyam.IamDataFrame(data='NZ_All results.csv')

#Transformation of units to be used later
df_nz.divide("Emissions|Kyoto Gases", 1000, "Emissions|Kyoto Gases [Gt]",ignore_units=True,append=True)
df_nz.divide("Emissions|CO2", 1000, "Emissions|CO\u2082 [Gt]",ignore_units=True,append=True)
df_nz.divide("Emissions|CO2|AFOLU", 1000, "Emissions|CO2|AFOLU [Gt]",ignore_units=True,append=True)
df_nz.divide("Emissions|CO2|Energy|Demand|Industry", 1000, "Emissions|CO2|Energy|Demand|Industry [Gt]",ignore_units=True,append=True)
df_nz.divide("Emissions|CO2|Energy|Demand|Transportation", 1000, "Emissions|CO2|Energy|Demand|Transportation [Gt]",ignore_units=True,append=True)
df_nz.divide("Emissions|CO2|Energy|Demand|Residential and Commercial", 1000, "Emissions|CO2|Energy|Demand|Residential and Commercial [Gt]",ignore_units=True,append=True)
df_nz.divide("Emissions|CO2|Energy|Supply|Electricity", 1000, "Emissions|CO2|Energy|Supply|Electricity [Gt]",ignore_units=True,append=True)
df_nz.divide("Emissions|CO2|Energy and Industrial Processes", 1000, "Emissions|CO2|Energy and Industrial Processes [Gt]",ignore_units=True,append=True)

df_nz.subtract("Emissions|Kyoto Gases", "Emissions|CO2", "Emissions|non-CO\u2082",ignore_units=True,append=True)
df_nz.subtract("Emissions|Kyoto Gases [Gt]", "Emissions|CO\u2082 [Gt]", "Emissions|non-CO\u2082 [Gt]",ignore_units=True,append=True)

#Agreggate variables for new regions
df_nz.aggregate_region(df_nz.variable, region='EU', subregions=('WEU','CEU'), components=False, method='sum', weight=None, append=True, drop_negative_weights=True)
df_nz.aggregate_region(df_nz.variable, region='OECD', subregions=('OCE','WEU','CEU','CAN','JAP','KOR','MEX','TUR','USA'), components=False, method='sum', weight=None, append=True, drop_negative_weights=True)
df_nz.aggregate_region(df_nz.variable, region='non-OECD_target', subregions=('BRA','CHN','INDIA','INDO','RUS','SAF','SEAS','STAN','UKR','WAF'), components=False, method='sum', weight=None, append=True, drop_negative_weights=True)
df_nz.aggregate_region(df_nz.variable, region='non-OECD_nontarget', subregions=('EAF','ME','NAF','RCAM','RSAF','RSAM','RSAS'), components=False, method='sum', weight=None, append=True, drop_negative_weights=True)

#Rename variables for ease of use
df_nz.rename(variable={'Emissions|CO2|AFOLU [Gt]': 'CO\u2082|AFOLU', 'Emissions|CO2|Energy|Demand|Industry [Gt]': 'CO\u2082|Industry', 'Emissions|CO2|Energy|Demand|Transportation [Gt]': 'CO\u2082|Transport',
                       'Emissions|CO2|Energy|Demand|Residential and Commercial [Gt]': 'CO\u2082|Buildings',  'Emissions|CO2|Energy|Supply|Electricity [Gt]': 'CO\u2082|Electricity',
                       'Emissions|CO2|Energy and Industrial Processes [Gt]': 'CO\u2082|Energy and Industry', 'Emissions|non-CO\u2082 [Gt]': 'non-CO\u2082'}, inplace=True)

#Declare sectoral emission variables
var_sectors=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")

#Calculate substituted primary energy variables
df_nz.divide("Primary Energy|Nuclear", 0.4 , "Primary Energy|Nuclear [sub]",ignore_units=True,append=True)
df_nz.divide("Primary Energy|Non-Biomass Renewables|Hydro", 0.4 , "Primary Energy|Non-Biomass Renewables|Hydro [sub]",ignore_units=True,append=True)
df_nz.divide("Primary Energy|Non-Biomass Renewables|Solar", 0.4 , "Primary Energy|Non-Biomass Renewables|Solar [sub]",ignore_units=True,append=True)
df_nz.divide("Primary Energy|Non-Biomass Renewables|Wind", 0.4 , "Primary Energy|Non-Biomass Renewables|Wind [sub]",ignore_units=True,append=True)
df_nz.divide("Primary Energy|Other", 0.4 , "Primary Energy|Other [sub]",ignore_units=True,append=True)
df_nz.rename(variable={"Primary Energy|Coal|w/ CCS":"CoalCCS", "Primary Energy|Coal|w/o CCS":"Coal", "Primary Energy|Oil|w/ CCS":'OilCCS',"Primary Energy|Oil|w/o CCS":'Oil',
                                      "Primary Energy|Gas|w/ CCS":'GasCCS', "Primary Energy|Gas|w/o CCS":'Gas',"Primary Energy|Nuclear [sub]":'Nuclear',"Primary Energy|Non-Biomass Renewables|Hydro [sub]":'Hydro',
                                      "Primary Energy|Non-Biomass Renewables|Solar [sub]":'Solar', "Primary Energy|Non-Biomass Renewables|Wind [sub]":'Wind', "Primary Energy|Biomass|Modern":'Mod.Bio',
                                      "Primary Energy|Biomass|Traditional":'Trad.Bio',"Primary Energy|Biomass|Electricity|w/ CCS":'Mod.BECCS',"Primary Energy|Other [sub]":'Other'}, inplace=True)

#Declare primary energy variables an colormap
var_primary=("CoalCCS", "Coal", "GasCCS", "Gas","Oil","OilCCS","Nuclear","Hydro", "Solar", "Wind", "Mod.Bio", "Trad.Bio","Mod.BECCS","Other")
cmp = ListedColormap(['black', 'gray','lightskyblue','powderblue','darkblue','lawngreen','seagreen','pink','sienna','sandybrown','red','gold','darkgreen', 'darkkhaki'])

'''
Global GHG & mean temp increase for all scenarios 
'''
fig, axs = plt.subplot_mosaic([['a','a','a','b','b']], constrained_layout=True, figsize=(24,20),sharey=False)
for label, ax in axs.items():
    trans = mtransforms.ScaledTranslation(5/72, -5/72, fig.dpi_scale_trans)
    ax.text(0.0, 1.0, label, transform=ax.transAxes + trans,
            fontsize=22, weight="bold", verticalalignment='top',
            bbox=dict(facecolor='none', edgecolor='none', pad=3.0))
df_nz.filter(variable='Emissions|Kyoto Gases [Gt]', region="World").plot(ax=axs['a'],color='scenario',title=(''),legend=False,linewidth=4)
axs['a'].set_xlabel("")
axs['a'].set_ylabel('Gt CO\u2082eq $\mathregular{yr^{-1}}$',fontsize=30)
axs['a'].yaxis.get_label().set_fontsize(30)
axs['a'].yaxis.labelpad = -4
axs['a'].xaxis.set_tick_params(labelsize=26)
axs['a'].yaxis.set_tick_params(labelsize=26)
handles, labels = axs['a'].get_legend_handles_labels()
by_label = dict(zip(labels, handles))
order = [1,2,3,4,5,6,0]
axs['a'].legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc='lower left', bbox_to_anchor=(0, 0), 
                prop=dict(size=38), framealpha=1, edgecolor="none",frameon=True)
axs['a'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['a'].spines['right'].set_visible(False)
axs['a'].spines['top'].set_visible(False)
axs['a'].spines['left'].set_visible(False)
axs['a'].yaxis.set_tick_params(length=0)
axs['a'].yaxis.grid(True)
axs['a'].set_ylim((-10,70))
df_nz.filter(variable='Temperature|Global Mean', region='World').plot(ax=axs['b'],color='scenario',title=(''),legend=False,linewidth=4)
axs['b'].set_ylabel("$^{o}$C", fontsize=30)
axs['b'].set_xlabel("")
axs['b'].yaxis.get_label().set_fontsize(30)
axs['b'].yaxis.labelpad = -1
axs['b'].xaxis.set_tick_params(labelsize=26)
axs['b'].yaxis.set_tick_params(labelsize=26)
axs['b'].spines['right'].set_visible(False)
axs['b'].spines['top'].set_visible(False)
axs['b'].spines['left'].set_visible(False)
axs['b'].yaxis.set_tick_params(length=0)
axs['b'].yaxis.grid(True)

'''
#GHG continuous emissions
'''
fig, axs = plt.subplot_mosaic([['a','b','c'],['d','e','f'],['g','h','i']], constrained_layout=True, figsize=(24,20),sharey=False)
for label, ax in axs.items():
    trans = mtransforms.ScaledTranslation(5/72, -5/72, fig.dpi_scale_trans)
    ax.text(0.0, 1.0, label, transform=ax.transAxes + trans,
            fontsize=22, weight="bold", verticalalignment='top',
            bbox=dict(facecolor='none', edgecolor='none', pad=3.0))
cmp2 = "Set2"
df_nz.filter(scenario="CurPol", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100],variable=var_sectors, region='OECD',keep=True).plot.stack(ax=axs['a'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['a'].set_title('CurPol', fontsize=26)
axs['a'].set_ylabel('Gt CO\u2082eq $\mathregular{yr^{-1}}$', fontsize=22)
axs['a'].set_xlabel('') 
axs['a'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['a'].yaxis.grid(False)
axs['a'].xaxis.set_tick_params(labelsize=22)
axs['a'].yaxis.set_tick_params(labelsize=22)
axs['a'].yaxis.labelpad = -5
axs['a'].set_ylim((-6,15))
axs['a'].yaxis.set_major_locator(MaxNLocator(integer=True))
df_nz.filter(scenario="NZ", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_sectors, region='OECD',keep=True).plot.stack(ax=axs['b'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['b'].set_title('NZ', fontsize=26)
axs['b'].set_ylabel('', fontsize=16)
axs['b'].set_xlabel('') 
axs['b'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['b'].xaxis.set_tick_params(labelsize=22)
axs['b'].set_ylim((-6,15))
axs['b'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['b'].set_yticklabels([])
df_nz.filter(scenario="NZ-St", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100],variable=var_sectors, region='OECD',keep=True).plot.stack(ax=axs['c'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['c'].set_title('NZ-St', fontsize=26)
axs['c'].set_ylabel('', fontsize=20)
axs['c'].set_xlabel('') 
axs['c'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['c'].yaxis.grid(False)
axs['c'].xaxis.set_tick_params(labelsize=22)
axs['c'].set_ylabel("OECD", fontsize=24,rotation=270)
axs['c'].yaxis.set_label_position("right")
axs['c'].yaxis.labelpad = 22
axs['c'].set_ylim((-6,15))
axs['c'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['c'].set_yticklabels([])
df_nz.filter(scenario="CurPol", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_sectors, region='non-OECD_target',keep=True).plot.stack(ax=axs['d'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['d'].set_title('', fontsize=16)
axs['d'].set_ylabel('Gt CO\u2082eq $\mathregular{yr^{-1}}$', fontsize=22)
axs['d'].set_xlabel('') 
axs['d'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['d'].xaxis.set_tick_params(labelsize=22)
axs['d'].yaxis.set_tick_params(labelsize=22)
axs['d'].set_ylim((-7,35))
df_nz.filter(scenario="NZ", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_sectors, region='non-OECD_target',keep=True).plot.stack(ax=axs['e'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['e'].set_title('', fontsize=16)
axs['e'].set_ylabel('', fontsize=16)
axs['e'].set_xlabel('') 
axs['e'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['e'].xaxis.set_tick_params(labelsize=22)
axs['e'].set_ylim((-7,35))
axs['e'].set_yticklabels([])
df_nz.filter(scenario="NZ-St", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_sectors, region='non-OECD_target',keep=True).plot.stack(ax=axs['f'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['f'].set_title('', fontsize=16)
axs['f'].set_ylabel('', fontsize=16)
axs['f'].set_xlabel('') 
axs['f'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['f'].xaxis.set_tick_params(labelsize=22)
axs['f'].set_ylim((-7,35))
axs['f'].set_yticklabels([])
axs['f'].set_ylabel("non-OECD with net-zero target", fontsize=24,rotation=270)
axs['f'].yaxis.set_label_position("right")
axs['f'].yaxis.labelpad = 22
df_nz.filter(scenario="CurPol", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_sectors, region='non-OECD_nontarget',keep=True).plot.stack(ax=axs['g'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['g'].set_title('', fontsize=16)
axs['g'].set_ylabel('Gt CO\u2082eq $\mathregular{yr^{-1}}$', fontsize=22)
axs['g'].set_xlabel('') 
axs['g'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['g'].xaxis.set_tick_params(labelsize=22)
axs['g'].yaxis.set_tick_params(labelsize=22)
axs['g'].set_ylim((-7,25))
df_nz.filter(scenario="NZ", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_sectors, region='non-OECD_nontarget',keep=True).plot.stack(ax=axs['h'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=False,cmap=cmp2)
axs['h'].set_title('', fontsize=16)
axs['h'].set_ylabel('', fontsize=20)
axs['h'].set_xlabel('') 
axs['h'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['h'].xaxis.set_tick_params(labelsize=22)
axs['h'].set_ylim((-7,25))
axs['h'].set_yticklabels([])
df_nz.filter(scenario="NZ-St", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_sectors, region='non-OECD_nontarget',keep=True).plot.stack(ax=axs['i'],total={"color": "black", "ls": "--", "lw": 1.0}, legend=True,cmap=cmp2)
custom_legend = [Line2D([0], [0], color='black', linestyle='--',label='Total'),
                Patch(facecolor=([102/256, 194/256, 165/256]), edgecolor=([102/256, 194/256, 165/256]),label='CO\u2082|AFOLU'),
                Patch(facecolor=([252/256, 141/256, 98/256]), edgecolor=([252/256, 141/256, 98/256]),label='CO\u2082|Buildings'),
                Patch(facecolor=([231/256, 138/256, 195/256]), edgecolor=([231/256, 138/256, 195/256]),label='CO\u2082|Electricity'),
                Patch(facecolor=([166/256, 216/256, 84/256]), edgecolor=([166/256, 216/256, 84/256]),label='CO\u2082|Industry'),
                Patch(facecolor=([229/256, 196/256, 148/256]), edgecolor=([229/256, 196/256, 148/256]),label='CO\u2082|Transport'),
                Patch(facecolor=([179/256, 179/256, 179/256]), edgecolor=([179/256, 179/256, 179/256]),label='non-CO\u2082')]
axs['i'].legend(handles=custom_legend, loc='upper right',bbox_to_anchor=(1, 1),prop=dict(size=24),framealpha=0,ncol=1) 
axs['i'].set_title('', fontsize=16)
axs['i'].set_ylabel('', fontsize=16)
axs['i'].set_xlabel('') 
axs['i'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['i'].xaxis.set_tick_params(labelsize=22)
axs['i'].set_ylim((-7,25))
axs['i'].set_yticklabels([])
axs['i'].set_ylabel("non-OECD without net-zero target", fontsize=24,rotation=270)
axs['i'].yaxis.set_label_position("right")
axs['i'].yaxis.labelpad = 22

'''
#Primary Energy
'''
fig, axs = plt.subplot_mosaic([['a', 'b','c'], ['d', 'e','f'], ['g','h','i']], constrained_layout=True, figsize=(24,20))
for label, ax in axs.items():
    trans = mtransforms.ScaledTranslation(5/72, -5/72, fig.dpi_scale_trans)
    ax.text(0.0, 1.0, label, transform=ax.transAxes + trans,
            fontsize=22, weight = 'bold', verticalalignment='top',
            bbox=dict(facecolor='none', edgecolor='none', pad=3.0))
df_nz.filter(scenario="CurPol", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100],variable=var_primary, region='OECD',keep=True).plot.stack(ax=axs['a'], legend=False,cmap=cmp)
axs['a'].set_title('CurPol', fontsize=24)
axs['a'].set_ylabel('EJ $\mathregular{yr^{-1}}$', fontsize=20)
axs['a'].set_xlabel('') 
axs['a'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['a'].yaxis.grid(False)
axs['a'].xaxis.set_tick_params(labelsize=20)
axs['a'].yaxis.set_tick_params(labelsize=20)
axs['a'].set_ylim((-10,700))
df_nz.filter(scenario="NZ", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_primary, region='OECD',keep=True).plot.stack(ax=axs['b'], legend=False,cmap=cmp)
axs['b'].set_title('NZ', fontsize=24)
axs['b'].set_ylabel('', fontsize=16)
axs['b'].set_xlabel('') 
axs['b'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['b'].xaxis.set_tick_params(labelsize=22)
axs['b'].set_ylim((-10,700))
axs['b'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['b'].set_yticklabels([])
df_nz.filter(scenario="NZ-St", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100],variable=var_primary, region='OECD',keep=True).plot.stack(ax=axs['c'], legend=False,cmap=cmp)
axs['c'].set_title('NZ-St', fontsize=24)
axs['c'].set_ylabel('', fontsize=20)
axs['c'].set_xlabel('') 
axs['c'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['c'].yaxis.grid(False)
axs['c'].xaxis.set_tick_params(labelsize=22)
axs['c'].set_ylabel("OECD", fontsize=24,rotation=270)
axs['c'].yaxis.set_label_position("right")
axs['c'].yaxis.labelpad = 22
axs['c'].set_ylim((-10,700))
axs['c'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['c'].set_yticklabels([])
df_nz.filter(scenario="CurPol", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_primary, region='non-OECD_target',keep=True).plot.stack(ax=axs['d'], legend=False,cmap=cmp)
axs['d'].set_title('', fontsize=16)
axs['d'].set_ylabel('EJ $\mathregular{yr^{-1}}$', fontsize=24)
axs['d'].set_xlabel('') 
axs['d'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['d'].xaxis.set_tick_params(labelsize=22)
axs['d'].yaxis.set_tick_params(labelsize=22)
axs['d'].set_ylim((-10,700))
df_nz.filter(scenario="NZ", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_primary, region='non-OECD_target',keep=True).plot.stack(ax=axs['e'], legend=False,cmap=cmp)
axs['e'].set_title('', fontsize=16)
axs['e'].set_ylabel('', fontsize=16)
axs['e'].set_xlabel('') 
axs['e'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['e'].xaxis.set_tick_params(labelsize=22)
axs['e'].set_ylim((-10,700))
axs['e'].set_yticklabels([])
df_nz.filter(scenario="NZ-St", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_primary, region='non-OECD_target',keep=True).plot.stack(ax=axs['f'],legend=False,cmap=cmp)
axs['f'].set_title('', fontsize=16)
axs['f'].set_ylabel('', fontsize=16)
axs['f'].set_xlabel('') 
axs['f'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['f'].xaxis.set_tick_params(labelsize=22)
axs['f'].set_ylim((-10,700))
axs['f'].set_yticklabels([])
axs['f'].set_ylabel("non-OECD with net-zero target", fontsize=24,rotation=270)
axs['f'].yaxis.set_label_position("right")
axs['f'].yaxis.labelpad = 22
df_nz.filter(scenario="CurPol", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_primary, region='non-OECD_nontarget',keep=True).plot.stack(ax=axs['g'], legend=False,cmap=cmp)
axs['g'].set_title('', fontsize=16)
axs['g'].set_ylabel('EJ $\mathregular{yr^{-1}}$', fontsize=24)
axs['g'].set_xlabel('') 
axs['g'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['g'].xaxis.set_tick_params(labelsize=22)
axs['g'].yaxis.set_tick_params(labelsize=22)
axs['g'].set_ylim((-10,700))
df_nz.filter(scenario="NZ", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_primary, region='non-OECD_nontarget',keep=True).plot.stack(ax=axs['h'], legend=False,cmap=cmp)
axs['h'].set_title('', fontsize=16)
axs['h'].set_ylabel('', fontsize=20)
axs['h'].set_xlabel('') 
axs['h'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['h'].xaxis.set_tick_params(labelsize=22)
axs['h'].set_ylim((-10,700))
axs['h'].set_yticklabels([])
df_nz.filter(scenario="NZ-St", year=[2015,2020,2025,2030,2035,2040,2045,2050,2055,2060,2065,2070,2075,2080,2085,2090,2095,2100], variable=var_primary, region='non-OECD_nontarget',keep=True).plot.stack(ax=axs['i'], legend=True,cmap=cmp)
handles, labels = axs['i'].get_legend_handles_labels()
by_label = dict(zip(labels, handles))
order = [0,1,2,3,4,5,6,7,8,9,10,11,12,13]
axs['i'].legend([handles[idx] for idx in order],[labels[idx] for idx in order], loc='lower right', bbox_to_anchor=(1.52, -0.05), prop=dict(size=20.5), framealpha=0, ncol=1)
axs['i'].set_title('', fontsize=16)
axs['i'].set_ylabel('', fontsize=16)
axs['i'].set_xlabel('') 
axs['i'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['i'].xaxis.set_tick_params(labelsize=22)
axs['i'].yaxis.set_tick_params(labelsize=22)
axs['i'].set_ylabel("non-OECD without net-zero target", fontsize=24,rotation=270)
axs['i'].yaxis.set_label_position("right")
axs['i'].yaxis.labelpad = 22
axs['i'].set_ylim((-10,700))
axs['i'].set_yticklabels([])

'''
Sectoral GHG graph
'''
df_wf=df_nz.filter(region=('World','OECD','non-OECD_target','non-OECD_nontarget'), scenario=('CurPol','NDC','NZ','NZ-Al','NZ-Br','NZ-St','1.5C'),year=[2050,2050],variable=('CO\u2082|AFOLU','CO\u2082|Industry','CO\u2082|Transport','CO\u2082|Buildings', 'CO\u2082|Electricity', 'non-CO\u2082'))
df_wf.subtract("NZ","CurPol", "diffNDCNZCP",axis="scenario",ignore_units=True,append=True)
df_wf.subtract("NZ-Al","NZ", "diffNZNDCNZ",axis="scenario",ignore_units=True,append=True)
df_wf.subtract("NZ-Br","NZ-Al", "diffNZINCNZ",axis="scenario",ignore_units=True,append=True)
df_wf.subtract("NDC","CurPol", "diffNDCCP",axis="scenario",ignore_units=True,append=True)
df_wf.subtract("NZ","NDC", "diffNDCNZ",axis="scenario",ignore_units=True,append=True)
TE_vars=["CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport","CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082"]
df_wf.aggregate("TE",components=TE_vars,append=True)

fig, axs = plt.subplot_mosaic([['a'], ['b'],['c']], constrained_layout=True, figsize=(24,20))
for label, ax in axs.items():
    trans = mtransforms.ScaledTranslation(5/72, -5/72, fig.dpi_scale_trans)
    ax.text(0.0, 1.0, label, transform=ax.transAxes + trans,
            fontsize=22, weight = 'bold', verticalalignment='top',
            bbox=dict(facecolor='none', edgecolor='none', pad=3.0))
    
cmp_wf = "Set2"
ind = np.arange(start=0, stop=55, step=1.31)

args_CurPol_2050 = dict(scenario=("CurPol"), year=[2050])
args_CurPol_2050= df_nz.filter(**args_CurPol_2050, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="OECD", keep=True)
args_CurPol_2050.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[41], width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=cmp_wf,legend=False)

args_CurPol_base=dict(scenario=("CurPol"), year=[2050])
data_CurPol_base=df_wf.filter(**args_CurPol_base, variable="TE").filter(region="OECD", keep=True)
axs['a'].axhline(y=data_CurPol_base.data.value[0], xmin=0.02, xmax=0.18,color='black', linestyle='--', linewidth=1, zorder=3)

args2 = dict(scenario=("diffNDCCP"), year=[2050])
data2 = df_wf.filter(**args2, variable=("non-CO\u2082")).filter(region="OECD", keep=True)
data2.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),  hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args3 = dict(scenario=("diffNDCCP"), year=[2050])
data3 = df_wf.filter(**args3, variable=("CO\u2082|Transport")).filter(region="OECD", keep=True)
data3.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args4 = dict(scenario=("diffNDCCP"), year=[2050])
data4 = df_wf.filter(**args4, variable=("CO\u2082|Industry")).filter(region="OECD", keep=True)
data4.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args5 = dict(scenario=("diffNDCCP"), year=[2050])
data5 = df_wf.filter(**args5, variable=("CO\u2082|Electricity")).filter(region="OECD", keep=True)
data5.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args6 = dict(scenario=("diffNDCCP"), year=[2050])
data6 = df_wf.filter(**args6, variable=("CO\u2082|Buildings")).filter(region="OECD", keep=True)
data6.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0]+data5.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args7 = dict(scenario=("diffNDCCP"), year=[2050])
data7 = df_wf.filter(**args7, variable=("CO\u2082|AFOLU")).filter(region="OECD", keep=True)
data7.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0]+data5.data.value[0]+data6.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args8 = dict(scenario=("NDC"), year=[2050])
dataNDC = df_nz.filter(**args8, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="OECD", keep=True)
dataNDC.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True, position=ind[38],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NDC_base=dict(scenario=("NDC"), year=[2050])
data_NDC_base=df_wf.filter(**args_NDC_base, variable="TE").filter(region="OECD", keep=True)
axs['a'].axhline(y=data_NDC_base.data.value[0], xmin=0.19, xmax=0.36,color='black', linestyle='--', linewidth=1, zorder=3)

args9 = dict(scenario=("diffNDCNZ"), year=[2050])
data9 = df_wf.filter(**args9, variable=("non-CO\u2082")).filter(region="OECD", keep=True)
data9.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),  hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args10 = dict(scenario=("diffNDCNZ"), year=[2050])
data10 = df_wf.filter(**args10, variable=("CO\u2082|Transport")).filter(region="OECD", keep=True)
data10.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args11 = dict(scenario=("diffNDCNZ"), year=[2050])
data11 = df_wf.filter(**args11, variable=("CO\u2082|Industry")).filter(region="OECD", keep=True)
data11.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args12 = dict(scenario=("diffNDCNZ"), year=[2050])
data12 = df_wf.filter(**args12, variable=("CO\u2082|Electricity")).filter(region="OECD", keep=True)
data12.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0]+data11.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args13 = dict(scenario=("diffNDCNZ"), year=[2050])
data13 = df_wf.filter(**args13, variable=("CO\u2082|Buildings")).filter(region="OECD", keep=True)
data13.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0]+data11.data.value[0]+data12.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args14 = dict(scenario=("diffNDCNZ"), year=[2050])
data14 = df_wf.filter(**args14, variable=("CO\u2082|AFOLU")).filter(region="OECD", keep=True)
data14.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0]+data11.data.value[0]+data12.data.value[0]+data13.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args15 = dict(scenario=("NZ"), year=[2050])
dataNDCNZ = df_nz.filter(**args15, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="OECD", keep=True)
dataNDCNZ.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True, position=ind[35],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NDCNZ_base=dict(scenario=("NZ"), year=[2050])
data_NDCNZ_base=df_wf.filter(**args_NDCNZ_base, variable="TE").filter(region="OECD", keep=True)
axs['a'].axhline(y=data_NDCNZ_base.data.value[0], xmin=0.37, xmax=0.54,color='black', linestyle='--', linewidth=1, zorder=3)

args16 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data16 = df_wf.filter(**args16, variable=("non-CO\u2082")).filter(region="OECD", keep=True)
data16.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args17 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data17 = df_wf.filter(**args17, variable=("CO\u2082|Transport")).filter(region="OECD", keep=True)
data17.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args18 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data18 = df_wf.filter(**args18, variable=("CO\u2082|Industry")).filter(region="OECD", keep=True)
data18.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args19 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data19 = df_wf.filter(**args19, variable=("CO\u2082|Electricity")).filter(region="OECD", keep=True)
data19.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data17.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args20 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data20 = df_wf.filter(**args20, variable=("CO\u2082|Buildings")).filter(region="OECD", keep=True)
data20.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data18.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args21 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data21 = df_wf.filter(**args21, variable=("CO\u2082|AFOLU")).filter(region="OECD", keep=True)
data21.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data18.data.value[0]+data20.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args22 = dict(scenario=("NZ-Al"), year=[2050])
dataNZ = df_nz.filter(**args22, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="OECD", keep=True)
dataNZ.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True, position=ind[32],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZ_base=dict(scenario=("NZ-Al"), year=[2050])
data_NZ_base=df_wf.filter(**args_NZ_base, variable="TE").filter(region="OECD", keep=True)
axs['a'].axhline(y=data_NZ_base.data.value[0], xmin=0.55, xmax=0.72,color='black', linestyle='--', linewidth=1, zorder=3)

args23 = dict(scenario=("diffNZINCNZ"), year=[2050])
data23 = df_wf.filter(**args23, variable=("non-CO\u2082")).filter(region="OECD", keep=True)
data23.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args24 = dict(scenario=("diffNZINCNZ"), year=[2050])
data24 = df_wf.filter(**args24, variable=("CO\u2082|Transport")).filter(region="OECD", keep=True)
data24.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args25 = dict(scenario=("diffNZINCNZ"), year=[2050])
data25 = df_wf.filter(**args25, variable=("CO\u2082|Industry")).filter(region="OECD", keep=True)
data25.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args26 = dict(scenario=("diffNZINCNZ"), year=[2050])
data26 = df_wf.filter(**args26, variable=("CO\u2082|Electricity")).filter(region="OECD", keep=True)
data26.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args27 = dict(scenario=("diffNZINCNZ"), year=[2050])
data27 = df_wf.filter(**args27, variable=("CO\u2082|Buildings")).filter(region="OECD", keep=True)
data27.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0]+data26.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args28 = dict(scenario=("diffNZINCNZ"), year=[2050])
data28 = df_wf.filter(**args28, variable=("CO\u2082|AFOLU")).filter(region="OECD", keep=True)
data28.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0]+data26.data.value[0]+data27.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args29 = dict(scenario=("NZ-Br"), year=[2050])
dataNZINC = df_nz.filter(**args29, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="OECD", keep=True)
dataNZINC.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True, position=ind[29],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZINC_base=dict(scenario=("NZ-Br"), year=[2050])
data_NZINC_base=df_wf.filter(**args_NZINC_base, variable="TE").filter(region="OECD", keep=True)
axs['a'].axhline(y=data_NZINC_base.data.value[0], xmin=0.73, xmax=0.9,color='black', linestyle='--', linewidth=1, zorder=3)

args30 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data30 = df_wf.filter(**args30, variable=("non-CO\u2082")).filter(region="OECD", keep=True)
data30.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]), hatch='//',width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args31 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data31 = df_wf.filter(**args31, variable=("CO\u2082|Transport")).filter(region="OECD", keep=True)
data31.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args32 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data32 = df_wf.filter(**args32, variable=("CO\u2082|Industry")).filter(region="OECD", keep=True)
data32.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args33 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data33 = df_wf.filter(**args33, variable=("CO\u2082|Electricity")).filter(region="OECD", keep=True)
data33.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args34 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data34 = df_wf.filter(**args34, variable=("CO\u2082|Buildings")).filter(region="OECD", keep=True)
data34.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args35 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data35 = df_wf.filter(**args35, variable=("CO\u2082|AFOLU")).filter(region="OECD", keep=True)
data35.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0]+data34.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args36 = dict(scenario=("NZ-St"), year=[2050])
dataNZstr = df_nz.filter(**args36, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="OECD", keep=True)
dataNZstr.plot.bar(ax=axs['a'],bars="variable", x="year", stacked=True, position=ind[26],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZStr_base=dict(scenario=("NZ-St"), year=[2050])
data_NZStr_base=df_wf.filter(**args_NZStr_base, variable="TE").filter(region="OECD", keep=True)
axs['a'].axhline(y=data_NZStr_base.data.value[0], xmin=0.91, xmax=0.985,color='black', linestyle='--', linewidth=1, zorder=3)
axs['a'].set_xlim((-2.73,-1.62))
axs['a'].set_ylim((-5,15))
axs['a'].set_title('OECD', fontsize=24)
axs['a'].set_ylabel('Gt CO\u2082eq $\mathregular{yr^{-1}}$', fontsize=24)
axs['a'].set_xlabel('') 
axs['a'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['a'].xaxis.set_tick_params(labelsize=22)
axs['a'].yaxis.set_tick_params(labelsize=22)
axs['a'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['a'].set_facecolor('gainsboro')

#non-OECD_target
args_CurPol_2050 = dict(scenario=("CurPol"), year=[2050])
args_CurPol_2050= df_nz.filter(**args_CurPol_2050, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_target", keep=True)
args_CurPol_2050.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[41], width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=cmp_wf,legend=False)

args_CurPol_base=dict(scenario=("CurPol"), year=[2050])
data_CurPol_base=df_wf.filter(**args_CurPol_base, variable="TE").filter(region="non-OECD_target", keep=True)
axs['b'].axhline(y=data_CurPol_base.data.value[0], xmin=0.02, xmax=0.18,color='black', linestyle='--', linewidth=1, zorder=3)

args2 = dict(scenario=("diffNDCCP"), year=[2050])
data2 = df_wf.filter(**args2, variable=("non-CO\u2082")).filter(region="non-OECD_target", keep=True)
data2.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),  hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args3 = dict(scenario=("diffNDCCP"), year=[2050])
data3 = df_wf.filter(**args3, variable=("CO\u2082|Transport")).filter(region="non-OECD_target", keep=True)
data3.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args4 = dict(scenario=("diffNDCCP"), year=[2050])
data4 = df_wf.filter(**args4, variable=("CO\u2082|Industry")).filter(region="non-OECD_target", keep=True)
data4.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args5 = dict(scenario=("diffNDCCP"), year=[2050])
data5 = df_wf.filter(**args5, variable=("CO\u2082|Electricity")).filter(region="non-OECD_target", keep=True)
data5.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args6 = dict(scenario=("diffNDCCP"), year=[2050])
data6 = df_wf.filter(**args6, variable=("CO\u2082|Buildings")).filter(region="non-OECD_target", keep=True)
data6.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0]+data5.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args7 = dict(scenario=("diffNDCCP"), year=[2050])
data7 = df_wf.filter(**args7, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_target", keep=True)
data7.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args8 = dict(scenario=("NDC"), year=[2050])
dataNDC = df_nz.filter(**args8, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_target", keep=True)
dataNDC.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True, position=ind[38],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NDC_base=dict(scenario=("NDC"), year=[2050])
data_NDC_base=df_wf.filter(**args_NDC_base, variable="TE").filter(region="non-OECD_target", keep=True)
axs['b'].axhline(y=data_NDC_base.data.value[0], xmin=0.19, xmax=0.36,color='black', linestyle='--', linewidth=1, zorder=3)

args9 = dict(scenario=("diffNDCNZ"), year=[2050])
data9 = df_wf.filter(**args9, variable=("non-CO\u2082")).filter(region="non-OECD_target", keep=True)
data9.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),  hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args10 = dict(scenario=("diffNDCNZ"), year=[2050])
data10 = df_wf.filter(**args10, variable=("CO\u2082|Transport")).filter(region="non-OECD_target", keep=True)
data10.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args11 = dict(scenario=("diffNDCNZ"), year=[2050])
data11 = df_wf.filter(**args11, variable=("CO\u2082|Industry")).filter(region="non-OECD_target", keep=True)
data11.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args12 = dict(scenario=("diffNDCNZ"), year=[2050])
data12 = df_wf.filter(**args12, variable=("CO\u2082|Electricity")).filter(region="non-OECD_target", keep=True)
data12.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0]+data11.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args13 = dict(scenario=("diffNDCNZ"), year=[2050])
data13 = df_wf.filter(**args13, variable=("CO\u2082|Buildings")).filter(region="non-OECD_target", keep=True)
data13.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0]+data11.data.value[0]+data12.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args14 = dict(scenario=("diffNDCNZ"), year=[2050])
data14 = df_wf.filter(**args14, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_target", keep=True)
data14.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0]+data10.data.value[0]+data11.data.value[0]+data12.data.value[0]+data13.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args15 = dict(scenario=("NZ"), year=[2050])
dataNDCNZ = df_nz.filter(**args15, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_target", keep=True)
dataNDCNZ.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True, position=ind[35],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NDCNZ_base=dict(scenario=("NZ"), year=[2050])
data_NDCNZ_base=df_wf.filter(**args_NDCNZ_base, variable="TE").filter(region="non-OECD_target", keep=True)
axs['b'].axhline(y=data_NDCNZ_base.data.value[0], xmin=0.37, xmax=0.54,color='black', linestyle='--', linewidth=1, zorder=3)

args16 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data16 = df_wf.filter(**args16, variable=("non-CO\u2082")).filter(region="non-OECD_target", keep=True)
data16.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args17 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data17 = df_wf.filter(**args17, variable=("CO\u2082|Transport")).filter(region="non-OECD_target", keep=True)
data17.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args18 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data18 = df_wf.filter(**args18, variable=("CO\u2082|Industry")).filter(region="non-OECD_target", keep=True)
data18.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args19 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data19 = df_wf.filter(**args19, variable=("CO\u2082|Electricity")).filter(region="non-OECD_target", keep=True)
data19.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0]+data18.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args20 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data20 = df_wf.filter(**args20, variable=("CO\u2082|Buildings")).filter(region="non-OECD_target", keep=True)
data20.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0]+data18.data.value[0]+data19.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args21 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data21 = df_wf.filter(**args21, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_target", keep=True)
data21.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0]+data18.data.value[0]+data19.data.value[0]+data20.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args22 = dict(scenario=("NZ-Al"), year=[2050])
dataNZ = df_nz.filter(**args22, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_target", keep=True)
dataNZ.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True, position=ind[32],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZ_base=dict(scenario=("NZ-Al"), year=[2050])
data_NZ_base=df_wf.filter(**args_NZ_base, variable="TE").filter(region="non-OECD_target", keep=True)
axs['b'].axhline(y=data_NZ_base.data.value[0], xmin=0.55, xmax=0.72,color='black', linestyle='--', linewidth=1, zorder=3)

args23 = dict(scenario=("diffNZINCNZ"), year=[2050])
data23 = df_wf.filter(**args23, variable=("non-CO\u2082")).filter(region="non-OECD_target", keep=True)
data23.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args24 = dict(scenario=("diffNZINCNZ"), year=[2050])
data24 = df_wf.filter(**args24, variable=("CO\u2082|Transport")).filter(region="non-OECD_target", keep=True)
data24.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args25 = dict(scenario=("diffNZINCNZ"), year=[2050])
data25 = df_wf.filter(**args25, variable=("CO\u2082|Industry")).filter(region="non-OECD_target", keep=True)
data25.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args26 = dict(scenario=("diffNZINCNZ"), year=[2050])
data26 = df_wf.filter(**args26, variable=("CO\u2082|Electricity")).filter(region="non-OECD_target", keep=True)
data26.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args27 = dict(scenario=("diffNZINCNZ"), year=[2050])
data27 = df_wf.filter(**args27, variable=("CO\u2082|Buildings")).filter(region="non-OECD_target", keep=True)
data27.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0]+data26.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args28 = dict(scenario=("diffNZINCNZ"), year=[2050])
data28 = df_wf.filter(**args28, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_target", keep=True)
data28.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0]+data26.data.value[0]+data27.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args29 = dict(scenario=("NZ-Br"), year=[2050])
dataNZINC = df_nz.filter(**args29, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_target", keep=True)
dataNZINC.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True, position=ind[29],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZINC_base=dict(scenario=("NZ-Br"), year=[2050])
data_NZINC_base=df_wf.filter(**args_NZINC_base, variable="TE").filter(region="non-OECD_target", keep=True)
axs['b'].axhline(y=data_NZINC_base.data.value[0], xmin=0.73, xmax=0.9,color='black', linestyle='--', linewidth=1, zorder=3)

args30 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data30 = df_wf.filter(**args30, variable=("non-CO\u2082")).filter(region="non-OECD_target", keep=True)
data30.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]), hatch='//',width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args31 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data31 = df_wf.filter(**args31, variable=("CO\u2082|Transport")).filter(region="non-OECD_target", keep=True)
data31.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args32 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data32 = df_wf.filter(**args32, variable=("CO\u2082|Industry")).filter(region="non-OECD_target", keep=True)
data32.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args33 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data33 = df_wf.filter(**args33, variable=("CO\u2082|Electricity")).filter(region="non-OECD_target", keep=True)
data33.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args34 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data34 = df_wf.filter(**args34, variable=("CO\u2082|Buildings")).filter(region="non-OECD_target", keep=True)
data34.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0]+data33.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args35 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data35 = df_wf.filter(**args35, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_target", keep=True)
data35.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0]+data33.data.value[0]+data34.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args36 = dict(scenario=("NZ-St"), year=[2050])
dataNZstr = df_nz.filter(**args36, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_target", keep=True)
dataNZstr.plot.bar(ax=axs['b'],bars="variable", x="year", stacked=True, position=ind[26],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZStr_base=dict(scenario=("NZ-St"), year=[2050])
data_NZStr_base=df_wf.filter(**args_NZStr_base, variable="TE").filter(region="non-OECD_target", keep=True)
axs['b'].axhline(y=data_NZStr_base.data.value[0], xmin=0.91, xmax=0.985,color='black', linestyle='--', linewidth=1, zorder=3)
axs['b'].set_xlim((-2.73,-1.62))
axs['b'].set_ylim((-8,32))
handles, labels = axs['b'].get_legend_handles_labels()
by_label = dict(zip(labels, handles))
axs['b'].set_title('non-OECD with net-zero target', fontsize=24)
axs['b'].set_ylabel('Gt CO\u2082eq $\mathregular{yr^{-1}}$', fontsize=24)
axs['b'].set_xlabel('') 
axs['b'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['b'].xaxis.set_tick_params(labelsize=22)
axs['b'].yaxis.set_tick_params(labelsize=22)
axs['b'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['b'].set_facecolor('gainsboro')

#non-OECD_nontarget
args_CurPol_2050 = dict(scenario=("CurPol"), year=[2050])
args_CurPol_2050= df_nz.filter(**args_CurPol_2050, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
args_CurPol_2050.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[41], width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=cmp_wf,legend=False)

args_CurPol_base=dict(scenario=("CurPol"), year=[2050])
data_CurPol_base=df_wf.filter(**args_CurPol_base, variable="TE").filter(region="non-OECD_nontarget", keep=True)
axs['c'].axhline(y=data_CurPol_base.data.value[0], xmin=0.02, xmax=0.18,color='black', linestyle='--', linewidth=1, zorder=3)

args2 = dict(scenario=("diffNDCCP"), year=[2050])
data2 = df_wf.filter(**args2, variable=("non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
data2.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),  hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args3 = dict(scenario=("diffNDCCP"), year=[2050])
data3 = df_wf.filter(**args3, variable=("CO\u2082|Transport")).filter(region="non-OECD_nontarget", keep=True)
data3.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args4 = dict(scenario=("diffNDCCP"), year=[2050])
data4 = df_wf.filter(**args4, variable=("CO\u2082|Industry")).filter(region="non-OECD_nontarget", keep=True)
data4.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args5 = dict(scenario=("diffNDCCP"), year=[2050])
data5 = df_wf.filter(**args5, variable=("CO\u2082|Electricity")).filter(region="non-OECD_nontarget", keep=True)
data5.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args6 = dict(scenario=("diffNDCCP"), year=[2050])
data6 = df_wf.filter(**args6, variable=("CO\u2082|Buildings")).filter(region="non-OECD_nontarget", keep=True)
data6.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0]+data5.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args7 = dict(scenario=("diffNDCCP"), year=[2050])
data7 = df_wf.filter(**args7, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_nontarget", keep=True)
data7.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[39], bottom=data_CurPol_base.data.value[0]+data2.data.value[0]+data3.data.value[0]+data4.data.value[0]+data5.data.value[0]+data6.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args8 = dict(scenario=("NDC"), year=[2050])
dataNDC = df_nz.filter(**args8, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
dataNDC.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True, position=ind[38],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NDC_base=dict(scenario=("NDC"), year=[2050])
data_NDC_base=df_wf.filter(**args_NDC_base, variable="TE").filter(region="non-OECD_nontarget", keep=True)
axs['c'].axhline(y=data_NDC_base.data.value[0], xmin=0.19, xmax=0.36,color='black', linestyle='--', linewidth=1, zorder=3)

args9 = dict(scenario=("diffNDCNZ"), year=[2050])
data9 = df_wf.filter(**args9, variable=("non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
data9.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),  hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args10 = dict(scenario=("diffNDCNZ"), year=[2050])
data10 = df_wf.filter(**args10, variable=("CO\u2082|Transport")).filter(region="non-OECD_nontarget", keep=True)
data10.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args11 = dict(scenario=("diffNDCNZ"), year=[2050])
data11 = df_wf.filter(**args11, variable=("CO\u2082|Industry")).filter(region="non-OECD_nontarget", keep=True)
data11.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data10.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args12 = dict(scenario=("diffNDCNZ"), year=[2050])
data12 = df_wf.filter(**args12, variable=("CO\u2082|Electricity")).filter(region="non-OECD_nontarget", keep=True)
data12.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data10.data.value[0]+data11.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args13 = dict(scenario=("diffNDCNZ"), year=[2050])
data13 = df_wf.filter(**args13, variable=("CO\u2082|Buildings")).filter(region="non-OECD_nontarget", keep=True)
data13.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data10.data.value[0]+data11.data.value[0]+data12.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args14 = dict(scenario=("diffNDCNZ"), year=[2050])
data14 = df_wf.filter(**args14, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_nontarget", keep=True)
data14.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[36], bottom=data_NDC_base.data.value[0]+data9.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args15 = dict(scenario=("NZ"), year=[2050])
dataNDCNZ = df_nz.filter(**args8, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
dataNDCNZ.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True, position=ind[35],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NDCNZ_base=dict(scenario=("NZ"), year=[2050])
data_NDCNZ_base=df_wf.filter(**args_NDCNZ_base, variable="TE").filter(region="non-OECD_nontarget", keep=True)
axs['c'].axhline(y=data_NDCNZ_base.data.value[0], xmin=0.37, xmax=0.54,color='black', linestyle='--', linewidth=1, zorder=3)

args16 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data16 = df_wf.filter(**args16, variable=("non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
data16.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args17 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data17 = df_wf.filter(**args17, variable=("CO\u2082|Transport")).filter(region="non-OECD_nontarget", keep=True)
data17.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args18 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data18 = df_wf.filter(**args18, variable=("CO\u2082|Industry")).filter(region="non-OECD_nontarget", keep=True)
data18.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args19 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data19 = df_wf.filter(**args12, variable=("CO\u2082|Electricity")).filter(region="non-OECD_nontarget", keep=True)
data19.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0]+data18.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args20 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data20 = df_wf.filter(**args20, variable=("CO\u2082|Buildings")).filter(region="non-OECD_nontarget", keep=True)
data20.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0]+data18.data.value[0]+data19.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args21 = dict(scenario=("diffNZNDCNZ"), year=[2050])
data21 = df_wf.filter(**args21, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_nontarget", keep=True)
data21.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[33], bottom=data_NDCNZ_base.data.value[0]+data16.data.value[0]+data17.data.value[0]+data18.data.value[0]+data19.data.value[0]+data20.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args22 = dict(scenario=("NZ-Al"), year=[2050])
dataNZ = df_nz.filter(**args22, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
dataNZ.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True, position=ind[32],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZ_base=dict(scenario=("NZ-Al"), year=[2050])
data_NZ_base=df_wf.filter(**args_NZ_base, variable="TE").filter(region="non-OECD_nontarget", keep=True)
axs['c'].axhline(y=data_NZ_base.data.value[0], xmin=0.55, xmax=0.72,color='black', linestyle='--', linewidth=1, zorder=3)

args23 = dict(scenario=("diffNZINCNZ"), year=[2050])
data23 = df_wf.filter(**args23, variable=("non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
data23.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]),hatch='//', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args24 = dict(scenario=("diffNZINCNZ"), year=[2050])
data24 = df_wf.filter(**args24, variable=("CO\u2082|Transport")).filter(region="non-OECD_nontarget", keep=True)
data24.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args25 = dict(scenario=("diffNZINCNZ"), year=[2050])
data25 = df_wf.filter(**args25, variable=("CO\u2082|Industry")).filter(region="non-OECD_nontarget", keep=True)
data25.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args26 = dict(scenario=("diffNZINCNZ"), year=[2050])
data26 = df_wf.filter(**args26, variable=("CO\u2082|Electricity")).filter(region="non-OECD_nontarget", keep=True)
data26.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args27 = dict(scenario=("diffNZINCNZ"), year=[2050])
data27 = df_wf.filter(**args27, variable=("CO\u2082|Buildings")).filter(region="non-OECD_nontarget", keep=True)
data27.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0]+data26.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args28 = dict(scenario=("diffNZINCNZ"), year=[2050])
data28 = df_wf.filter(**args28, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_nontarget", keep=True)
data28.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[30], bottom=data_NZ_base.data.value[0]+data23.data.value[0]+data24.data.value[0]+data25.data.value[0]+data26.data.value[0]+data27.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args29 = dict(scenario=("NZ-Br"), year=[2050])
dataNZINC = df_nz.filter(**args29, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
dataNZINC.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True, position=ind[29],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZINC_base=dict(scenario=("NZ-Br"), year=[2050])
data_NZINC_base=df_wf.filter(**args_NZINC_base, variable="TE").filter(region="non-OECD_nontarget", keep=True)
axs['c'].axhline(y=data_NZINC_base.data.value[0], xmin=0.73, xmax=0.9,color='black', linestyle='--', linewidth=1, zorder=3)

args30 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data30 = df_wf.filter(**args30, variable=("non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
data30.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0],
               cmap=ListedColormap([179/256, 179/256, 179/256]), hatch='//',width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args31 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data31 = df_wf.filter(**args31, variable=("CO\u2082|Transport")).filter(region="non-OECD_nontarget", keep=True)
data31.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([229/256, 196/256, 148/256]),hatch='\\',legend=False)

args32 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data32 = df_wf.filter(**args32, variable=("CO\u2082|Industry")).filter(region="non-OECD_nontarget", keep=True)
data32.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0], width=.05,linewidth=0.5,
               edgecolor = "black", zorder=3,cmap=ListedColormap([166/256, 216/256, 84/256]),hatch='//',legend=False)

args33 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data33 = df_wf.filter(**args33, variable=("CO\u2082|Electricity")).filter(region="non-OECD_nontarget", keep=True)
data33.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([231/256, 138/256, 195/256]),hatch='\\',legend=False)

args34 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data34 = df_wf.filter(**args34, variable=("CO\u2082|Buildings")).filter(region="non-OECD_nontarget", keep=True)
data34.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0]+data33.data.value[0], 
               width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap=ListedColormap([252/256, 141/256, 98/256]),hatch='//',legend=False)

args35 = dict(scenario=("diffNZStrNZINC"), year=[2050])
data35 = df_wf.filter(**args35, variable=("CO\u2082|AFOLU")).filter(region="non-OECD_nontarget", keep=True)
data35.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True,position=ind[27], bottom=data_NZINC_base.data.value[0]+data30.data.value[0]+data31.data.value[0]+data32.data.value[0]+data33.data.value[0]+data34.data.value[0],
               cmap=ListedColormap([102/256, 194/256, 165/256]),hatch='\\', width=.05,linewidth=0.5,edgecolor = "black", zorder=3,legend=False)

args36 = dict(scenario=("NZ-St"), year=[2050])
dataNZstr = df_nz.filter(**args36, variable=("CO\u2082|AFOLU", "CO\u2082|Industry", "CO\u2082|Transport",
                                      "CO\u2082|Buildings", "CO\u2082|Electricity", "non-CO\u2082")).filter(region="non-OECD_nontarget", keep=True)
dataNZstr.plot.bar(ax=axs['c'],bars="variable", x="year", stacked=True, position=ind[26],width=.05,linewidth=0.5,edgecolor = "black", zorder=3,cmap = cmp_wf,legend=False)

args_NZStr_base=dict(scenario=("NZ-St"), year=[2050])
data_NZStr_base=df_wf.filter(**args_NZStr_base, variable="TE").filter(region="non-OECD_nontarget", keep=True)
axs['c'].axhline(y=data_NZStr_base.data.value[0], xmin=0.91, xmax=0.985,color='black', linestyle='--', linewidth=1, zorder=3)
axs['c'].set_xlim((-2.73,-1.62))
axs['c'].set_ylim((-5,15))
axs['c'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['c'].set_title('non-OECD without net-zero target', fontsize=24)
axs['c'].set_ylabel('Gt CO\u2082eq $\mathregular{yr^{-1}}$', fontsize=24)
axs['c'].set_xlabel('') 
axs['c'].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
axs['c'].xaxis.set_tick_params(labelsize=22)
axs['c'].yaxis.set_tick_params(labelsize=22)
axs['c'].yaxis.set_major_locator(MaxNLocator(integer=True))
axs['c'].set_facecolor('gainsboro')
axs['c'].set_xticks([-2.655, -2.46, -2.265, -2.07, -1.87, -1.675])
axs['c'].set_xticklabels(['CurPol','NDC','NZ','NZ-Al','NZ-Br', 'NZ-St'],fontsize=22,rotation=45)
custom_legend = [Line2D([0], [0], color='black', linestyle='--',label='Total emissions'),
                Patch(facecolor=([179/256, 179/256, 179/256]), edgecolor=([179/256, 179/256, 179/256]),label='non-CO\u2082'),
                Patch(facecolor=([229/256, 196/256, 148/256]), edgecolor=([229/256, 196/256, 148/256]),label='CO\u2082|Transport'),
                Patch(facecolor=([166/256, 216/256, 84/256]), edgecolor=([166/256, 216/256, 84/256]),label='CO\u2082|Industry'),
                Patch(facecolor=([231/256, 138/256, 195/256]), edgecolor=([231/256, 138/256, 195/256]),label='CO\u2082|Electricity'),
                Patch(facecolor=([252/256, 141/256, 98/256]), edgecolor=([252/256, 141/256, 98/256]),label='CO\u2082|Buildings'),                                
                Patch(facecolor=([102/256, 194/256, 165/256]), edgecolor=([102/256, 194/256, 165/256]),label='CO\u2082|AFOLU')]
axs['c'].legend(handles=custom_legend, loc='upper right',bbox_to_anchor=(1, 1),prop=dict(size=20),ncol=1,framealpha=0) 
