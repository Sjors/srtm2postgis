# Read srtm data files and put them in the database.
import pg, psycopg2
from osgeo import gdal, gdal_array
import database 
import sys
import re
from math import sqrt

# Main functions

def loadTile(filename):
  srtm = gdal.Open('data/Australia/' + filename + '.hgt')
  return gdal_array.DatasetReadAsArray(srtm)

def createTableAltitude(db):
  db.query(" \
    CREATE TABLE altitude ( \
      lat double precision NOT NULL, \
      lon double precision NOT NULL, \
      alt double precision NULL , \
      PRIMARY KEY ( lat, lon ) \
    ); \
  ")
  return True
  
def connectToDatabase(database):
    return pg.DB(dbname=database.db,host='localhost', user=database.db_user, passwd=database.db_pass)
      
def connectToDatabasePsycopg2(database):
    conn = psycopg2.connect("dbname='" + database.db + "' host='localhost' user='" + database.db_user + "' password='" + database.db_pass + "'")
    return conn.cursor()
      

def dropAllTables(db):
    db.query("DROP TABLE IF EXISTS altitude;")

def checkDatabaseEmpty(db):
    # Test is the test database is as we expect it after setUp:
    return db.get_tables() == ['information_schema.sql_features', 'information_schema.sql_implementation_info', 'information_schema.sql_languages', 'information_schema.sql_packages', 'information_schema.sql_parts', 'information_schema.sql_sizing', 'information_schema.sql_sizing_profiles', 'public.geometry_columns', 'public.spatial_ref_sys']

def insertTileIntoDatabase(cur, db_name, tile, lat0, lon0):
  # I use the Psycopg2 connection, with its copy_to and 
  # copy_from commands, which use the more efficient COPY command. 
  # This method requires a temporary file.
  
  # First we write the data into a temporary file.
  f = open('/tmp/tempcopy', 'w')
  for row in range(len(tile) - 1):
    for col in range(len(tile) - 1):
      f.write(str(lat0 - float(row)/1200.) + "\t" + str(lon0 + float(col)/1200.) + "\t" + str(tile[row][col] ) + "\n")
  

  f.close() 

  # Now we read the data from the temporary file and put it in the
  # altitude table.

  f = open('/tmp/tempcopy', 'r')
  #cur.copy_from(f, 'altitude') 
  
  # Unfortunately the copy_from() command hangs on my computer for
  # some reason, so we try something else. See also:
  # http://lists.initd.org/pipermail/psycopg/2007-October/005684.html

  import subprocess

  #psqlcmd = os.path.join('c:\\', 'Program Files', 'PostgreSQL', '8.2',
  #'bin', 'psql')
  
  psqlcmd = "/usr/bin/psql"

  p = subprocess.Popen('psql ' + db_name +  ' -c "COPY altitude FROM STDIN;"', stdin=f, shell=True);
  p.wait()

  f.close
        
def readTileFromDatabase(db, lat0, lon0):
  sql = db.query(" \
    SELECT \
      alt \
    FROM altitude \
    WHERE \
      lat <= " + str(lat0) + "\
      AND lat > " + str(lat0 -1) + "\
      AND lon >= " + str(lon0) + "\
      AND lon < " + str(lon0 + 1) + "\
    ORDER BY lat DESC, lon ASC \
  ")
  res = sql.getresult()
  
  # Now turn the result into a 2D array

  tile = []
  
  # Calculate tile width (should be 1200, or 10 for test tiles)
  tile_width = int(sqrt(len(res)))
  i = 0
  for x in range(tile_width):
    row = []
    for y in range(tile_width):
      row.append(int(res[i][0]))
      i = i + 1

    tile.append(row)
  
  return tile
        
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
  db = connectToDatabase(database) 
  import verify_download

  # Verify result?
  if 'verify' in sys.argv:
    # For every tile, verify the top left coordinate.
    for file in verify_download.files_hashes:
      # Strip .hgt.zip extension:
      file = file[1][0:-8] 

      [lat,lon] = getLatLonFromFileName(file)

      # Get top left altitude from file:
      coordinate_file = loadTile(file)[0][0]

      # Get top left altitude from database:
      sql = db.query(" \
        SELECT \
          alt \
        FROM altitude \
        WHERE \
          lat = " + str(lat) + "\
          AND lon = " + str(lon) + "\
      ")
      coordinate_db = int(sql.getresult()[0][0])
      
      if coordinate_db != coordinate_file:
        print "Mismatch tile " + file[1]
        exit() 

    # Check the total number of points in the database:
    sql = db.query("SELECT count(*) FROM altitude")
    total = int(sql.getresult()[0][0])
    if not total == len(verify_download.files_hashes) * 1200 * 1200:
      print "Not all tiles have been (completely) inserted!"
      exit()
        
    print "All tiles seem to have made it into the database! Enjoy."

    exit()

  # Does the user want to empty the database?
  if 'empty' in sys.argv:
    print "Deleting tables from databse..." 
    dropAllTables(db)
    print "Done..."
    exit()

  # Make sure the database is empty before we start:
  if not checkDatabaseEmpty(db):
    print "Database is not empty. Run 'read_data empty' to empty it first."
    exit()
  
  # Second database connection with psychopg2 
  db_psycopg2 = connectToDatabasePsycopg2(database)

  createTableAltitude(db)

  i = 0
  for file in verify_download.files_hashes:
    i = i + 1
    # Strip .hgt.zip extension:
    file = file[1][0:-8] 
    # Get latitude and longitude from file name 
    [lat,lon] = getLatLonFromFileName(file)
    # Load tile from file
    tile = loadTile(file)

    print("Insert data for tile " + file + " (" + str(i) + " / " + str(len(verify_download.files_hashes)) + ") ...")

    insertTileIntoDatabase(db_psycopg2, "srtm" , tile, lat, lon)

  print("All tiles inserted. Pleasy verify the result with python \
  read_data.py verify")

