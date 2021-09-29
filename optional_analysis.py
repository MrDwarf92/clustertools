#Date modified: 05/05/2021, 14:45
#Last Change: Removed cluster size distribution
#Author: Stefan Zeisl

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math
from pathlib import Path
from file_preparation import file_preparation
from distance import calculate_mean_distance

def plot_statistics(cluster_ss,bins):
    fig, axs = plt.subplots(1,constrained_layout=True,ncols=2)
    #bins = int(input("Number of bins [5]: ") or "5")

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
    plt.show()


def chemical_analysis(cluster_data):
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
    element_list_fmt =[x[:x.find('Count')-1]+" at%" for x in chemistry_list.index]

    for x in element_list:
        cluster_data[x+'_pct'] = 100*(cluster_data[x+' Count']/cluster_data['Sum Count'])

    df_out = pd.DataFrame([chemistry_list.to_numpy()],columns=element_list_fmt)
    #str_elements = ''
   # for elem in element_list:
   #     str_elements += (elem+' at%;')
   # str_chem = ''
   # for chem in chemistry_list:
   #     str_chem += str(round(chem,2))+';'

    #printing the average chemical composition
   # print('')
   # print('average chemical composition of clusters')
   # print(str_elements)
    #print(str_chem)
    return df_out
