# Script verifies that the MD5 checksum of all files is correct 

# Usage:
# You must specify the continent and you can optionally specify a bounding box.
# python test/verify_download.py Continent [north] [south] [west] [east]
# e.g.:
# python test/verify_download.py Australia
# python test/verify_download.py Eurasia 54 47 0 16

# I could not find the 'official' MD5 checksums for the data so I created them 
# myself. So if you get an error message, that could also mean the MD5 
# checksum in this script is wrong. In that case: please let me know.

import hashlib
import sys
import os

sys.path += [os.path.abspath('.')]
from data import util, files

continent = sys.argv[1]

[north, south, west, east] = util.getBoundingBox(sys.argv, 2)

files_hashes = util.getFilesHashes(continent)

if __name__ == '__main__':
  for file_hash in files_hashes:
    [lat,lon] = util.getLatLonFromFileName(file_hash[1])
    if util.inBoundingBox(lat, lon, north, south, west, east):
      f = file("data/" + continent + "/" + file_hash[1])
      if(not hashlib.md5(f.read()).hexdigest() == file_hash[0]):
        print "Error in file " + file_hash[1]
        exit()
  
