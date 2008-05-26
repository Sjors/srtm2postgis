# Runs tests for download.py
import unittest

# Import same libraries as download.py:
from ftplib import FTP
import urllib

class TestDownloadScript(unittest.TestCase):
    
    def testFtp(self):
        # Make sure:
        
        print "Does the FTP server still exists and is it online?" 
        self.ftp = FTP('e0srp01u.ecs.nasa.gov')
        self.assert_(self.ftp.login())        

        print "Is the data in the right folder?"
        self.assert_(self.ftp.cwd("srtm/version2/SRTM3/Australia"))
       
        print "Are there 1060 files in that folder?"
        self.files = self.ftp.nlst()
        self.assertEqual(len(self.files),1060)

if __name__ == '__main__':
    unittest.main()

