# geonames2shp
This tool generates .shp file from a given .txt file which includes the geonames of a particular country.  

Download geonames country .txt files from:
[Geonames NGA](https://geonames.nga.mil/geonames/GNSData)

# Installation
Python version 3.8.5 >= is required.  

`pip3 install -r requirements.txt`  

# Usage
Place inside GeonamesText directory country's .txt file which includes the geonames data.   

# Arguments
`<imported_geonames_text(.txt)>   <exported_geonames_shapefile(.shp)>`  

# Execution
`python geonames_txt2shp.py gr.txt greece`  
  
# Output
The tool creates a directory GeoNames_txt2shp_<datetime> where you can find the exported .shp file.  
