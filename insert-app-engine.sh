#!/bin/bash

# Inserts one tile into the data store, 1 row at a time.
# Usage: ./insert [start_row_number]
# e.g. : "./insert 1" starts at the first row
#        "./insert 230" resumes from row 230

# If the connection fails, it will retry after 30 seconds. 
# You can abort it with ctrl+c

# Get your cookie string at your-app-name.appspot.com/load
COOKIE="--cookie=ACSID=AJKiYcGKgvz9W0iA0pJg95liB4QAXL89zDouK_cBo-f74dE-9SfAZY6m1bBTJ-4QANbqWlKiUvi_-0TRTNCR3sgDW-8JE7Qj3wLcXdnXK-WBjSbphCqIPk-FbpLseuM-CXbNLIFxFuCo-SrzcRifevKQFT3DrBJU9QHI5j8HFe26t0YglqPUh7TLSvEnvycaHZXrxN0TTbAZYOThl-EknJydB0AH7k4BpGiog6m5o7ykbeHpNeRR8o37NcHHlFfkIhESpp3LHLHctb0aGGgdWKqcxxb9Im8PIUupcOMG1xMGgKs5-Jbq-sEFz8Gx2t8UtsSb3uRobluD9O2BgwDe0urWRPh6k8cClfToEjkNop2AWvvmCxoK5F6SiH6NlYOu0-5f46-7mwbucZ_q4q-nVQNofIGTRgr7UKd5w3VPcqJ3lRbZTo9cQiaBzeRN6zY70hK2Y3uBz7D-"

# If you use the offline data store, the cookie will look like this by defalt:
# COOKIE="--cookie='dev_appserver_login="test@example.com:True"'"

# Enter location of the bulk upload client on your system
BULKLOADCLIENT="/home/sjors/gapp/tools/bulkload_client.py"

# Enter location where you put your version of the App Engine application:
#APPURL="http://altitude.sprovoost.nl/load" # Returns a "Bad Gateway" error
APPURL="http://osm-route-altitude-profile.appspot.com/load"

# You can also use the local datastore:
#APPURL="http://localhost:8080/load"

for ((a=$1; a <= 1200 ; a++))
do
  SUCCESS="false"
  while [ $SUCCESS = "false" ]; do
    python import-google-apps-engine.py online $a 2> error.txt
    cat error.txt | grep KeyboardInterrupt > stop
    if [ -s stop ]; then
      echo "Keyboard Interrupt : stopping..."
      rm stop
      exit
    fi

    $BULKLOADCLIENT --filename data/tile.csv --kind Altitude --url $APPURL --batch_size 150 $COOKIE 2>> error.txt

    cat error.txt | grep KeyboardInterrupt > stop
    if [ -s stop ]; then
      echo "Keyboard Interrupt : stopping..."
      rm stop
      exit
    fi

    cat error.txt | grep "Import succcessful" > success

    if [ -s success ]; then 
      SUCCESS="true" 
      rm success
    else
      echo "An error occured! Server probably overloaded. Let's try again..."
      echo "Retry tile $a... in 5 minutes"
      sleep 300
    fi

  done
done                           # A construct borrowed from 'ksh93'.
