# Read an srtm data file and turn it into an csv file

from osgeo import gdal, gdal_array
import sys
import re
from math import sqrt

# Main functions

def loadTile(filename):
  srtm = gdal.Open('data/Eurasia/' + filename + '.hgt')
  return gdal_array.DatasetReadAsArray(srtm)

def posFromLatLon(lat,lon):
  return (lat * 360 + lon) * 1200 * 1200

def writeTileCsvFile(tile, lat0, lon0, top_row = 1, bottom_row = 1200, left_col = 0, right_col = 1199 ):
  # Calculate begin position
  begin = posFromLatLon(lat0,lon0)

  # First we write the data into a temporary file.
  f = open('data/tile.csv', 'w')
  # We drop the top row and right column.
  for row in range(top_row, bottom_row + 1 ):
    for col in range(left_col, right_col + 1):
      f.write(str(\
      begin + (row-1) * 1200 + col\
      ) + ", " + str(tile[row][col] ) + "\n")

  f.close() 

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

if __name__ == '__main__':
  # We will only upload 1 tile to the Google App Engine. This will take quite 
  # a bit of time. For the offline data store, we will only "upload" the city 
  # of Heidelberg; the offline data store is very slow.
  
  # For this we need tile N49E008. 
  name = "N49E008"
  tile = loadTile(name)
  [lat,lon] = getLatLonFromFileName(name)

  if not ("online" in sys.argv or "offline" in sys.argv):
      print "Online or offline?"
      exit()
  
  if sys.argv[1] == "offline":
      # If we are offline, we'll only look the center of Heidelberg.
      # 49.39 --- 49.42
      # 8.67 --- 8.71
      # That corresponds to:
      row_top = int((1.0 - 0.42) * 1200.)
      row_bottom = int((1.0 - 0.39) * 1200.)
      col_left = int(0.67 * 1200.)
      col_right = int(0.71 * 1200.)
      # So that 1813 records
      writeTileCsvFile(tile, lat, lon, row_top, row_bottom, col_left, col_right)
      print "Now run this command to insert the data into your local datastore:"
      print "/path/to/app-engine-sdk/bulkload_client.py --filename ../data/tile.csv --kind Altitude --url http://localhost:8080/load --batch_size 100 --cookie 'dev_appserver_login=test@example.com:True'"

  else:
      # Because the bulk upload script does not support resume, we will upload
      # the data row by row. sys.argv[2] represents the line number to insert.
      # You should create a script to perform the upload. Start at 1, end at 1200.
      row = int(sys.argv[2])
      print "About to make csv for row " + str(row) + " of 1200..."
      row_top = row
      row_bottom = row
      col_left = 0
      col_right = 1199
      writeTileCsvFile(tile, lat, lon, row_top, row_bottom, col_left, col_right)

      # To insert, you need to do something like this:
      # /path/to/app-engine-sdk/bulkload_client.py --filename data/tile.csv --kind Altitude --url http://something.appspot.com/load --batch_size 100"
      
      # You also need to add a --cookie argument: just surf to http://something.appspot.com/load
      # to see how.
