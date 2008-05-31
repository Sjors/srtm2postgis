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
      self.assertEqual(data.size,1201*1201)
    
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

class TestDatabase(unittest.TestCase):
  def setUp(self):
    self.db = connectToDatabase(database_test)
    # Drop all tables
    dropAllTables(self.db);

  def testDatabasePresent(self):
    # Already tested in setUp()
    self.assert_(True)

  def testDatabaseEmpty(self):
    self.assert_(checkDatabaseEmpty(db))
  
  def testTableAltitudeExists(self):
    # Call function to create table
    createTableAltitude(self.db)

    tables = self.db.get_tables()
    
    self.assert_('public.altitude' in tables) 

  def tearDown(self):
    # Drop all tables that might have been created:
    dropAllTables(self.db);

if __name__ == '__main__':
    unittest.main()
