#Date modified: 13/08/2020, 10:44:32

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import functools
import itertools
import time
import math
from scipy.spatial import Delaunay
from mpl_toolkits.mplot3d import Axes3D

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



def calculate_distance_3D(p1, p2):
    distance = ((p1[0]-p2[0])**2+(p1[1]-p2[1])**2+(p1[2]-p2[2])**2)**0.5
    return distance


def calculate_mean_2(vertices_list,point_list,volume_list,is_surface_to_surface):
    sum = 0
    subtractor = 0
    distances = np.zeros(len(vertices_list))
    counter = 0
    for x in vertices_list:
        subtractor = 0
        p1 = point_list[x[0]]
        p2 = point_list[x[1]]

        #When surface to surface is selected (True)
        #calculate the radius of both spheres and subtract them from the distance!
        if is_surface_to_surface:
            subtractor = (3*volume_list[x[0]]/(4*math.pi))**(1/3)+(3*volume_list[x[1]]/(4*math.pi))**(1/3)

        distances[counter]=calculate_distance_3D(p1,p2)-subtractor
        counter = counter +1

    mean_distance = np.median(distances)
    stdev = np.std(distances)
    return mean_distance, stdev

def calculate_distances(distance_list,volume_list,is_surface_to_surface):
    subtractor = 0
    distances = np.copy(distance_list)
    #When surface to surface is selected (True)
    #calculate the radius of both spheres and subtract them from the distance!
    if is_surface_to_surface:
        for x in np.arange(len(distances)):
            subtractor = (3*volume_list[x]/(4*math.pi))**(1/3)+(3*distances[x,1]/(4*math.pi))**(1/3)
            distances[x,0] = distances[x,0]-subtractor
            if distances[x,0] <= 0:
                print(f"Distance smaller than zero: P1 = {int(x):d}       P2 = {int(distances[x,2]):d}    ")
    return distances

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

def create_distance_list(points,simplices,volume_list):
    vertex_list = create_vertex_list(simplices)
    distance_list = np.zeros((len(points),3))
    for x in vertex_list:
        distance = calculate_distance_3D(points[x[0]],points[x[1]])
        if distance_list[x[0],0] > distance or distance_list[x[0],0] == 0:
            distance_list[x[0],0] = distance
            distance_list[x[0],1] = volume_list[x[1]]
            distance_list[x[0],2] = x[1]
        if distance_list[x[1],0] > distance or distance_list[x[1],0] == 0:
            distance_list[x[1],0] = distance
            distance_list[x[1],1] = volume_list[x[0]]
            distance_list[x[1],2] = x[0]
    return distance_list

def plot_figure(distance_list, points,volumes):
    #distance list: [distance, volume, partner]
    fig = plt.figure()
    ax= Axes3D(fig)
    ax.scatter(points[:,0],points[:,1],points[:,2],s=volumes)
    for i in np.arange(len(distance_list)):
        p1 = i
        p2 = int(distance_list[i,2])
        x = [points[p1,0],points[p2,0]]
        y = [points[p1,1],points[p2,1]]
        z = [points[p1,2],points[p2,2]]
        ax.plot(x,y,z,color='blue',linestyle='-')
        
def plot_figure_2(d_list, points,volumes):
    fig = plt.figure()
    ax= Axes3D(fig)
    filtered = d_list[:,0]
    newpoints = np.array([[points[int(x),0],points[int(x),1],points[int(x),2],volumes[int(x)]] for x in filtered])
    print(newpoints)
    ax.scatter(newpoints[:,0],newpoints[:,1],newpoints[:,2],s=newpoints[:,3])
    color = 'blue'
    for i in np.arange(len(d_list)):
        p1 = i
        p2 = int(d_list[i,2])
        x = [points[p1,0],points[p2,0]]
        y = [points[p1,1],points[p2,1]]
        z = [points[p1,2],points[p2,2]]
        ax.plot(x,y,z,color='blue',linestyle='-')

def calculate_radius(volume):
    return (volume*(3/4)*(1/3.1415))**(1/3)

@timer
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
    
    if len(points)<4:
        print("Not enough points for distance evaluation! A minimum of 4 clusters is required!")
        return 0
    #Delaunay Triangulation of point list
    tri = Delaunay(points)
    vertices = create_vertex_list(tri.simplices)

    distance_list = create_distance_list(points,tri.simplices,volumes)

    #mean_distance_v, stdev_v = calculate_mean(vertices,points,volumes,True)
    distances_new = calculate_distances(distance_list,volumes,True)
    print(f"Mean distance of precipitates (surface-to-surface); {np.mean(distances_new[:,0]):.4f}; {np.std(distances_new[:,0]):.4f}")
    
    d_new = distances_new
    
    distances_new = calculate_distances(distance_list,volumes,True)
    print(f"Median distance of precipitates (surface-to-surface); {np.median(distances_new[:,0]):.4f}")

    #mean_distance, stdev = calculate_mean(vertices,points,volumes,False)
    distances_new = calculate_distances(distance_list,volumes,False)
    print(f"Mean distance of precipitates (centers); {np.mean(distances_new[:,0]):.4f}; {np.std(distances_new[:,0]):.4f}")
    
    #mean_distance_v, stdev_v = calculate_mean(vertices,points,volumes,True)
    mean_distance_v, stdev_v = calculate_mean_2(vertices,points,volumes,False)
    print(f"Mean distance of precipitates (alternative calculation, centers); {mean_distance_v:.4f}; {stdev_v:.4f}")
    
    n = np.arange(len(d_new))
    d_test = np.array([[x, d_new[x,0], d_new[x,1], d_new[x,2]] for x in n])
    test = np.array([x for x in d_test if x[1]<0])
    plot_figure(distance_list,points,volumes)
    
    #plot_figure_2(test,points,volumes)
    
    plt.show()
    return d_new[:,0]


def plot_dist_statistics(distances,bins):
    fig, axs = plt.subplots()
    axs.hist(distances, bins=bins)
    return fig