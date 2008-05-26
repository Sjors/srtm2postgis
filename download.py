# Downloads the SRTM data for Australia
#
# Loosely based on example at:
# http://postneo.com/stories/2003/01/01/beyondTheBasicPythonFtplibExample.html

# Import some libraries:
from ftplib import FTP
import urllib

# First we get the list of files through an FTP connection.

ftp = FTP('e0srp01u.ecs.nasa.gov')

def handleDownload(block):
    file.write(block)
    print ".",

ftp.login()

ftp.cwd("srtm/version2/SRTM3/Australia")

# Now list all Australian tiles.
# See ftp://e0srp01u.ecs.nasa.gov/srtm/version2/SRTM3/Australia/

# List all files (should be 1060)
files = ftp.nlst()

# And close connection.

ftp.close()

# Now download all files using urllib.urlretrieve

for i in range(len(files)):
  print "Downloading " + files[i] + "... (" + str(i + 1) + " of " + str(len(files)) +")"
  urllib.urlretrieve("ftp://e0srp01u.ecs.nasa.gov/srtm/version2/SRTM3/Australia/" + files[i],"data/Australia/" + files[i])

