#!/usr/bin/python

import sys
import csv
import utilities

# csvfilename - file name of fingerprint DB in csv format
# list of live rssi reading from user
# first algorithm using rssi and fingerprints only to get user location
def algorithm1(csvfilename, myRssi):
    # Dictionary contains x,y,z,alt,lon,lat for each fingerprint
    dic0 = dict()
    # Dictionary contains rssi values of each fingerprint
    dic1 = dict()
    # go over the csv file and extracts values
    with open(csvfilename) as csvfile:
        s = "".join(["f", str(0)])
        j = 0
        i = 0
        l = []
        x, y, z = 0.0, 0.0, 0.0
        reader = csv.DictReader(csvfile)
        for row in reader:
            if i == 0:
                x, y, z = row['x'], row['y'], row['Altitude']
                dic0[s] = [x,y,z,row['Latitude'], row['Longitude']]
            l += [row['rssi']]
            if i == 15:
                dic1[s] = l
                j += 1
                s = "".join(["f", str(j)])
                i = 0
                l = []
            else:
                i += 1
    min = -1
    imin = ""
    # using 1 nearest neighbor algorithm1 to find user location
    for e in dic1:
        d = utilities.calcDist(myRssi,dic1[e], 2)
        if imin == "":
            min = d
            imin = e
        else:
            if min > d:
                min = d
                imin = e
    x, y, alt,lat,lon = dic0[imin]
    print x, y, alt,lat,lon

# csvfilename - file name of fingerprint DB in csv format
# list of live rssi reading from user
# ranges of user from responder - less than 3
# second algorithm using rssi and fingerprints and range to get user location
# TODO - tomer
def algorithm2(csvfilename, myRssi, myRanges):
    pass

# csvfilename - file name of responders location
# ranges of user from responder - more than 2
# third algorithm using rssi and fingerprints and range to get user location
def algorithm3(csvfilename, myRanges):
    with open(csvfilename) as csvfile:
        reader = csv.DictReader(csvfile)
        dic = dict()
        for row in reader:
            lat = float(row['Latitude'])
            lon = float(row['Longitude'])
            alt = float(row['Altitude'])
            x, y, z = utilities.lla2ecef((lat, lon, alt))
            l = [x, y, z]
            dic[row['mac']] = l
    x, y, z = utilities.trilateration(dic,myRanges)
    lat, lon, alt = utilities.ecef2lla((x,y,z))
    print x, y, z,lat, lon, alt
    pass

def main(argv):
    if(len(argv) < 6):
        print("Error: wrong number of arguments");
        return -1
    findLocation(argv[0],argv[1:])
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
