from struct import unpack
import unittest

class TestImportScript(unittest.TestCase):
    def testPointsPerTile(self):
			file = open('../data/Australia/S11E119.hgt','rb')
			b = file.read()
			self.assertEqual(len(b)/2,1201*1201)
			file.close()
    
    def testFirstNumber(self):
      file = open('../data/Australia/S11E119.hgt','rb')
      be_int = file.read(4)
      le_int = unpack('>i',be_int)
      self.assertEqual(le_int[0],0)
      file.close()

    def testTileIntegrity(self):
      # Uses two adjecant tiles around Melbourne to test
      # * the sum of altitudes of all 1201*1201 points in the tiles
      # * Eastern edge of West Melbourne tile should be the same as western edge 
      # of East melbourne tile.
      
      # Melbourne (West):
      res = loadTile("S37E144.hgt")
      self.assertEqual(res[1],14632703885312)
      west = res[0]

      ## Melbourne (East):
      res = loadTile("S37E145.hgt")
      self.assertEqual(res[1], 17769215361024)
      east=res[0]

      for i in range(1201):
        self.assertEqual(west[i][1200] - east[i][0],0) 

def loadTile(filename):
  file = open('../data/Australia/' + filename,'rb')
  tile = []
  total = 0
  for x in range(1201):
    row = []
    for y in range(1201):
      # Add two bytes for some reason (x86_64 specific?)
      be_int = file.read(2) + '\x00\x00' 
      row.append(unpack('>i',be_int)[0])

    tile.append(row)
    total = total + sum(row)

  file.close
  return [tile, total]

if __name__ == '__main__':
    unittest.main()
