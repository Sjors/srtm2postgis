# Read srtm data files and put them in a Postgres database.
import pg, psycopg2
import database_pg 

import re
import sys

from math import sqrt
from read_data import verify, posFromLatLon, loadTile

from data import files
from data import util
  

class DatabasePg:
  def __init__(self, db_name, db_user, db_pass):
    self.db = pg.DB(dbname=db_name,host='localhost', user=db_user, passwd=db_pass)

  def dropAllTables(self):
      self.db.query("DROP TABLE IF EXISTS altitude;")

  def createTableAltitude(self):
    tables = self.db.get_tables()
      
    if not('public.altitude' in tables): 
      self.db.query(" \
        CREATE TABLE altitude ( \
          pos bigint NOT NULL, \
          alt int NULL , \
          PRIMARY KEY ( pos ) \
        ); \
      ")
    return True

  def fetchTopLeftAltitude(self, lat, lon):
    pos = posFromLatLon(lat,lon)
    sql = self.db.query(" \
      SELECT \
        alt \
      FROM altitude \
      WHERE \
        pos = " + str(pos) + "\
     ")
    return int(sql.getresult()[0][0])

  def checkDatabaseEmpty():
      # Test is the test database is as we expect it after setUp:
      return self.db.get_tables() == ['information_schema.sql_features', 'information_schema.sql_implementation_info', 'information_schema.sql_languages', 'information_schema.sql_packages', 'information_schema.sql_parts', 'information_schema.sql_sizing', 'information_schema.sql_sizing_profiles', 'public.geometry_columns', 'public.spatial_ref_sys']

  def readTile(self, lat0, lon0):
    # Calculate begin and end position
    begin = posFromLatLon(lat0,lon0)
    end = posFromLatLon(lat0 + 1, lon0 + 1)
    sql = self.db.query(" \
      SELECT \
        alt \
      FROM altitude \
      WHERE \
        pos >= " + str(begin) + "\
        AND pos < " + str(end) + "\
      ORDER BY pos ASC \
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
        
  def getTables(self):
    return self.db.get_tables()


class DatabasePsycopg2:
  def __init__(self, db_name, db_user, db_pass):
    self.db_name = db_name

    conn = psycopg2.connect("dbname='" + db_name + "' host='localhost' user='" + db_user + "' password='" + db_pass + "'")
    self.cursor = conn.cursor()

  def insertTile(self, tile, lat0, lon0):
    # I use the Psycopg2 connection, with its copy_to and 
    # copy_from commands, which use the more efficient COPY command. 
    # This method requires a temporary file.

    # Calculate begin position
    begin = posFromLatLon(lat0,lon0)

    # First we write the data into a temporary file.
    f = open('/tmp/tempcopy', 'w')
    # We drop the top row and right column.
    for row in range(1, len(tile)):
      for col in range(0, len(tile) - 1):
        f.write(str(\
        begin + (row-1) * 1200 + col\
        ) + "\t" + str(tile[row][col] ) + "\n")

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

    p = subprocess.Popen('psql ' + self.db_name +  ' -c "COPY altitude FROM STDIN;"', stdin=f, shell=True);
    p.wait()

    f.close
  
def main():
  db_pg = DatabasePg(database_pg.db, database_pg.db_user, database_pg.db_pass)
  db_psycopg2 = DatabasePsycopg2(database_pg.db, database_pg.db_user, database_pg.db_pass)

  try:
      continent = sys.argv[1]
      
  except: 
      print "Please specify the continent. Africa, Australia, Eurasia, Islands, North_America or South_America."

  # Does the user want to empty the database?
  if 'empty' in sys.argv:
    print "Deleting tables from databse..." 
    db_pg.dropAllTables()
    print "Done..."
    exit()

  [north, south, west, east] = util.getBoundingBox(sys.argv, 3)
      
  files_hashes = util.getFilesHashes(continent)
  
  number_of_tiles = util.numberOfFiles(files_hashes, north, south, west, east)
  
  # Verify result?
  if 'verify' in sys.argv:
    verify(db_pg, number_of_tiles, files_hashes, continent,  north, south, west, east)

  # If a tile name is given as the second argument it will resume from there.
  p = re.compile('[NSEW]\d*')
  resume_from = ""
  try:
    if(p.find(sys.argv[2])):
      resume_from = sys.argv[2]
      
  except: 
    None
    
  db_pg.createTableAltitude()

  i = 0

  for file in files_hashes:
    # Strip .hgt.zip extension:
    file = file[1][0:-8] 
    # Get latitude and longitude from file name 
    [lat,lon] = util.getLatLonFromFileName(file)
    
    if util.inBoundingBox(lat, lon, north, south, west, east):
      i = i + 1
  
      # Are we resuming?
      if resume_from == file:
        resume_from = "" 
      
      if resume_from == "":

        # Load tile from file
        tile = loadTile(continent, file)

        # First check if the tile is not already in the database:

        try:
          db_pg.fetchTopLeftAltitude(lat, lon)
          print("Skipping tile " + file + " (" + str(i) + " / " + str(number_of_tiles) + ") ...")

        except:
          print("Insert data for tile " + file + " (" + str(i) + " / " + str(number_of_tiles) + ") ...")

          db_psycopg2.insertTile(tile, lat, lon)

  print("All tiles inserted. Pleasy verify the result with python \
  read_data.py verify")


if __name__ == '__main__':
  main()
