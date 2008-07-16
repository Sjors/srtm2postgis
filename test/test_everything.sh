#!/bin/bash
echo "Download script unit tests..."
python test/test_download.py

echo "Download one tile..."
python download.py Australia 0 -11 -11 119 119

echo "Verify this download..."
python test/verify_download.py Australia -11 -11 119 119

cd data/Australia && unzip S11E119.hgt.zip && cd ../..

echo "Test database insert..."
python test/test_read_data.py

