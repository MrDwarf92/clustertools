#Date modified: 13/08/2020, 10:44:32

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import functools
import itertools
import time
import math
from scipy.spatial import Delaunay
from filecrawler import filecrawler

#Look for possible paths to make things easier


def timer(func):
    @functools.wraps(func)
    def wrapper_timer(*args):
        start_time = time.perf_counter()
        value = func(*args)
        end_time = time.perf_counter()
        run_time = end_time-start_time
        print(f"Finished {func.__name__!r} in {run_time:.4f} s")
        return value
    return wrapper_timer


def openfile():
    filepath='/drives/uni/PhD/Maraging Steels/clusters_debug.csv'
    while filepath == '':
        filepath = filecrawler()
    return filepath


def calculate_distance_3D(p1, p2):
    distance = ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)**0.5
    return distance


def calculate_mean(vertices_list,point_list,volume_list,is_surface_to_surface):
    sum = 0
    subtractor = 0
    distances = np.zeros(len(vertices_list))
    vertex_list_new = np.zeros((len(vertices_list),6))
    counter = 0
    for x in vertices_list:
        subtractor = 0
        p1 = point_list[x[0]]
        p2 = point_list[x[1]]
        vertex_list_new[counter] = [p1[0],p1[1],p1[2],p2[0],p2[1],p2[2]]

        #When surface to surface is selected (True)
        #calculate the radius of both spheres and subtract them from the distance!
        if is_surface_to_surface:
            subtractor = (3*volume_list[x[0]]/(4*math.pi))**(1/3)+(3*volume_list[x[1]]/(4*math.pi))**(1/3)

        distances[counter]=calculate_distance_3D(p1,p2)-subtractor
        counter = counter +1

    mean_distance = np.median(distances)
    stdev = np.std(distances)
    return mean_distance, stdev, vertex_list_new

def calculate_mean_2(neighbor_list,point_list,volume_list):
    sum = 0
    subtractor = 0

    distance_list = np.zeros(len(neighbor_list))
    distance_x = np.zeros(4)
    i=0
    for x in neighbor_list:
        count = 0
        for nb in x:
            print(nb)
            #Check if neighbour of point "i" at position "count" is invalid (-1), if not: calculate distance and add to
            #distance list at position "count"
            #distance_x gets completely overwritten, so no need to "clear" it
            subtractor = (3*volume_list[i]/(4*math.pi))**(1/3)+(3*volume_list[nb]/(4*math.pi))**(1/3)
            distance_x[count] = np.NaN if nb == -1 else calculate_distance_3D(point_list[i],point_list[nb])-subtractor
            count = count+1
        distance_list[i] = np.min(distance_x)
        i=i+1
    return distance_list

def create_vertex_list(simplices):
    #Parameter simplices contains all tetrahedrons defined by the IDs of 4 points
    size = len(simplices)
    result = np.zeros((size,6),dtype=[('a','i4'),('b','i4')])

    #Adding all combination (unique per tetrahedron) of point tuples (vertices) to a list
    for x in np.arange(size):
        result[x] = list(itertools.combinations(simplices[x,:],2))

    #Vlist contains all vertices of all tetrahedrons
    v_list = result.flatten()

    #Sorting the list and removing duplicate shared vertices via mapping
    #res contains only unique vertices
    res = list({*map(tuple, map(sorted, v_list))})

    return res

def create_distance_list(points,simplices):
    vertex_list = create_vertex_list(simplices)
    distance_list = np.zeros(len(points))
    for x in vertex_list:
        distance = calculate_distance_3D(points[x[0]],points[x[1]])
        if distance_list[x[0]] > distance or distance_list[x[0]] == 0:
            distance_list[x[0]] = distance
        if distance_list[x[1]] > distance or distance_list[x[1]] == 0:
            distance_list[x[1]] = distance
    return distance_list




def calculate_mean_distance(filepath):
    #First 10 rows are just metadata
    #The first column of the CSV file must be renamed to "Cluster", empty columns can be removed
    cluster_data = pd.read_csv(filepath,delimiter=',',skip_blank_lines=False,header=10)

    #We want to drop the first line (matrix)
    cluster_data.drop(index=0,inplace=True)
    cluster_ss = cluster_data [['Center_x (nm) Ranged\'','Center_y (nm) Ranged\'','Center_z (nm) Ranged\'','V_Extent (nm^3) Total\'']]
    #Transforming Pandas Data to point list
    points = cluster_ss.values[:,0:3]
    volumes = cluster_ss.values[:,3]


    #Delaunay Triangulation of point list
    tri = Delaunay(points)
    vertices = create_vertex_list(tri.simplices)

    #new_distances = calculate_mean_2(tri.neighbors,points,volumes)
    distance_list = create_neighbor_list(points,tri.simplices)
    print(distance_list)


    fig = plt.figure()
    sx = 1
    sy=1
    sz=-1

    #vlist_new = calculate_mean(tri.simplices)
    ax = Axes3D(fig)
    ax.scatter(points[:,0]*sx,points[:,1]*sy,-points[:,2]*sz,s=100)
    for x in vlist_new:
        v_x = [x[0], x[3]]
        v_y = [x[1], x[4]]
        v_z = [x[2], x[5]]
        ax.plot(v_x,v_y,v_z,color='blue',linestyle='-')
    #ax.plot(vlist_new[:,0]*sx,vlist_new[:,1]*sy,-vlist_new[:,2]*sz,vlist_new[:,3]*sx,vlist_new[:,4]*sy,-vlist_new[:,5]*sz, color='blue',linestyle='-')
    plt.show()
