# Read srtm data files and put them in the database.
import pg
from osgeo import gdal, gdal_array
import database 
import sys

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
  
def connectToDatabase(database):
    return pg.DB(dbname=database.db,host='localhost', user=database.db_user, passwd=database.db_pass)
      

def dropAllTables(db):
    db.query("DROP TABLE IF EXISTS altitude;")

def checkDatabaseEmpty(db):
    # Test is the test database is as we expect it after setUp:
    return db.get_tables() == ['information_schema.sql_features', 'information_schema.sql_implementation_info', 'information_schema.sql_languages', 'information_schema.sql_packages', 'information_schema.sql_parts', 'information_schema.sql_sizing', 'information_schema.sql_sizing_profiles', 'public.geometry_columns', 'public.spatial_ref_sys']

db = connectToDatabase(database) 

# Does the user want to empty the database first?
if 'empty' in sys.argv:
  print "Deleting tables from databse..." 
  dropAllTables(db)
  print "Done..."

# Make sure the database is empty before we start:
if not checkDatabaseEmpty(db):
  print "Database is not empty. Run 'read_data empty' to empty it first."
  exit()

createTableAltitude(db)
