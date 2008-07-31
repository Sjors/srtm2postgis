# Read srtm data files and put them in the database.
from osgeo import gdal, gdal_array
import os

import re
import zipfile

from data import util

# Main functions

def loadTile(continent, filename):
  # Unzip it
  zf = zipfile.ZipFile('data/' + continent + '/' + filename + ".hgt.zip")
  for name in zf.namelist():
    outfile = open('data/' + continent + '/' + name, 'wb')
    outfile.write(zf.read(name))
    outfile.flush()
    outfile.close()
  
  # Read it
  srtm = gdal.Open('data/' + continent + '/' + filename + '.hgt')
  
  # Clean up
  os.remove('data/' + continent + '/' + filename + '.hgt')
  
  return gdal_array.DatasetReadAsArray(srtm)

def connectToDatabasePsycopg2(database):
    conn = psycopg2.connect("dbname='" + database.db + "' host='localhost' user='" + database.db_user + "' password='" + database.db_pass + "'")
    return conn.cursor()

def posFromLatLon(lat,lon):
  return (lat * 360 + lon) * 1200 * 1200

def verify(db, number_of_tiles, files_hashes, continent, north, south, west, east):
    # For every tile, verify the bottom left coordinate.
    for file in files_hashes:
      # Strip .hgt.zip extension:
      file = file[1][0:-8] 
    
      [lat,lon] = util.getLatLonFromFileName(file)
      
      # Only a smaller part of Australia (see below):
      if util.inBoundingBox(lat, lon, north, south, west, east):
      
        print "Verify " + file + "..." 
    
        # Get top left altitude from file:
        coordinate_file = loadTile(continent, file)[1][0]
    
        # Get top left altitude from database:
        coordinate_db = db.fetchTopLeftAltitude(lat,lon)
        
        if coordinate_db != coordinate_file:
          print "Mismatch tile " + file[1]
          exit() 
    
    # Check the total number of points in the database:
    
    print "Check the total number of points in the database..."
    
    sql = db.query("SELECT count(pos) FROM altitude")
    total = int(sql.getresult()[0][0])
    if not total == number_of_tiles * 1200 * 1200:
      print "Not all tiles have been (completely) inserted!"
      exit()
        
    print "All tiles seem to have made it into the database! Enjoy."
    
    exit()

