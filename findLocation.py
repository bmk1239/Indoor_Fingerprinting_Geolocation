#!/usr/bin/python

import sys
import csv
import utilities

def findLocation(csvfilename, myRssi, N):
    dic0 = dict()
    dic1 = dict()
    with open(csvfilename) as csvfile:
        s = "".join(["f", str(0)])
        j = 0
        i = 0
        l = []
        x, y, z = 0.0, 0.0, 0.0
        reader = csv.DictReader(csvfile)
        for row in reader:
            if i == 0:
                x, y, z = row['x'], row['y'], row['z']
                dic0[s] = (x,y,z)
            l += [row['rssi']]
            if i == 4:
                dic1[s] = l
                j += 1
                s = "".join(["f", str(j)])
                i = 0
                l = []
            else:
                i += 1
    dic2 = dict()
    for e in dic1:
        d = utilities.calcDist(myRssi,dic1[e], 2)
        dic2[e] = d
    dic1.clear()
    dic3 = dict()
    for i in range(0,N):
        e = min(dic2, key=dic2.get)
        dic1[e] = dic0[e]
        dic3[e] = [dic2[e]]
        del dic2[e]
    x, y, z = utilities.calcLoc(dic1, dic3)
    print x, y, z

def main(argv):
    if(len(argv) < 6):
        print("Error: wrong number of arguments");
        return -1
    findLocation(argv[0],argv[1:], 10)
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
