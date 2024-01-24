#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 12:34:51 2024

@author: samiha
"""

import pandas as pd
import numpy as np
import pubchempy as pcp
import matplotlib.pyplot as plt
from NEIVA.python_scripts.connect_with_mysql import*
from NEIVA.python_scripts.tools.assign_mozart_species import mozart_species
from NEIVA.python_scripts.data_integration_process.sort_molec_formula import *

from sqlalchemy import text


# This function returns the PM2.5, OC, BC data for a specified fire type and table name. The table name inlcudes three different tables
# integrated ef, processed ef, recommended ef.
def select_pm_data (ft, table_name):
    bk_db=connect_db('backend_db')
    output_db=connect_db('neiva_output_db')
    if table_name=='integrated ef':
        efcoldf=pd.read_sql(text('select * from bkdb_info_efcol'), con=bk_db)
        df=pd.read_sql(text('select * from Integrated_EF'), con=output_db)

        efcol=list(efcoldf['efcol'])
        efcoldf['BC']=df[efcol][df['id']=='BC'].values[0]
        efcoldf['OC']=df[efcol][df['id']=='OC'].values[0]
        efcoldf['PM2.5']=df[efcol][df['id']=='PM2.5'].values[0]
        efcoldf['OA']=df[efcol][df['id']=='OC'].values[0]

        return (efcoldf[['legend','MCE','PM2.5','OC','BC','OA']][efcoldf['fire_type']==ft].reset_index(drop=True))

    if table_name=='processed ef':
        efcoldf=pd.read_sql(text('select * from info_efcol_processed_data'), con=bk_db)
        df=pd.read_sql(text('select * from Processed_EF'), con=output_db)

        efcol=list(efcoldf['efcol'])
        efcoldf['BC']=df[efcol][df['id']=='BC'].values[0]
        efcoldf['OC']=df[efcol][df['id']=='OC'].values[0]
        efcoldf['PM2.5']=df[efcol][df['id']=='PM2.5'].values[0]
        efcoldf['OA']=df[efcol][df['id']=='OC'].values[0]

        return (efcoldf[['legend','PM2.5','OC','BC','OA']][efcoldf['fire_type']==ft].reset_index(drop=True))

    if table_name=='recommended ef':
        df=pd.read_sql(text('select * from Recommended_EF'), con=output_db)
        efcol='AVG_'+ft.replace(' ','_')
        iid=['PM<2.5','OC','BC','OA']
        return df[['compound',efcol]][df['id'].isin(iid)].reset_index(drop=True)


# This function returns the EF of specified pollutant category and fire type.
def select_ef_pollutant_category(ft, pc):
    bk_db=connect_db('backend_db')
    output_db=connect_db('neiva_output_db')
    
    efcol='AVG_'+ft.replace(' ','_')
    rdf=pd.read_sql(text('select * from Recommended_EF'), con=output_db)

    if pc=='PM optical property':
      return (rdf[['compound',efcol]][rdf['pollutant_category']==pc][rdf[efcol].notna()].reset_index(drop=True))
    else:
      return (rdf[['mm','formula','compound',efcol]][rdf['pollutant_category']==pc][rdf[efcol].notna()].reset_index(drop=True))

# This function returns the EF of specified compound name and table name (integrated ef, processed ef and recommended ef)
def select_compound(ft, com_name,table_name):
    bk_db=connect_db('backend_db')
    output_db=connect_db('neiva_output_db')

    if table_name=='integrated ef':
        df=pd.read_sql(text('select * from Integrated_EF'), con=output_db)
        efcoldf=pd.read_sql(text('select * from bkdb_info_efcol'), con=bk_db)
        allcol= ['legend','fuel_type','measurement_type','MCE',com_name]

    if table_name=='processed ef':
        df=pd.read_sql(text('select * from Processed_EF'), con=output_db)
        efcoldf=pd.read_sql(text('select * from info_efcol_processed_data'), con=bk_db)
        allcol= ['legend','measurement_type',com_name]

    try:
        aa=pcp.get_compounds(com_name, 'name')[0].inchi
        ind=df[df['id']==aa].index[0]
        efcol=list(efcoldf['efcol'])

        efcoldf[com_name]=df[efcol].iloc[ind].values
        efcoldf[com_name]=round(efcoldf[com_name],3)
    
        ll=efcoldf[allcol][efcoldf['fire_type']==ft]
        ll=ll.sort_values(by='measurement_type')
        ll=ll[ll[com_name].notna()]
        ll=ll.reset_index(drop=True)
        return ll

    except:
        return 'Cannot assin ID. Search by formula'

def select_chemical_formula (ft, formula,table_name):
    bk_db=connect_db('backend_db')
    output_db=connect_db('neiva_output_db')

    if table_name=='integrated ef':
        df=pd.read_sql(text('select * from Integrated_EF'), con=output_db)
        efcoldf=pd.read_sql(text('select * from bkdb_info_efcol'), con=bk_db)

    if table_name=='processed ef':
        df=pd.read_sql(text('select * from Processed_EF'), con=output_db)
        efcoldf=pd.read_sql(text('select * from info_efcol_processed_data'), con=bk_db)
    
    ll=list(efcoldf['efcol'][efcoldf['fire_type']==ft])
    cols=['mm','formula','compound']+ll
    
    return df[cols][df['formula']==formula].reset_index(drop=True)



def select_compound_rdf (ft, com_name):
    output_db=connect_db('neiva_output_db')
    df=pd.read_sql(text('select * from Recommended_EF'), con=output_db)
    
    try:
        aa=pcp.get_compounds(com_name, 'name')[0].inchi
        ind=df[df['id']==aa].index[0]
        col='AVG_'+ft.replace(' ','_')
        df[col]=round(df[col],3)
        return df[['mm','formula','compound',col]][ind:ind+1].reset_index(drop=True)
    except:
        return 'Cannot assign ID. Use chemical formula to search.'

def select_chemical_formula_rdf (ft, formula):
    output_db=connect_db('neiva_output_db')
    df=pd.read_sql(text('select * from Recommended_EF'), con=output_db)
    
    col='AVG_'+ft.replace(' ','_')
    
    return df[['mm','formula', col, 'id']][df['formula']==formula].reset_index(drop=True)
    


# Plots ef data of a specified fire type and table name
def plot_ef(compound,ft, table_name):
  bk_db=connect_db('backend_db')
  output_db=connect_db('neiva_output_db')
    
  if table_name=='processed ef':
    df=pd.read_sql(text('select * from Processed_EF'), con=output_db)
    efcoldf=pd.read_sql(text('select * from info_efcol_processed_data'), con=bk_db)

  if table_name=='integrated ef':
    df=pd.read_sql(text('select * from Integrated_EF'), con=output_db)
    efcoldf=pd.read_sql(text('select * from bkdb_info_efcol'), con=bk_db)

  try:
      iid=pcp.get_compounds(compound, 'name')[0].inchi
      ind=df[df['id']==iid].index[0]

      efcoldf[compound]=df[efcoldf['efcol']].iloc[ind].values
    
      ef_vals=list(efcoldf[compound][efcoldf['fire_type']==ft][efcoldf[compound].notna()])
      l1=efcoldf['study'][efcoldf['fire_type']==ft][efcoldf[compound].notna()]
      l2=efcoldf['fuel_type'][efcoldf['fire_type']==ft][efcoldf[compound].notna()]
      if table_name=='processed ef':
        ef_legend=list(l1)
      if table_name=='integrated ef':
        ef_legend=list(l1+':'+l2)
      
      # Plot the figure   
      import seaborn as sns
      pal = sns.color_palette('colorblind',10)
    
      ax1 = plt.subplot(111)
      plt.scatter(np.arange(len(ef_vals)), ef_vals, zorder=3, color=pal[0], edgecolor='k')
      plt.ylabel('Emission factor (g/kg)', fontsize=10)
      
      plt.tick_params(labelsize=10)
      ax1.grid(linestyle='--',color='#EBE7E0',zorder=4)
      ax1.tick_params(axis='x',which='both',bottom=False)
      plt.setp(ax1.spines.values(),lw=1.5)
    
      plt.title("Compound:"+compound+"; Fire type:"+ ft, fontsize=10)
      plt.xticks(np.arange(len(ef_vals)), ef_legend, rotation=90)
      plt.tight_layout()
  except:
         return 'Cannot assign ID. Use chemical formula to search.'
     
  return



