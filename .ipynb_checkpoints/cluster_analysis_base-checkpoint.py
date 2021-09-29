#Date modified: 05/05/2021, 14:45
#Last Change: Added a mean distance calculation, Implementation of functions
#Author: Stefan Zeisl

import pandas as pd
import numpy as np
import math
from file_preparation import file_preparation


def calculate_statistics(cluster_data,vtotal,phase,va_opt):
    
    #Definition of Volumes in [nm3] of the unit cells of [Fe, beta, eta]
    unit_volumes = np.array([0.0118199515, 0.011943936, 0.0116875])
    if phase==2:
        unit_volumes = np.array([0.0118199515, 0.011943936, 0.0116875,va_opt])  
    
    cluster_ss = cluster_data [['Cluster',"V_Extent (nm^3) Total'",'e_length','d_eq','cyl_dia','Ranged Ions']]
    
    type = phase+1 #input from phase-value= 0 or 1 for beta or eta, so we need to add 1
    
    #Getting all ions for the Fv calculation
    ions_precip = cluster_data['Ranged Ions'].sum()
    #ions_precip = ions_total-cluster_data['Ranged Ions'].iloc[0]
    v_ions = (ions_precip/0.37)*unit_volumes[type] 
    v_ion_factor = unit_volumes[type]/(0.37)
    
    #Calculating some stuff. N_clusters -> Number of clusters (basically just count(*)-1), Fv -> Volume fraction, Nv -> Number density
    N_clusters = (cluster_ss['Cluster'].count())
    Fv = (v_ions)/vtotal
    Nv = N_clusters/vtotal
    eq_dia = cluster_ss['d_eq'].mean()
    cyl_dia = cluster_ss['cyl_dia'].mean()
    mean_length = cluster_ss['e_length'].mean()
    output = ""
    ##OUTPUT
    #print('')
    #print('Cluster statistics:\n')
    #print('Number of ions: '+str(ions_precip))
    #print('Number of clusters;'+str(N_clusters))
    #print('Volume fraction of clusters [%];' + str(round(Fv*100,2)))
    #print('Number density [m^-3];' + np.format_float_scientific((Nv*1e27),precision=2))
    #print('Equivalent spherical diameter [nm];' + str(round(eq_dia,2)))
    #print('Mean length [nm];' + str(round(mean_length,2)))
    #print('Cylindrical diameter [nm];' + str(round(cyl_dia,2)))
    
    ##OUTPUT HTML
    output=output+'Cluster statistics:'
    output=output+"<table border=0 width=auto>"
    output=output+"<tr><td>"+'Number of ions </td><td>'+str(ions_precip)+"</tr>"
    output=output+"<tr><td>"+'Number of clusters</td><td>'+str(N_clusters)+"</tr>"
    output=output+"<tr><td>"+'Volume fraction of clusters [%]</td><td>' + str(round(Fv*100,2))+"</tr>"
    output=output+"<tr><td>"+'Number density [m^-3]</td><td>' + np.format_float_scientific((Nv*1e27),precision=2)+"</tr>"
    output=output+"<tr><td>"+'Equivalent spherical diameter [nm]</td><td>' + str(round(eq_dia,2))+"</tr>"
    output=output+"<tr><td>"+'Mean length [nm]</td><td>' + str(round(mean_length,2))+"</tr>"
    output=output+"<tr><td>"+'Cylindrical diameter [nm]</td><td>' + str(round(cyl_dia,2))+"</tr>"
    output=output+"</table>"
    return cluster_ss, cluster_data, output
    

def cluster_calc(filepath,vtotal,phase,va_opt, **kwargs):

    file_preparation(filepath)
    threshold = kwargs.get('threshold',-1)
    output = ""   
    
    #First 10 rows are just metadata
    #The first column of the CSV file must be renamed to "Cluster", empty columns can be removed
    cluster_data = pd.read_csv(filepath,delimiter=',',header=10,skip_blank_lines = False)

    #We now want to drop the first line (matrix)
    cluster_data.drop(index=0,inplace=True)
    
    #Calculating the ellipsoid length and equivalent mean diameter
    cluster_data['e_length'] = 2*cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].max(axis=1) #longest axis of an ellipsoid

    #Calculates the mean equivalent diameter of an elippsoid
    #The calculation was split up for testing purposes, now I am to lazy to piece everything back togeter
    cluster_data['d_eq_1'] = 3*cluster_data["V_Extent (nm^3) Total'"]
    cluster_data['d_eq'] = 2*((cluster_data.d_eq_1/(4*math.pi))**(1/3))
    cluster_data['cyl_dia'] = 2*(cluster_data["V_Extent (nm^3) Total'"]/(cluster_data['e_length']*math.pi))**0.5
    
    #If a threshold for a bimodal distribution was defined, split up the calculation in two!
    if threshold>0:
        filter_mas = cluster_data['d_eq']>=threshold
        filter_menos = cluster_data['d_eq']<threshold
        data_mas = cluster_data.where(filter_mas,inplace=False)
        data_menos = cluster_data.where(filter_menos,inplace=False)
        
        output=output+"<h2>Precipitates >= "+str(threshold)+"</h2>"
        cluster_ss, cluster_data, o1 = calculate_statistics(data_mas,vtotal,phase,va_opt)
        output=output+o1
        
        output=output+"<h2>Precipitates <"+str(threshold)+"</h2>"
        cluster_ss, cluster_data, o2 = calculate_statistics(data_menos,vtotal,phase,va_opt)
        output=output+o2
        
        output=output+"<h2>All precipitates</h2>"
    
    
    cluster_ss, cluster_data, o_all = calculate_statistics(cluster_data,vtotal,phase,va_opt)
    output=output+o_all

    return cluster_ss, cluster_data, output