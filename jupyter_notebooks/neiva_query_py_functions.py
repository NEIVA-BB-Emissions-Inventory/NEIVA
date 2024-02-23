# -*- coding: utf-8 -*-
"""NEIVA_query_py_functions.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1vQzswdGvSaY7e0h5NEYUGzO7EYRCzcib

# **Demonstrate the use cases and features of the `neivapy` python package**

## **1. Setting up the NEIVA database in the colab environment.**
"""

!pip install mysql-connector-python # Install the necessary package to connect Python with MySQL databases.
!pip install pubchempy
!apt-get update
!pip install pymysql
!apt-get -y install mysql-server    # Install the MySQL server on the Colab environment.
!service mysql start                # With MySQL install, this starts the server.

# Setting the password. Here 'root' is used as password.

!mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH 'mysql_native_password' BY 'root';FLUSH PRIVILEGES;"

# Remove the existing NEIVA repository if it exists.
!rm -rf NEIVA
# Download the NEIVA repository from GitHub
!git clone https://github.com/NEIVA-BB-emissions-Inventory/NEIVA.git

# Check if the repository is downloaded by listing its contents.
!ls NEIVA/data

# Initialize MySQL databases and import data from NEIVA SQL files
!mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS backend_db"
!mysql -u root -proot backend_db < NEIVA/data/backend_db.sql
!mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS legacy_db"
!mysql -u root -proot legacy_db < NEIVA/data/legacy_db.sql
!mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS neiva_output_db"
!mysql -u root -proot neiva_output_db < NEIVA/data/neiva_output_db.sql
!mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS primary_db"
!mysql -u root -proot primary_db < NEIVA/data/primary_db.sql
!mysql -u root -proot -e "CREATE DATABASE IF NOT EXISTS raw_db"
!mysql -u root -proot raw_db < NEIVA/data/raw_db.sql

"""
---
## An overview of the database content is given below-
*   `legacy_db (ldb)`: The Akagi et al supplement, inlcuding 2014 and 2015 updates, are stored as tabled in this repository.
*   `raw_db (rdb)`: Data from selected publciations are stores as tables in the repository.
*   `primary_db (pdb)`: Data from legacy and raw db were reformatted to achieve a consistent structure and stored in this db.
*   `neiva_output_db` (`output_db`): The output of the data integartion and processing algorithmn is stored in this db. It contains 4 tables:
`Integrated_EF` (`integrated ef`): The output of the data integration step is stored in this table.
`Processed_EF` (`processed ef`): The Integreated_EF table undergoes several data processing steps, the output is stored in Processed_EF table.
`Recommended_EF` (`processed ef`): The calculated averages of all EFs for each of the fire types are stored in this table.
`Property_Surrogate`: Chemical and physical property data, as well as surroagte model species assignments for each of the NMOC_g (Non methane organic compound gaseous) is stored in this table.
*   `backend_db` (`bk_db`): Tables that are used in the python scripts for processing data and generating tables are stored in this database.
---"""

!mysql -u root -proot -e "show databases;"

!mysql -u root -proot -e "use neiva_output_db; show tables;"

"""## **2. Import the `neivapy` package and other essential python libraries**"""

import NEIVA.neivapy as nv

from sqlalchemy import text
import pandas as pd
import warnings
warnings.simplefilter("ignore", UserWarning)
from google.colab import files

"""## **3 Demonstrate query functions**

##**3.1 Display information**

`nv.fire_type()` Returns the list of the fire types.
"""

nv.fire_type()

"""`nv.table_info(database, fire type)`Returns a list of table names along with
associated information.
*   Options for database: `ldb` (legacy db), `rdb` (raw db), `pdb` (primary db)
*   Options for fire type: Can be obtained from `nv.fire_type()` function.
"""

dd=nv.table_info ('rdb','garbage burning')
dd

# download data
dd.to_csv('dd.csv')
files.download('dd.csv')

"""`nv.summary_table(fire type, measurement type)` Returns a list of emission factor (EF) column names of the integrated EF table along with information- MCE, fuel type, cookstove name if available.
*   Options for fire type: Can be obtained from `nv.fire_type()` function.
*   Options for measurement type: `lab`, `field`, `all`
"""

nv.summary_table('cookstove', 'field')

"""`nv.display_pollutant_category()` Displays the list of pollutant category."""

nv.display_pollutant_category()

"""`nv.property_varaibles()` Displays the property variables, chemcial mechanism, description, unit, sources of the Property_Surrogate table."""

nv.property_variables()

"""`nv.model_surrogate()` Displays the unique set of model surrogates for a specified chemical mechanism.
*   Options for chemical mechanism: `S07`, `S07T`, `S18B`, `MOZT1`, `GEOS_chem`

*Note:* The description of the chemcial mechanism variables can be obtained from `nv.property_variables()`.
"""

