#Date modified: 05/05/2021, 14:45
#Last Change: Added a mean distance calculation, Implementation of functions
#Author: Stefan Zeisl

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
from filecrawler import filecrawler
from file_preparation import file_preparation
from distance import calculate_mean_distance
from optional_analysis import plot_statistics, chemical_analysis


#Definition of Volumes in [nm3] of the unit cells of [Fe, beta, eta]
unit_volumes = np.array([0.0118199515, 0.011943936, 0.0116875])

#Look for possible paths to make things easier
def openfile():
    filepath=''
    while filepath == '':
        filepath = filecrawler()
    file_preparation(filepath)
    return filepath


def cluster_analysis_main():

    filepath = openfile()
    #First 10 rows are just metadata
    #The first column of the CSV file must be renamed to "Cluster", empty columns can be removed
    cluster_data = pd.read_csv(filepath,delimiter=',',header=10,skip_blank_lines = False)

    #User needs to input the total volume of the tip
    vtotal = float(input('Enter total volume of tip [nm^3]: '))
    type = int(input('Enter the type of precipitate (1=NiAl, 2=Ni3Ti): '))

    #Getting all ions for the Fv calculation
    ions_total = cluster_data['Ranged Ions'].sum()
    ions_precip = ions_total-cluster_data['Ranged Ions'].iloc[0]
    v_ions = (ions_precip/0.37)*unit_volumes[type]
    v_ion_factor = unit_volumes[type]/(0.37)

    #We now want to drop the first line (matrix)
    cluster_data.drop(index=0,inplace=True)

    #Calculating the ellipsoid length and equivalent mean diameter
    cluster_data['e_length'] = 2*cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].max(axis=1) #longest axis of an ellipsoid

    #Calculates the mean equivalent diameter of an elippsoid
    #The calculation was split up for testing purposes, now I am to lazy to piece everything back togeter
    cluster_data['d_eq_1'] = 3*cluster_data["V_Extent (nm^3) Total'"]
    cluster_data['d_eq'] = 2*((cluster_data.d_eq_1/(4*math.pi))**(1/3))
    cluster_data['cyl_dia'] = 2*(cluster_data["V_Extent (nm^3) Total'"]/(cluster_data['e_length']*math.pi))**0.5

    cluster_ss = cluster_data [['Cluster',"V_Extent (nm^3) Total'",'e_length','d_eq','cyl_dia','Ranged Ions']]


    #Calculating some stuff. N_clusters -> Number of clusters (basically just count(*)-1), Fv -> Volume fraction, Nv -> Number density
    N_clusters = (cluster_ss['Cluster'].count())
    Fv = (v_ions)/vtotal
    Nv = N_clusters/vtotal
    eq_dia = cluster_ss['d_eq'].mean()
    cyl_dia = cluster_ss['cyl_dia'].mean()
    mean_length = cluster_ss['e_length'].mean()


    ##OUTPUT
    print('')
    print('Cluster statistics:\n')
    print('Number of ions: '+str(ions_precip))
    print('Number of clusters;'+str(N_clusters))
    print('Volume fraction of clusters [%];' + str(round(Fv*100,2)))
    print('Number density [m^-3];' + np.format_float_scientific((Nv*1e27),precision=2))
    print('Equivalent spherical diameter [nm];' + str(round(eq_dia,2)))
    print('Mean length [nm];' + str(round(mean_length,2)))
    print('Cylindrical diameter [nm];' + str(round(cyl_dia,2)))
    calculate_mean_distance(filepath)
    print('')

    #optional stuff
    #chemical_analysis(cluster_data)
    #plot_statistics(cluster_ss)

cluster_analysis_main()
