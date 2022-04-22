# GeoPandas-Demo

See the Jupyter Notebook for a brief overview of the GeoPandas library for Python and a demonstration of how we used its capabilities for a project. 

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


The __katana.py__ file contains the function katana used to split shapefiles up based on a user defined threshold.
https://snorfalorpagus.net/blog/2016/03/13/splitting-large-polygons-for-faster-intersections/
Copyright (c) 2016, Joshua Arnott
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