nv.model_surrogates('MOZT1')

"""## **3.2 Query emission factor (EF)**

`nv.select_compound(fire type, compound, table_or_db)` Returns the EF data.
*   Options for fire type: Can be optained from `nv.fire_type()`
*   Options for compound: `compound name (e.g., phenol, methanol)` which includes inorganic gas, methane, NMOC_g, NMOC_p and `PM2.5*`,`PM2.5`, `PM10`,`PM1`,`PM2.5(PM1-PM5)`, `OC`, `BC`, `EC`, `OA`, `NOx_as_NO`.
*   Options for table_or_db: `integrated ef`, `processed ef`, `recommended ef`, `ldb` (legacy db), `rdb` (raw db).
"""

dd=nv.select_compound ('savanna', 'PM2.5', 'processed ef')
dd[['legend','EF']]

"""`nv.select_chemical_formula(fire_type, chemical_formula, table name)` Returns the EF data.
*   Options for chemcial formula: `chemical formula of compounds` (e.g., CO, CO2, C10H16).
*   Options for table name: `integrated ef`, `processed ef`, `recommended ef`.


"""

nv.select_chemical_formula ('savanna', 'CHNO', 'integrated ef')

"""`nv.select_pm_data(fire type, table name)` Returns EF of PM2.5*, PM10, OA, OC, BC, EC.
*   Options for table name: `integrated ef`, `processed ef`, `recommended ef`.
"""

nv.select_pm_data ('crop residue', 'processed ef')

"""`nv.select_ef_pollutant_category(fire type, pollutant category)` Returns EF data.
*   Options for pollutant category: Can be obtained from `nv.display_pollutant_category()`.
"""

nv.select_ef_pollutant_category('crop residue', 'PM optical property')

"""`nv.compare_lab_field(fire type, compound, table name)` Returns the mean EF, mean MCE, number of data count of laboratory versus field data.
*   Options for compound: `compound name (e.g., phenol, methanol)` which includes inorganic gas, methane, NMOC_g, NMOC_p and `PM2.5*`, `PM10`, `OC`, `BC`, `EC`, `OA`, `NOx_as_NO`.
*   Options for table name: `integrated ef`, `processed ef`
"""

nv.compare_lab_field ('temperate forest', 'methanol','processed ef')

"""`nv.ef_sorted_by_property(df, fire type, chem, model surrogate, property variable)` Returns the EF of NMOC_g sorted by the specified property varaible in ascending order. The NMOC_g is selected for a specifed fire type, chemical mechanism and model surrogate. This function also requires a dataframe as input.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for chemical mechasnim, property varaible can be obtained from `nv.property_varaibles()`.
*   Options for model surrogate can be obtained from `nv.model_surrogate()`.
"""

output_db=nv.connect_db('neiva_output_db')
rdf=pd.read_sql(text('select * from Recommended_EF'), con=output_db)
nv.ef_sorted_by_property (rdf, 'temperate forest', 'S22', 'XYNL', 'hc')

"""`nv.plot_ef(fire type, compound, table name)` Generates a scatter plot illustrating study(fuel type) versus EF the specified options.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for compound: `compound name (e.g., phenol, methanol)` which includes inorganic gas, methane, NMOC_g, NMOC_p and `PM2.5*`, `PM10`, `OC`, `BC`, `EC`, `OA`, `NOx_as_NO`.
*   Options for table name: `integrated ef`, `processed ef`


"""

nv.plot_ef('peat', 'carbon dioxide', 'integrated ef')

"""`nv.boxplot_ef(compound, fire type, table name)` This function id identical to `nv.plot_ef()` but it generates a boxplot of the EF data instead of a scatter plot.
*   Options for fire type: Can be obtained from nv.fire_type(). Additionally, the `all` option includes tropical forest, temperate forest, boreal forest, savanna, crop residue, peat)
*   Option for table name: `integrated ef`, `processed ef`


"""

nv.boxplot_ef ('PM2.5*', 'all', 'integrated ef')

"""`nv.mce_vs_ef(compound, fire_type)` This fucntion generates a scatter plot of the MCE versus EF data and produces a linear fit if the data count is greater than 4.
*   Options for compound: `compound name (e.g., phenol, methanol)` which includes inorganic gas, methane, NMOC_g, NMOC_p and `PM2.5*`, `PM10`, `OC`, `BC`, `EC`, `OA`, `NOx_as_NO`.
*   Options for fire type: Can be obtained from `nv.fire_type()` and `all`.
"""

nv.mce_vs_ef ('acetic acid', 'temperate forest')

