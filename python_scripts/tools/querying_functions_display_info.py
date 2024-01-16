#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 11:45:35 2024

@author: samiha
"""

import pandas as pd
import numpy as np
import pubchempy as pcp
import matplotlib.pyplot as plt
from NEIVA.python_scripts.connect_with_mysql import*
from sqlalchemy import text



def table_info (database, fire_type):
    bk_db=connect_db('backend_db')
    dd=pd.read_sql(text('select * from bkdb_info_table_name'), con=bk_db)
    dd_final=dd[dd['db']==database].reset_index(drop=True)
    dd_final=dd_final[dd_final['fire_type'].str.contains(fire_type)]
    return dd_final[['tbl_name','fire_type','study','source','doi']]
    
def summary_table (fire_type):
    bk_db=connect_db('backend_db')
    dd=pd.read_sql(text('select * from bkdb_info_efcol'), con=bk_db)
    dd[dd['fire_type']==fire_type].reset_index(drop=True)
    if fire_type!='cookstove':
        return dd[['efcol','measurement_type','MCE','fuel_type','study']]
    else:
        return dd[['efcol','measurement_type','MCE','fuel_type','cookstove_name','cookstove_type','study']]

def display_pollutant_category():
    bk_db=connect_db('backend_db')
    output_db=connect_db('neiva_output_db')
    
    rdf=pd.read_sql(text('select * from Recommended_EF'), con=output_db)
    ll=rdf['pollutant_category'].unique()
    return list(ll)

def property_variables ():
    bk_db=connect_db('backend_db')
    df=pd.read_sql(text('select * from property_surrogate_info'), con=bk_db)
    return df[['column name', 'description', 'unit']]
    

def model_surrogates(chem):
   bk_db=connect_db('backend_db')
   output_db=connect_db('neiva_output_db')

   pp=pd.read_sql(text('select * from Property_Surrogate'), con=output_db)
   return list(pp[chem].unique())


ll=list(df[df['fire_type']=='multiple fire type'].index)

for i in range(len(ll)):
    ss=df['study'].iloc[ll[i]]
    df.loc[ll[i],'fire_type']=';'.join(df2['fire_type'][df2['study']==ss].unique())
    




