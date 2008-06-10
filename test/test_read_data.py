import sys
import os
import pg

import unittest
sys.path += [os.path.abspath('.')]
import database_test 

from read_data import *

class TestImportScript(unittest.TestCase):
    def testPointsPerTile(self):
      data = loadTile('S11E119')
      self.assertEqual(len(data) * len(data[0]),1201*1201)
    
    def testFirstNumber(self):
      data = loadTile('S11E119')
      self.assertEqual(data[0][0],0)

    def testTileIntegrity(self):
      # The sum of altitudes of all 1201*1201 points in two tiles
     
       # Melbourne (West):
      west = loadTile("S37E144")
      self.assertEqual(west.sum(),223277342)

      ## Melbourne (East):
      east = loadTile("S37E145")
      self.assertEqual(east.sum(), 271136709)
    
    def testTileOverlap(self):
      # Uses two adjecant tiles around Melbourne to test
      # * Eastern edge of West Melbourne tile should be the same as 
      #   western edge of East Melbourne tile.
      
      # Melbourne (West):
      west = loadTile("S37E144")

      ## Melbourne (East):
      east = loadTile("S37E145")

      for i in range(1201):
        self.assertEqual(west[i][1200] - east[i][0],0) 

      # Also try for north - south boundary:
      north = loadTile("S36E144")
      south = loadTile("S37E144")
      
      for i in range(1201):
        self.assertEqual(north[1200][i] - south[0][i],0) 

      # Some other area north - south boundary:
      south = loadTile("S33E147")
      north = loadTile("S32E147")

      for i in range(1201):
        self.assertEqual(north[1200][i] - south[0][i],0) 

      # Some other area west - east boundary:
      west = loadTile("S33E147")

      ## Melbourne (East):
      east = loadTile("S33E148")

      for i in range(1201):
        self.assertEqual(west[i][1200] - east[i][0],0) 


class TestDatabase(unittest.TestCase):
  def setUp(self):
    self.db = connectToDatabase(database_test)
    # Drop all tables
    dropAllTables(self.db);

  def testDatabasePresent(self):
    # Already tested in setUp()
    self.assert_(True)

  def testDatabaseEmpty(self):
    self.assert_(checkDatabaseEmpty(self.db))
  
  def testTableAltitudeExists(self):
    # Call function to create table
    createTableAltitude(self.db)

    tables = self.db.get_tables()
    
    self.assert_('public.altitude' in tables) 

  def testGetLatLonFromFileName(self):
    self.assertEqual([-11,119], getLatLonFromFileName("S11E119"))
    self.assertEqual([11,119], getLatLonFromFileName("N11E119"))
    self.assertEqual([11,-119], getLatLonFromFileName("N11W119"))
    self.assertEqual([-11,-119], getLatLonFromFileName("S11W119"))

  def testPosFromLatLon(self):
    self.assertEqual(posFromLatLon(0,0),0) 
    self.assertEqual(posFromLatLon(0,1),1200*1200) 
    self.assertEqual(posFromLatLon(0,2),1200*1200*2) 
    self.assertEqual(posFromLatLon(1,0),1200*1200*360) 
    self.assertEqual(posFromLatLon(0,-1),-1200*1200) 
    self.assertEqual(posFromLatLon(-37,145),(-37 * 360 + 145) * 1200 * 1200) 
  
  def testInsertTileIntoDatabase(self):
    # Create table
    self.assert_(createTableAltitude(self.db))
    # Load example tile
    tile = loadTile('S37E145')
    tile = tile[0:11][0:11]
    # Get lat and lon from filename
    [lat,lon] = getLatLonFromFileName("S37E145")

    # Make the tile smaller, so this will be faster:
    # 11x11 tile: because the top row and right column are dropped,
    # only the bottom-left 10x10 tile will be stored in the
    # database.

    # Insert tile into database
    # We use psycopg2 for the connection in this case.
    db_psycopg2 = connectToDatabasePsycopg2(database_test)
    insertTileIntoDatabase(db_psycopg2, "srtm_test" , tile, lat, lon)

    # Check if the tile is indeed in the database
    tile_back = readTileFromDatabase(self.db, lat, lon)
    for i in range(len(tile) - 1):
      for j in range(len(tile) - 1):
        self.assert_(tile_back[i][j] == tile[i+1][j])

  def tearDown(self):
    # Drop all tables that might have been created:
    dropAllTables(self.db);

if __name__ == '__main__':
    unittest.main()
