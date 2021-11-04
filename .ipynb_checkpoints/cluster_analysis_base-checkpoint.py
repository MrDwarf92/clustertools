#Date modified: 01/10/2021
#Last Change: Changed it into a class-based design
#Author: Stefan Zeisl

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
#from file_preparation import file_preparation

class ClusterAnalysis:
    
    def __init__(self,all_data, p_volume, m_volume):
        self.all_data = all_data
        self.p_volume = p_volume
        self.m_volume = m_volume
        self.cluster_data = None
        self.cluster_ss = None
        pass

    def calculate_statistics(self):

        #Duplicate and remove matrix
        self.cluster_ss = self.cluster_data [['Cluster',"V_Extent (nm^3) Total'",'e_length','d_eq','cyl_dia','Ranged Ions']]
        #print(self.cluster_ss)
        #self.cluster_ss.drop(index=0,inplace=True)

        #Getting the matrix ion count
        df_matrix = self.all_data.loc[self.all_data['Cluster']=='Matrix']
        m_ions = df_matrix['Ranged Ions'].sum()

        #Getting the precipitate ion count
        p_ions = self.cluster_data['Ranged Ions'].sum()


        Fv = (p_ions*self.p_volume)/(m_ions*self.m_volume+p_ions*self.p_volume)




        #Calculating some stuff. N_clusters -> Number of clusters (basically just count(*)-1), Fv -> Volume fraction, Nv -> Number density
        N_clusters = (self.cluster_ss['Cluster'].count())
        #Fv = (v_ions)/vtotal
        vtotal=(m_ions*self.m_volume+p_ions*self.p_volume)/0.37
        Nv = N_clusters/vtotal
        eq_dia = self.cluster_ss['d_eq'].mean()
        eq_dia_std = self.cluster_ss['d_eq'].std()
        cyl_dia = self.cluster_ss['cyl_dia'].mean()
        cyl_dia_std = self.cluster_ss['cyl_dia'].std()
        mean_length = self.cluster_ss['e_length'].mean()
        mean_length_std = self.cluster_ss['e_length'].std()
        #output = ""

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
        output='Cluster statistics:'
        output=output+"<table border=0 width=auto>"
        output=output+"<tr><td>"+"Quantity</td><td> Value </td><td>Std. Dev.</td></tr>"
        output=output+"<tr><td>"+'Total measurement volume (nm^3): </td><td>'+str(vtotal)+"</td><td></td></tr>"
        output=output+"<tr><td>"+'Number of ions </td><td>'+str(p_ions)+"</td><td></td></tr>"
        output=output+"<tr><td>"+'Number of clusters</td><td>'+str(N_clusters)+"</td><td></td></tr>"
        output=output+"<tr><td>"+'Volume fraction of clusters (%)</td><td>' + str(round(Fv*100,2))+"</td><td></td></tr>"
        output=output+"<tr><td>"+'Number density (m^-3)</td><td>' + np.format_float_scientific((Nv*1e27),precision=2)+"</td><td></td></tr>"
        output=output+"<tr><td>"+'Equivalent spherical diameter (nm)</td><td>' + str(round(eq_dia,2))+"</td><td>"+str(round(eq_dia_std,2))+"</td></tr>"
        output=output+"<tr><td>"+'Mean length (nm)</td><td>' + str(round(mean_length,2))+"</td><td>"+str(round(mean_length_std,2))+"</td></tr>"
        output=output+"<tr><td>"+'Cylindrical diameter (nm)</td><td>' + str(round(cyl_dia,2))+"</td><td>"+str(round(cyl_dia_std,2))+"</td></tr>"
        output=output+"</table>"
        return output


    def cluster_calc(self,threshold):

        #threshold = Diameter value for statistic separation

        #We now want to drop the first line (matrix)
        #however need the matrix data for later
        
        self.cluster_data = self.all_data.drop(index=0)

        #Calculating the ellipsoid length and equivalent mean diameter
        self.cluster_data['e_length'] = 2*self.cluster_data[["Extent_x (nm) Total'","Extent_y (nm) Total'","Extent_z (nm) Total'"]].max(axis=1) #longest axis of an ellipsoid

        #Calculates the mean equivalent diameter of an elippsoid
        #The calculation was split up for easier debugging
        self.cluster_data['d_eq_1'] = 3*self.cluster_data["V_Extent (nm^3) Total'"]
        self.cluster_data['d_eq'] = 2*((self.cluster_data.d_eq_1/(4*math.pi))**(1/3))
        self.cluster_data['cyl_dia'] = 2*(self.cluster_data["V_Extent (nm^3) Total'"]/(self.cluster_data['e_length']*math.pi))**0.5

        #If a threshold for a bimodal distribution was defined, split up the calculation in two!
        if threshold:
            filter_mas = self.cluster_data['d_eq']>=threshold
            filter_menos = self.cluster_data['d_eq']<threshold
            data_mas = self.cluster_data.where(filter_mas,inplace=False)
            data_menos = self.cluster_data.where(filter_menos,inplace=False)
            
            cluster_data_orig = self.cluster_data
            
            output="<h2>Precipitates >= "+str(threshold)+"</h2>"
            self.cluster_data = data_mas
            o1 = self.calculate_statistics()
            output=output+o1

            output=output+"<h2>Precipitates <"+str(threshold)+"</h2>"
            self.cluster_data = data_mas
            o2 = self.calculate_statistics()
            output=output+o2

            output=output+"<h2>All precipitates</h2>"
        else:
            output = self.calculate_statistics()

        return output
    
    def plot_statistics(self,bins):
        fig, axs = plt.subplots(1,constrained_layout=True,ncols=2)
        #bins = int(input("Number of bins [5]: ") or "5")

        axs[0].tick_params(labelsize=15)
        axs[0].set_title('Length distribution')
        axs[0].set_ylabel('Frequency',size=15)
        axs[0].set_xlabel('Length [nm]',size=15)
        axs[0].hist(self.cluster_ss['e_length'],color='b',bins=bins,edgecolor='black',linewidth=0.8)
        
        axs[1].tick_params(labelsize=15)
        axs[1].set_title('Diameter distribution')
        axs[1].set_ylabel('Frequency',size=15)
        axs[1].set_xlabel('equivalent Diameter [nm]',size=15)
        axs[1].hist(self.cluster_ss['d_eq'],bins=bins,color='b',edgecolor='black',linewidth=0.8)
        plt.show()