"""## **3.3 Query NMOC_g emission profile**

`nv.voc_profile(df, chem, fire type)` Returns the mole fraction of the model surrogates. It requires a dataframe in recommended EF table format as input.
*   Options for chem (chemical mechanism): Can be obtained from `nv.property_variables()`.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
"""

output_db=nv.connect_db('neiva_output_db')
rdf=pd.read_sql(text('select * from Recommended_EF'), con=output_db)

"""`nv.calc_OHR(df, chem, fire type, sum_nmoc_g_ef_in_ppb)` Calculates the OH reactivity (OHR) of model surrogates. It requires a dataframe in recommended EF table format as input.
*   Options for chem(chemcial mechanism): Can be obtained from `nv.property_variables()`.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   `sum_nmoc_g_ef_in_ppb`: The summation of NMOC_g EF in ppb unit.
"""

nv.calc_OHR(rdf,'S07','temperate forest',91)

"""`nv.calc_VBS(df, fire type)` Calculates the volatility basis set. It requires a dataframe in recommended EF table format as input.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
"""

nv.calc_VBS(rdf,'temperate forest')

"""`nv.weighted_property(df, fire type, chem)` Calculates property variables weighted by the EF of individual compounds for each model surroagte. It requires a dataframe in the recommended EF table format as input.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for chem(chemcial mechanism): Can be obtained from `nv.property_variables()`.
"""

nv.weighted_property(rdf, 'peat', 'S07')

"""`nv.speciation_profile(fire type, chem, model surrogate)` Returns the EF of NMOC_g.
*   Options for fire type: Can be obtained from `nv.fire_type()`
*   Options for chem(chemical mechanism): Can be obtained from `nv.property_variables()`.
*   Options for model surrogate: Can be obtained from `nv.model_surrogate()`.
"""

nv.speciation_profile('temperate forest','S07','ARO2')

"""`nv.GFED_lumped_ef_calc(df, fire type, chem, model surrogate)` Calculates the lumped EF. A conversion factor is applied to the EF of NMOC_g, calculated as nC(i)*12/mm(i) *italicized text*, where *'i'* is represents a NMOC_g molecule, *'nC'* denotes the number of carbon atoms in the NMOC_g molecule, and *'mm(i)'* represents the molecular weight of the NMOC_g. It requires a dataframe in the recommended EF table format as input.


*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for chem(chemical mechanism): Can be obtained from `nv.property_varaible()`.
*   Options for model surrogate: Can be obtained from `nv.model_surrogate()`.
"""

nv.GFED_lumped_ef_calc(rdf, 'temperate forest', 'S07', 'ARO2')

"""`nv.abundant_nmog(fire type, chem, property)` Returns the 25 NMOC_g sorted by EF in ascending order.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for chem(chemical mechanism) and property: Can be obtained from `nv.property_varaible()`.
"""

nv.abundant_nmog('temperate forest', 'MOZT1', 'kOH')

"""`nv.boxplot_abundant_nmog(fire type)` Generates a boxplot displaying the 25 NMOC_g compounds sorted by EF in ascending order.
*   Options for fire type: Can be obtained from `nv.fire_type()`.

"""

nv.boxplot_abundant_nmog('crop residue')

"""`nv.nmog_with_high_n(fire type, chem, property)` Retunrs the 25 NMOC_g sorted by data count in ascending order. It also displays the mapped model surrogate and property.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for chem(chemical mechanism) and property: Can be obtained from `nv.property_varaible()`.
"""

nv.nmog_with_high_n('cookstove', 'S07', 'kOH')

"""`nv.nmog_with_high_ohr (df, fire type, chem, sum_nmoc_g_ef_ppb)` Returns the 25 NMOC_g sorted by OHR in ascending order. It requires a dataframe in recommended table format as input.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for chem(chemical mechanism): Can be obtained from `nv.property_varaible()`.
*   `sum_nmoc_g_ef_ppb`: The summation of NMOC_g EF in ppb unit.
"""

nv.nmog_with_high_ohr (rdf, 'temperate forest', 'S07', 91)

"""`nv.plot_model_surrogate(df, fire type, chem, model surrogate)` Generates a boxplot illustrating NMOC_g versus EF. The NMOC_g are selected based on the speciifed chemical mechanism and model surrogate. If there are more than 25 NMOC_gs, it plots the first 25 NMOC_g.
*   Options for fire type: Can be obtained from `nv.fire_type()`.
*   Options for chem(chemical mechanism): Can be obtained from `nv.property_varaible()`.
*   Options for model surroagte: Can be obtained from `nv.model_surrogates()`.
"""

nv.plot_model_surrogate(rdf, 'temperate forest', 'S07','IPRD')