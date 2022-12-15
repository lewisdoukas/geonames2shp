import sys, os, time, datetime, warnings, traceback
import pandas as pd
import geopandas as gpd
from pandas.core.common import *
warnings.simplefilter(action="ignore", category= UserWarning)



banner = \
'''
 ___ __ __              ______               __                
|   |  |__.---.-.-----.|   _  \ .-----.--.--|  |--.---.-.-----.
|.  |  |  |  _  |__ --||.  |   \|  _  |  |  |    <|  _  |__ --|
|.  |__|__|___._|_____||.  |    |_____|_____|__|__|___._|_____|
|:  |                  |:  1    /                              
|::.|                  |::.. . /                               
`---'                  `------'  

'''


def create_export_dir():
    now = datetime.datetime.now().strftime("%d-%b-%Y_%H-%M-%S")

    if getattr(sys, "frozen", False):
        currentDirName = os.path.dirname(sys.executable).replace('\\', '/')
    elif __file__:
        currentDirName = os.path.dirname(__file__).replace('\\', '/')

    dir = f"{currentDirName}/GeoNames_txt2shp_{now}"

    dirExists = os.path.isdir(dir)
    if not dirExists:
        os.mkdir(dir)

    return(currentDirName, dir)


def formatTime(processTime):
    if processTime > 60:
        processTime //= 60
        if processTime > 60:
            processTime /= 60
            processTime = f"{round(processTime, 1)} hours"
        else:
            processTime = f"{processTime} minutes"
    else:
        processTime = f"{processTime} seconds"
    return(processTime)


def renameFC(geonameDf):
    fcDct = {
        "A" : "Administrative region",
        "P" : "Populated place",    
        "V" : "Vegetation",
        "L" : "Locality or area",
        "U" : "Undersea", 
        "R" : "Streets, highways, roads, or railroad",
        "T" : "Hypsographic",
        "H" : "Hydrographic" ,
        "S" : "Spot"
    }

    name = fcDct.get(geonameDf['FC'], geonameDf['FC'])
    return(name)


def renameSubFC(geonameDf, subfcDct, exportDir):
    try:
        now = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        subfc = subfcDct.get(geonameDf['DSG'], geonameDf['DSG'])
        return(subfc)

    except Exception as error:
        with open(f"{exportDir}/errors.log", "a", encoding="utf-8") as file:
            file.write(f"✕ {now}: Error with feature {geonameDf['UFI']}: {traceback.format_exc()}\n")


def main():
    """
    This tool generates .shp file from a given .txt file which includes geonames of a particular country.
    Download geonames country .txt files from:
    https://geonames.nga.mil/gns/html/namefiles.html -old
    https://geonames.nga.mil/geonames/GNSData/

    Usage:
    Place inside GeonamesText directory country's .txt file which includes geonames data
    Creates a directory GeoNames_txt2shp_<datetime> where you can find the exported .shp file

    Arguments: 
    <imported_geonames_text(.txt)>   <exported_geonames_shapefile(.shp)>

    Execution: 
    python geonames_txt2shp.py gr.txt greece
    """
    try:
        print(banner)
        
        if len(sys.argv) > 1:
            currentDir, exportDir = create_export_dir()

            txtFname = str(sys.argv[1]) if ".txt" in str(sys.argv[1]) else str(sys.argv[1]) + ".txt"
            txtPath = f"{currentDir}/GeonamesText/{txtFname}" 
            txtExists = os.path.isfile(txtPath)

            if txtExists:

                if len(sys.argv) > 2:
                    shpName = str(sys.argv[2]) if ".shp" in str(sys.argv[2]) else str(sys.argv[2]) + ".shp"
                
                else:
                    shpName = "geonames.shp"

                subfcTxtFname = f"{currentDir}/Subclasses/subfc.txt"
                subfcTxtExists = os.path.isfile(subfcTxtFname)

                if subfcTxtExists:
                    print("\n► Turn geonames .txt to .shp file... Please be patient. . .")
                    start = time.time()

                    # Get all Feature classes and subclasses from  https://www.geonames.org/export/codes.html into a txt file subfc.txt
                    df = pd.read_csv(subfcTxtFname, sep="\t", low_memory= False)
                    df.columns = ["FC", "FEAT", "DESC"]
                    fc = df['FC'].to_list()
                    feat = df['FEAT'].to_list()

                    # Create dictionary with fc : subfc
                    subfcDct = dict(zip(fc, feat))

                    # Columns to drop
                    droplist = ["rk", "lat_dms", "long_dms", "efctv_dt", "term_dt_f", "term_dt_n", "dialect_cd", "cc_ft", "adm1", "mod_dt_ft",
                                "ft_link", "nt", "name_rank", "lang_cd", "transl_cd", "script_cd", "name_link", "cc_nm", "sort_gen", "sort_name", "mod_dt_nm",
                                "gis_notes", "display"]

                    # Read downlaoded txt file and drop columns
                    df = pd.read_csv(txtPath, sep= "\t", low_memory= False).drop(droplist, axis= 1)
                    df = df.rename(columns= {"ufi": "UFI", "uni": "UNI", "generic": "GENERIC", "full_name" : "FULL_NAME", "full_nm_nd": "FULL_NAME_LATIN",
                                             "mgrs": "MGRS", "fc": "FC", "desig_cd": "DSG", "long_dd": "LONG", "lat_dd": "LAT"})

                    df['FEAT_CLASS'] = df.apply(renameFC, axis= 1)

                    # Rename feature sub class based on DSG code
                    df['FEAT_SUB_CLASS'] = df.apply(renameSubFC, axis= 1, args= [subfcDct, exportDir])

                    # Export .shp
                    gdf = gpd.GeoDataFrame(df, geometry= gpd.points_from_xy(df['LONG'], df['LAT'], crs="EPSG:4326")).drop(["FC", "DSG"], axis= 1)
                    gdf.to_file(f"{exportDir}/{shpName}", encoding= "utf8")

                    end = time.time()

                    processTime = round(end - start, 1)
                    processTime = formatTime(processTime)

                    print(f"\n✓ Geonames {shpName} has exported successfully after {processTime}\n")
                    errorExists = os.path.isfile(f"{exportDir}/errors.log")
                    if errorExists:
                        print(f"- For more details please open errors.log file.\n")
            
                else:
                    print("✕ Please place subfc.txt in the Subclasses directory.\n")
            
            else:
                print("✕ There is no such .txt file.\n")
        
        else:
            print("✕ Please input the right arguments:\n<imported_geonames_text(.txt)> <exported_geonames_shapefile(.shp)>")

        # Delete exported directory if is empty
        exportDirItems = os.listdir(exportDir)
        if not exportDirItems:
            os.rmdir(exportDir)

        os._exit(0)


    except Exception as error:
        now = datetime.datetime.now().strftime("%H:%M:%S %d-%m-%Y")
        print(f"\n✕ Failed to execute:\n{error}\n")
        print(f"- For more details please open errors.log file.\n")
        with open(f"{exportDir}/errors.log", "a", encoding="utf-8") as file:
            file.write(f"✕ {now}: {error}\n")
        os._exit(1)


if __name__ == "__main__":
    main()
