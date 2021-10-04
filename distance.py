#Date modified: 13/08/2020, 10:44:32

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import functools
import itertools
import time
import math
from scipy.spatial import Delaunay, ConvexHull
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


def calculate_distances(distance_list,volumes_df,is_surface_to_surface):
    #distance list contains: distance, p1, p2
    df_distances = pd.DataFrame(distance_list,columns=['Distance','P1','P2'])
    #     df_distances.to_csv('distances.csv', index=False)
    df_distances['P1 Key'] = "Cluster " + df_distances['P1'].astype(int).astype(str)
    df_distances['P2 Key'] = "Cluster " + df_distances['P2'].astype(int).astype(str)
    df_distances=df_distances.set_index('P1 Key')
    df_distances = pd.merge(df_distances,volumes_df,left_on='P1 Key',right_on='Cluster',how='inner')
    df_distances.rename(columns={'V_Extent (nm^3) Total\'':'V1'},inplace=True)
    df_distances=df_distances.set_index('P2 Key')
    df_distances = pd.merge(df_distances,volumes_df,left_on='P2 Key',right_on='Cluster',how='inner')
    df_distances.rename(columns={'V_Extent (nm^3) Total\'':'V2'},inplace=True)
    #df_distances=df_distances.set_index('P1')
    df_distances['r1'] =  ((3*df_distances.V1)/(4*3.1415))**(1/3)
    df_distances['r2'] = (((3*df_distances.V2)/(4*3.1415))**(1/3))
    df_distances['distance_sf'] = df_distances.Distance-df_distances.r1-df_distances.r2
    subtractor = 0
    #distances = np.copy(distance_list)
    #When surface to surface is selected (True)
    #calculate the radius of both spheres and subtract them from the distance!
    df_distances.sort_values(by=['distance_sf'],inplace=True)
    #     df_distances.to_csv('df_distances.csv', index=False)
    if is_surface_to_surface:
        return df_distances, df_distances['distance_sf'].values
    return df_distances, df_distances['Distance'].values

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


def create_distance_list(points,vertex_list,volume_list):
    distance_list = np.zeros((len(points),3))
    for x in vertex_list:
        distance = calculate_distance_3D(points[x[0]],points[x[1]])
        if distance_list[x[0],0] > distance or distance_list[x[0],0] == 0:
            distance_list[x[0],0] = distance
            distance_list[x[0],1] = x[0]
            distance_list[x[0],2] = x[1]
        if distance_list[x[1],0] > distance or distance_list[x[1],0] == 0:
            distance_list[x[1],0] = distance
            distance_list[x[1],1] = x[1]
            distance_list[x[1],2] = x[0]
    return distance_list


def plot_figure(distance_list, points, points_all, volumes_all):
    #distance list: [distance, volume, partner]
    fig = plt.figure()
    ax= Axes3D(fig)
    ax.scatter(points_all[:,0],points_all[:,1],points_all[:,2],s=volumes_all)
    for index, row in distance_list.iterrows():
        p1 = int(row['P1'])
        p2 = int(row['P2'])
        x = [points[p1,0],points[p2,0]]
        y = [points[p1,1],points[p2,1]]
        z = [points[p1,2],points[p2,2]]
        ax.plot(x,y,z,color='blue',linestyle='-')
    plt.show()

def calculate_radius(volume):
    return (volume*(3/4)*(1/3.1415))**(1/3)

@timer
def calculate_mean_distance(all_data):
    
    #We want to drop the first line (matrix)
    cluster_data=all_data.drop(index=0)
    cluster_ss = cluster_data [['Cluster','Center_x (nm) Ranged\'','Center_y (nm) Ranged\'','Center_z (nm) Ranged\'','V_Extent (nm^3) Total\'']]
    #Transforming Pandas Data to point list
    points = cluster_ss.values[:,1:4]
    volumes = cluster_ss.values[:,4]
    volumes_df = cluster_ss[['Cluster','V_Extent (nm^3) Total\'']]
    
    #Remove convex hull
    hull = ConvexHull(points)
    hullpoints = hull.simplices.flatten()
    hullpoints = np.unique(hullpoints)
    points_all = points
    volumes_all = volumes
    points = np.delete(points,hullpoints,0)
    volumes = np.delete(volumes,hullpoints,0)
    #if len(points)<4:
    #    print("Not enough points for distance evaluation! A minimum of 4 clusters is required!")
    #return 0
    #Delaunay Triangulation of point list
    tri = Delaunay(points)
    vertices = create_vertex_list(tri.simplices)
    distance_list = create_distance_list(points,vertices,volumes_all)
    #mean_distance_v, stdev_v = calculate_mean(vertices,points,volumes,True)
    df_distance_list, distances_new = calculate_distances(distance_list,volumes_df,True)
    
    plot_figure(df_distance_list, points, points_all, volumes_all.astype(int))
    output = "<table border=0 width=auto>"
    output = output+"<tr><td></td><td>Mean</td><td>Std.Dev.</td><td>Std.Err.</td></tr>"
    output= output + f"<tr><td>Mean distance of precipitates (surface-to-surface)</td><td>{np.mean(distances_new):.4f}</td><td>{np.std(distances_new):.4f}</td><td>{(np.std(distances_new)/np.sqrt(np.size(distances_new))):.4f}</td></tr>"
    d_new = distances_new
        #mean_distance, stdev = calculate_mean(vertices,points,volumes,False)
    df_distance_list, distances_new = calculate_distances(distance_list,volumes_df,False)
    output= output +f"<tr><td>Mean distance of precipitates (centers)</td><td>{np.mean(distances_new):.4f}</td><td>{np.std(distances_new):.4f}</td><td>{(np.std(distances_new)/np.sqrt(np.size(distances_new))):.4f}</td></tr>"
    output = output + "</table>"
    return output


def plot_dist_statistics(distances,bins):
    fig, axs = plt.subplots()
    axs.hist(distances, bins=bins,edgecolor='white')
    return fig