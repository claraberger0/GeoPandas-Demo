import geopandas as gpd
import pandas as pd
import time
import shapely.speedups
shapely.speedups.enable()
import numpy as np

import multiprocessing as mp
import itertools

from katana import katana

''' -----------------------split large polygons into smaller polygons to improve runtime-----------------------
'''
def splithazard(hazard_raw, threshold):
    start_time = time.time()
    hazard_split = gpd.GeoDataFrame()  
 
    for poly in hazard_raw.geometry:
        # The FEMA data multi polygons are comprised of smaller polygons that we have to split individually
        try:
            if len(poly)> 1:
                for j in range(len(poly)):
                    hazard_split = hazard_split.append(katana(poly[j],threshold,count=0)) #use the katana funtion from katana.py to iteratively split each polygon
            else:
                hazard_split = hazard_split.append(katana(poly,threshold,count=0))  # sets the threshold of how small the width of each box should be 
        except:
            hazard_split = hazard_split.append(katana(poly,threshold,count=0))  

    hazard_split = hazard_split.reset_index()

    print("split in chunks--- %s seconds ---" % (time.time() - start_time))
    
    return hazard_split

''' -----------------------a function to run the splithazard function over multiple CPU cores-----------------------
'''
def splithazard_multi(hazard_raw,threshold):
    # find the number of cpus on the computer
    cpus = mp.cpu_count()

    start_time1 = time.time()
    # add a new column where you approximately compute the area of the polygon 
    # this will allow us to find the biggest polygons and split them onto different cores
    hazard_raw = hazard_raw.to_crs(epsg=2957) # briefly changing to a projected CRS to compute area
    hazard_raw.loc[:,'area'] = hazard_raw.geometry.area  # adding an area column
    hazard_sort = hazard_raw.sort_values(by = 'area', ascending = False)  # sort the data frame so that the biggest polygons are first
    hazard_sort = hazard_sort.to_crs(epsg=4269) #back to geographic CRS

    # break the dataframe into N dataframes based on # of CPUs and split up the list of polygons to get N lists of appx equal load
    hazard_divided_cpu = [hazard_sort[i::cpus] for i in range(cpus)]    
    print("divide hazard based on cpus--- %s seconds ---" % (time.time() - start_time1))   

    #start the pool processing for the numpuer of cpus on the computer
    pool = mp.Pool(processes=cpus)

    # each core has to take 2 inputs as an iterable, so zip the list of dataframes with the threshold desired
    hazard_split_input = zip(hazard_divided_cpu, itertools.repeat(threshold))

    # split the splithazard function over the cpu cores with the zipped input
    hazard_split = pool.starmap(splithazard, hazard_split_input)

    start_time2 = time.time()
    #each core will return a "hazard_split" so join all of the results in a dataframe 
    all_hazard_split =  gpd.GeoDataFrame( pd.concat( hazard_split, ignore_index=True) , crs = "EPSG:4269" )

    print("concat all split hazards--- %s seconds ---" % (time.time() - start_time2))   

    return all_hazard_split

''' -----------------------ientify establishment points that are within the hazard zone by "matching" the points to the polygons---------
'''
def findpointmatches(estab_points, hazard_split):
    #take the points from the establishment data and create a spatial index for those points
    points = estab_points['geometry'] 
    estab_sindex = points.sindex

    start_time4 = time.time()
    #set up the geodataframe
    points_within_geometry = gpd.GeoDataFrame(columns= estab_points.columns)
    points_within_geometry = points_within_geometry.set_crs("EPSG:4269") #keep all the coordinates the same

    #to speed up the process, go through each sub-polygon and look for matches
    for poly in hazard_split.geometry: 
        # find approximate matches with r-tree, then precise matches from those approximate ones
        possible_matches_index = list(estab_sindex.intersection(poly.bounds))
        possible_matches = estab_points.iloc[possible_matches_index]
        possible_pip_mask = possible_matches.within(poly)
        precise_matches = possible_matches.loc[possible_pip_mask] 
        points_within_geometry = points_within_geometry.append(precise_matches)

    print("identify point matches--- %s seconds ---" % (time.time() - start_time4))

    return points_within_geometry

'''----------------------- a function to run the findpointmatches function over multiple CPU cores-----------------------
'''
def findpointmatches_multi(estab_points, hazard_split):
    #take the points from the establishment data and create a spatial index for those points
    points = estab_points['geometry'] 
    estab_sindex = points.sindex
    
    #intersect the spatial index of the establishments with the bounds of the total polyon to cut down the number of establishments to those that are in th area of the hazard
    possible_estab_index = list(estab_sindex.intersection(hazard_split.total_bounds))
    possible_estab = estab_points.iloc[possible_estab_index]

    # find the number of cpus on the computer
    cpus = mp.cpu_count()

    # split the establishment dataframe into N sections where N is the number of cpus
    estab_split = np.array_split(possible_estab,cpus)
        
    #start the pool processing for the numpuer of cpus on the computer
    pool = mp.Pool(processes=cpus)
    
    # zip each of the N sections of the establishments with the split hazard
    estab_split_input = zip(estab_split, itertools.repeat(hazard_split.geometry))
    
    # map the findpointmatches function with the input above to each of the cpus
    precise_matches = pool.starmap(findpointmatches,estab_split_input)

    start_time5 = time.time()
    # concatenate the N lists of points found by each processor
    all_points_within_geometry =  gpd.GeoDataFrame( pd.concat( precise_matches, ignore_index=True) , crs = "EPSG:4269" )

    print("concat all point matches--- %s seconds ---" % (time.time() - start_time5))   
    return all_points_within_geometry

