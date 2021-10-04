import cluster_analysis_base
import ipywidgets as widget
import matplotlib.pyplot as plt
import codecs
import pandas as pd
import numpy as np
from io import StringIO

class ClusterCalcMain():
    
    def __init__(self):
        #print("init: "+self.__class__.__name__)
        self.df_data = None
    
    def open_file(self, uploader_object):
        filename = next(iter(uploader_object.value.keys()),None)
        a = None
        if filename:
            a = uploader_object.value[filename]['content']
        a_text=codecs.decode(a,encoding='utf-8')
        df = pd.read_csv(StringIO(a_text),delimiter=',',header=10,skip_blank_lines = False)
        if df.columns[0] == "Unnamed: 0":
            df.rename(columns={"Unnamed: 0":"Cluster"},inplace=True)
        self.df_data=df
        return df
        
    def get_phase_list(self):
        phase_list = pd.read_csv("./data/phases.csv",delimiter=';',header=0)
        phase_list['Display'] = phase_list['ID'] + " (" + phase_list['volume'].astype("str")+" nm^3)"
        return phase_list
    
    def get_matrix_list(self):
        matrix_list = pd.read_csv("./data/matrix.csv",delimiter=';',header=0)
        matrix_list['Display'] = matrix_list['ID'] + " (" + matrix_list['volume'].astype("str")+" nm^3)"
        return matrix_list