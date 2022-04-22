# GeoPandas-Demo
Below is a description of the functions found in the spatial_analysis_function.py file. These functions may be used to speed up spatial intersections.

__splithazard__(*hazard_raw, threshold*): this function uses the katana function written in the katana.py file to take the large polygons included in the various hazard files and splits them into smaller polygons to speed up the analysis. Returns a geodataframe of the smaller polygons.
- *hazard_raw* is the shapefile from the SLR, FEMA, or tsunami geodatabase
- *threshold* defines how small to split the polygons, see the katana.py file for further description of this function. ERG experimented with the threshold to find the level that would result in the fastest runtime based on the polygons. Varying thresholds will not change the outputs.

__splithazard_multi__(*hazard_raw, threshold*): this function splits the hazard geometry into N dataframes, where N is the number of CPUs on the user’s computer. Then the splithazard function is split over N CPUs to run simultaneously.
- This function takes the same inputs as the splithazard function and may be used inplace for improved performance on a case by case basis.

__findpointmatches__(*estab_points, hazard_split*): this function intersects the establishment points with each of the split polygons. Returns a geodataframe with only the establishments that are in the hazard polygons.
- *estab_points* is a dataframe of establishments with the point locations
- *Hazard_split* is a dataframe of small split up hazard polygons.

__findpointmatches_multi__(*estab_points, hazard_split*): this function splits the establishment points dataframe into N dataframes, where N is the number of CPUs on the  user’s computer. Then the findpointmatches function is split over N CPUs to run simultaneously.
- This function takes the same inputs as the findpointmatches function and may be used inplace for improved performance on a case by case basis.
