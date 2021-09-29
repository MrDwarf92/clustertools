#Date modified: 08/09/2020, 10:13:24
#Last Change: Removed cluster size distribution
#Author: Stefan Zeisl

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
from filecrawler import filecrawler
from file_preparation import file_preparation

#Look for possible paths to make things easier

filepath=''

while filepath == '':
    filepath = filecrawler()

file_preparation(filepath)

#First 10 rows are just metadata
#The first column of the CSV file must be renamed to "Cluster", empty columns can be removed
cluster_data = pd.read_csv(filepath,delimiter=',',header=10,skip_blank_lines = False)

#We want to drop the first line (matrix)
cluster_data.drop(index=0,inplace=True)

#Calculating the ellipsoid length and equivalent mean diameter
cluster_data['e_length'] = 2*cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].max(axis=1) #longest axis of an ellipsoid
cluster_data['e_oblate'] = cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].min(axis=1)/cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].median(axis=1) #longest axis of an ellipsoid
cluster_data['e_aspect'] = cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].median(axis=1)/cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].max(axis=1) #longest axis of an ellipsoid

#Calculates the mean equivalent diameter of an elippsoid
#The calculation was split up for testing purposes, now I am to lazy to piece everything back togeter
cluster_data['d_eq_1'] = 3*cluster_data["V_Extent (nm^3) Total'"]
cluster_data['d_eq'] = 2*((cluster_data.d_eq_1/(4*math.pi))**(1/3))
cluster_data['cyl_dia'] = 2*(cluster_data["V_Extent (nm^3) Total'"]/(cluster_data['e_length']*math.pi))**0.5

cluster_ss = cluster_data [['Cluster',"V_Extent (nm^3) Total'",'e_length','e_oblate','e_aspect','d_eq','cyl_dia','Solute Ions']]

#User needs to input the total volume of the tip
vtotal = float(input('Enter total volume of tip [nm^3]: '))

#Calculating some stuff. N_clusters -> Number of clusters (basically just count(*)-1), Fv -> Volume fraction, Nv -> Number density
N_clusters = (cluster_ss['Cluster'].count())
Fv = cluster_ss["V_Extent (nm^3) Total'"].sum()/vtotal
Nv = N_clusters/vtotal
eq_dia = cluster_ss['d_eq'].mean()
cyl_dia = cluster_ss['cyl_dia'].mean()
mean_length = cluster_ss['e_length'].mean()


##OUTPUT
print('')
print('Cluster statistics:\n')
print('Number of clusters;'+str(N_clusters))
print('Volume fraction of clusters [%];' + str(round(Fv*100,2)))
print('Number density [m^-3];' + np.format_float_scientific((Nv*1e27),precision=2))
print('Equivalent spherical diameter [nm];' + str(round(eq_dia,2)))
print('Mean length [nm];' + str(round(mean_length,2)))
print('Cylindrical diameter [nm];' + str(round(cyl_dia,2)))
print('')

fig, axs = plt.subplots(1,constrained_layout=True,ncols=2)

bins = int(input("Number of bins [5]: ") or "5")

axs[0].tick_params(labelsize=15)
axs[0].set_title('Length distribution')
axs[0].set_ylabel('Frequency',size=15)
axs[0].set_xlabel('Length [nm]',size=15)
axs[0].hist(cluster_ss['e_length'],color='b',bins=bins,edgecolor='black',linewidth=0.8)

axs[1].tick_params(labelsize=15)
axs[1].set_title('Diameter distribution')
axs[1].set_ylabel('Frequency',size=15)
axs[1].set_xlabel('equivalent Diameter [nm]',size=15)
axs[1].hist(cluster_ss['d_eq'],bins=bins,color='b',edgecolor='black',linewidth=0.8)


# axs[0,1].set_title('Oblateness distribution')
# axs[0,1].set_ylabel('Frequency')
# axs[0,1].set_xlabel('Oblateness value')
# axs[0,1].hist(cluster_ss['e_oblate'],bins=bins,color='b',edgecolor='black',linewidth=0.8)
#
# axs[1,1].set_title('Aspect-ratio distribution')
# axs[1,1].set_ylabel('Frequency')
# axs[1,1].set_xlabel('Aspect-ratio')
# axs[1,1].hist(cluster_ss['e_aspect'],bins=bins,color='b',edgecolor='black',linewidth=0.8)

#####
#Routine for calculating the average chemical composition
#####

#Finding all columns with 'Count' in it
cols_ranged = [x for x in cluster_data.columns if 'Count' in x]


#Summing up the total number of ions per cluster, calculationg percentages
cluster_data['Sum Count'] = cluster_data[cols_ranged].sum(axis=1)
sum_all = cluster_data['Sum Count'].sum()

#Summing up the total number of ions per element
sum_elements = cluster_data[cols_ranged].sum(axis=0)

#Formating and printing
chemistry_list=((sum_elements/sum_all)*100)
element_list =[x[:x.find('Count')-1] for x in chemistry_list.index]

for x in element_list:
    cluster_data[x+'_pct'] = 100*(cluster_data[x+' Count']/cluster_data['Sum Count'])

# cols_pct = [x for x in cluster_data.columns if '_pct' in x]
# chem_stddev = cluster_data[cols_pct].std(axis=0)
# print(chem_stddev)

str_elements = ''
for elem in element_list:
    str_elements += (elem+' at%;')

str_chem = ''
for chem in chemistry_list:
    str_chem += str(round(chem,2))+';'

# str_stdlist = ''
# for std in std_list:
#     str_stdlist += str(round(chem,2))+';'

#printing the average chemical composition
print('')
print('average chemical composition of clusters')
print(str_elements)
print(str_chem)


plt.show()
