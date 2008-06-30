# Downloads the SRTM data for Australia
#
# Loosely based on example at:
# http://postneo.com/stories/2003/01/01/beyondTheBasicPythonFtplibExample.html

# Import some libraries:
from ftplib import FTP
import urllib
import re

# First we get the list of files through an FTP connection.

ftp = FTP('e0srp01u.ecs.nasa.gov')

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

ftp.login()

ftp.cwd("srtm/version2/SRTM3/Eurasia")
#ftp.cwd("srtm/version2/SRTM3/Australia")

# Now list all Australian tiles.
# See ftp://e0srp01u.ecs.nasa.gov/srtm/version2/SRTM3/Australia/

# List all files (should be 1060)
files = ftp.nlst()

# And close connection.

ftp.close()

# Now download all files using urllib.urlretrieve

for i in range(len(files)):
  [lat,lon] = getLatLonFromFileName(files[i])
  # Only download if in Germany or NL:
  #  if(47 <= lat and lat <=54 and 0 <= lon and lon <= 16):
  #  if(51 <= lat and lat <=51 and 8 <= lon and lon <= 16):
  if(53 <= lat and lat <=54 and 0 <= lon and lon <= 16):
    print "Downloading " + files[i] + " (lat = " + str(lat)  + " , lon = " + str(lon) + " )... (" + str(i + 1) + " of " + str(len(files)) +")"
    urllib.urlretrieve("ftp://e0srp01u.ecs.nasa.gov/srtm/version2/SRTM3/Eurasia/" + files[i],"data/Eurasia/" + files[i])
    #urllib.urlretrieve("ftp://e0srp01u.ecs.nasa.gov/srtm/version2/SRTM3/Australia/" + files[i],"data/Australia/" + files[i])

