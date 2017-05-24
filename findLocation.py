#!/usr/bin/python

import sys
import csv
import utilities

# csvfilename - file name of fingerprint DB in csv format
# list of live rssi reading from user
# returns dictionary with distance, location and ranges for each fingerprint
def allDistances(csvfilename, myRssi):
    # Dictionary contains x,y,z,alt,lon,lat for each fingerprint
    dic0 = dict()
    # Dictionary contains rssi values of each fingerprint
    dic1 = dict()
    # go over the csv file and extracts values
    with open(csvfilename) as csvfile:
        s = "".join(["f", str(0)])
        j = 0
        l = []
        l1 = dict()
        reader = csv.DictReader(csvfile)
        i = -1
        for row in reader:
            if (row['mac'] in l1):
                dic1[s] = l
                j += 1
                s = "".join(["f", str(j)])
                i = 0
                l = []
                l1 = dict()
            else:
                i += 1
            macs.append(row['mac'])
            if i == 0:
                lat1 = float(row['Latitude'])
                lon1 = float(row['Longitude'])
                alt1 = float(row['Altitude'])
                x, y, z = utilities.lla2ecef((lat1, lon1, alt1))
                dic0[s] = [x,y,z, lat1, lon1, alt1]
            l.append(row['rssi[db]'])
            l1[row['mac']] = row['range[cm]']
        if len(l) != 0:
            dic1[s] = [l,l1]
    dic = dict()
    for e in dic1:
        d = utilities.calcDist(myRssi,dic1[e][0], 2)
        dic[e] = [d,dic0[e],dic1[e][1]]
    return dic


# csvfilename - file name of fingerprint DB in csv format
# list of live rssi reading from user
# first algorithm using rssi and fingerprints only to get user location
def algorithm1(csvfilename, myRssi):
    dic = allDistances(csvfilename, myRssi)
    min = -1
    imin = ""
    # using 1 nearest neighbor algorithm1 to find user location
    for e in dic:
        if imin == "":
            min = dic[e][0]
            imin = e
        else:
            if min > dic[e][0]:
                min = dic[e][0]
                imin = e
    x, y, alt, lat, lon = dic[e][1]
    print x, y, alt, lat, lon
    pass

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
            lat1 = float(row['Latitude'])
            lon1 = float(row['Longitude'])
            alt1 = float(row['Altitude'])
            x, y, z = utilities.lla2ecef((lat1, lon1, alt1))
            l = [x, y, z]
            dic[row['mac']] = l
    x, y, z = utilities.trilateration(dic,myRanges)
    lat, lon, alt = utilities.ecef2lla((x,y,z))
    print lat, lon, alt
    pass

def main(argv):
    if(len(argv) < 6):
        print("Error: wrong number of arguments");
        return -1
    findLocation(argv[0],argv[1:])
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
