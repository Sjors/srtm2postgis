# Downloads the SRTM data for Australia

# Import some libraries:
from ftplib import FTP
import urllib
import re
import sys

def handleDownload(block):
    file.write(block)
    print ".",

def getLatLonFromFileName(name):
  # Split up in lat and lon:
  p = re.compile('[NSEW]\d*')
  [lat_str, lon_str] = p.findall(name)

  # North or south?
  if lat_str[0] == "N":
    lat = int(lat_str[1:])
  else: 
    lat = -int(lat_str[1:])
  
  # East or west?
  if lon_str[0] == "E":
    lon = int(lon_str[1:])
  else: 
    lon = -int(lon_str[1:])

  return [lat,lon]

def main():
    # First we make a list of all files that need to be download. This depends
    # on the arguments given to the program.
    # The first argument should be the continent:
    # * Africa  
    # * Australia  
    # * Eurasia  
    # * Islands  
    # * North_America  
    # * South_America    

    if len(sys.argv) > 1:
        continent = sys.argv[1]
        if not continent in ["Africa", "Australia", "Eurasia",  "Islands", "North_America", "South_America"]:
            print "First argument should be Africa, Australia, Eurasia, Islands, North_America or South_America."
            exit()
    else:
        print "Please provide arguments \n",\
        "First argument should be Africa, Australia, Eurasia, Islands, North_America or South_America.\n",\
        "Second argument (optional) specifies from which tile to resume. Use full file name e.g. \n",\
        "'N36W004.hgt.zip'. Set to 0 start at the first file. \n",\
        "Argument 3-6 optionally specify a bounding box: north, south, west, east"
        exit()
        
    # First we get the list of files through an FTP connection.
    ftp = FTP('e0srp01u.ecs.nasa.gov')

    ftp.login()

    ftp.cwd("srtm/version2/SRTM3/" + continent)

    # Now list all tiles of that continent.
    # See ftp://e0srp01u.ecs.nasa.gov/srtm/version2/SRTM3/[continent]/
    
    files = ftp.nlst()
    
    # And close connection.
    
    ftp.close()

    print len(files)
    exit()
    
    # Now download all files using urllib.urlretrieve
    
    # Determine if we need to resume at a certain point
    if(len(sys.argv) > 1):
        resume = argv[1]
        skip = True     

    # Do we have a bounding box?
    if len(sys.argv) == 6:
        north = sys.argv[2]
        south = sys.argv[3]
        west = sys.argv[4]
        east = sys.argv[5]
    else:
        north = 90
        south = -90
        east = -180
        west = 180
    
    for i in range(len(files)):
      if skip:
          if files[i] == resume:
              skip = False
          
      if not(skip):
          [lat,lon] = getLatLonFromFileName(files[i])
          if(south <= lat and lat <=north and west <= lon and lon <= east):
            print "Downloading " + files[i] + " (lat = " + str(lat)  + " , lon = " + str(lon) + " )... (" + str(i + 1) + " of " + str(len(files)) +")"
            urllib.urlretrieve("ftp://e0srp01u.ecs.nasa.gov/srtm/version2/SRTM3/Eurasia/" + files[i],"data/" + continent + "/" + files[i])
            
if __name__ == '__main__':            
    main()
