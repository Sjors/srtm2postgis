import unittest
from osgeo import gdal, gdal_array

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

def loadTile(filename):
  srtm = gdal.Open('../data/Australia/' + filename + '.hgt')
  return gdal_array.DatasetReadAsArray(srtm)

if __name__ == '__main__':
    unittest.main()
