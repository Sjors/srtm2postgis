import files
import re

def getFilesHashes(continent):
    if continent == 'Australia': files_hashes = files.Australia
    if continent == 'Eurasia': files_hashes = files.Eurasia
    if continent == 'Africa': files_hashes = files.Africa
    if continent == 'Islands': files_hashes = files.Islands
    if continent == 'North_America': files_hashes = files.North_America
    if continent == 'South_America': files_hashes = files.South_America
    return files_hashes
  
def numberOfFiles(file_list, north, south, west, east):
  i = 0 
  for file in file_list:
    # Strip .hgt.zip extension:
    file = file[1][0:-8] 
    # Get latitude and longitude from file name 
    [lat,lon] = getLatLonFromFileName(file)
    
    if inBoundingBox(lat, lon, north, south, west, east):
      i = i + 1
      
  return i


def getBoundingBox(sysargv, offset):
  try:
    north = int(sysargv[offset])
    south = int(sysargv[offset + 1])
    west = int(sysargv[offset + 2])
    east = int(sysargv[offset + 3])
    print "Bounding box " + str(south) + " <= lat <= " + str(north) + " and " +  str(west) + " <= lon <= " + str(east) + "."  

  except:
    north = 90
    south = -90
    west = -180
    east = 180
    
  return [north, south, west, east]

def inBoundingBox(lat,lon, north, south, west, east):
  return (lat <= north and lat >= south and lon >= west and lon <= east)

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

def verifyIsContinent(continent):
  if not continent in ["Africa", "Australia", "Eurasia",  "Islands", "North_America", "South_America"]:
    print "First argument should be Africa, Australia, Eurasia, Islands, North_America or South_America."
    exit()
