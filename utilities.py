import math
import sys, getopt
import numpy as np
from math import pow, cos, sin, sqrt, degrees, radians, atan2, pi
from scipy import cos, sin, arctan, sqrt, arctan2
import objects
import re

# assume WGS84
wgs84_a = 6378137.0
wgs84_f = 1.0 / 298.257223563
wgs84_e2 = 2 * wgs84_f - np.power(wgs84_f,2)

# code from https://github.com/ethz-asl/StructuralInspectionPlanner/blob/master/utils/ExportToPX4/SIP2PX4.py
# lonLatAlt - conatins LLA in degrees
# Coordinate conversion functions from LLA to cartesian
def lla2ecef(lonLatAlt):
	# LLA2ECEF Conversion (meters)

    latDeg, lonDeg, alt = lonLatAlt
    a, e2 = wgs84_a, wgs84_e2
    lon = radians(lonDeg)
    lat = radians(latDeg)
    chi = sqrt(1 - e2 * sin(lat) ** 2)
    q = (a / chi + alt) * cos(lat)
    return (q * cos(lon),
            q * sin(lon),
            ((a * (1 - e2) / chi) + alt) * sin(lat))

# code from https://github.com/ethz-asl/StructuralInspectionPlanner/blob/master/utils/ExportToPX4/SIP2PX4.py
# ecef - contains x,y,z in meters
# convert from cartesian coordinate to LLA in degrees
def ecef2lla(ecef):
	# ECEF2LLA (degrees)

    x, y, z = ecef
    a, e2, f = wgs84_a, wgs84_e2, wgs84_f
    lon = atan2(y, x)
    s = sqrt(x ** 2 + y ** 2)
    step = 0
    lat = None
    latPrev = 0
    converged = False
    while not converged:
        if step == 0:
            beta = atan2(z, (1 - f) * s)  # initial guess
        else:
            beta = atan2((1 - f) * sin(lat), cos(lat))  # improved guess
        lat = atan2(z + (e2 * (1 - f) / (1 - e2)) * a * sin(beta) ** 3,
                    s - e2 * a * cos(beta) ** 3)
        if (lat - latPrev) < 1e-4:
            converged = True
        latPrev = lat
        step += 1
    N = a / sqrt(1 - e2 * sin(lat) ** 2)
    alt = s * cos(lat) + (z + e2 * N * sin(lat)) * sin(lat) - N
    return (degrees(lat),
            degrees(lon),
            alt)

# timestamp - Dictionary of timestamps to compare with coordFile
# Cord_arr - array of coordFile
# returns - Dictionary of latitude, Dictionary of longitude and Dictionary of altitude extracts from Cord_arr.
def findLoc(timestamp, Cord_arr):
    lat = {}
    lon = {}
    alt = {}
    for t in timestamp:
        ts = timestamp[t]
        index=minDiffEntry(Cord_arr,ts)
        lat[t] = (Cord_arr[index][1])
        lon[t] = (Cord_arr[index][2])
        alt[t] = (Cord_arr[index][3])
    return lat,lon,alt

# code converted from https://github.com/subpos/subpos_receiver/blob/master/Trilateration.cpp
# resps - object with the locations of each responder in lla coordinate
# myRanges - Dictionary with ranges of user from each responder (at least 3 valid ranges)
def trilateration(resps, myRanges):
    assert isinstance(resps, objects.Responders)
    A = []
    b = []
    z = []
    seen = {}
    for i in range(resps.size):
        resp1 = resps.list[i]
        assert isinstance(resp1, objects.RespoRaw)
        if resp1.mac not in myRanges:
            continue
        r1 = (myRanges[resp1.mac]) * 0.01
        if r1 < 0:
            continue
        x1, y1, z1 = lla2ecef((resp1.Latitude,resp1.Longitude,resp1.Altitude))
        seen[resp1.mac] = (x1,y1,r1)
        z.append(z1)
        for j in range(i+1,resps.size):
            resp2 = resps.list[j]
            assert isinstance(resp2, objects.RespoRaw)
            if resp2.mac not in myRanges:
                continue
            r2 = (myRanges[resp2.mac]) * 0.01
            if r2 < 0:
                continue
            x2, y2, z2 = lla2ecef((resp2.Latitude, resp2.Longitude, resp2.Altitude))
            z.append(z2)
            b1 = ((pow(x1, 2) - pow(x2, 2)) +
                  (pow(y1, 2) - pow(y2, 2)) -
                  (pow(r1, 2) - pow(r2, 2))) / 2
            b.append([b1]);
            A1 = [x1-x2, y1-y2]
            A.append(A1)
    try:
        x,y = np.linalg.lstsq(A,b)[0]
    except:
        return 0,0,0
    x,y, z = x[0],y[0], (sum(z)/len(z))
    factor = 0.5
    max = 0
    while True:
        flag = True
        for mac in seen:
            x1, y1, r1 = seen[mac]
            r1 += factor
            if r1 > max:
                max = r1
            if sqrt(pow(x1 - x, 2) + pow(y1 - y, 2)) > r1:
                flag = False
                break
        if flag:
            break
        factor += 0.5
        if factor > 20:
            break;
    if factor > 20:
        return 0,0,0,0
    lat, lon, alt = ecef2lla((x,y,z))
    return lat, lon, 0, factor
    pass

# algorithm from http://journals.sagepub.com/doi/full/10.1155/2015/429104
# f_0 - live RSSI reading from user
# f_i - RSSI from fingerprint
# q - constant in this case 2
# calculate euclidean distance from rssi
def calcDist(f_0, f_i, q):
    sum = 0.0
    for i in range(0,min(len(f_0),f_i.size)):
        fpRaw = f_i.list[i]
        assert isinstance(fpRaw, objects.FpRaw)
        mac = fpRaw.mac
        x = float(f_0[mac]) - float(fpRaw.rssi)
        sum += pow(x,q)
    d = abs(sum)
    return pow(d,1/q)


# def changeTimeFormat(t):
def minDiffEntry(arr,time):
    min=9999999999999999
    minindex=-1
    for i in xrange(len(arr)):
        diff=abs(time-arr[i][0])
        if abs(time-arr[i][0])<min:
            min=diff
            minindex=i
            # print minindex,diff
    return  minindex



def readFromResult():
    file_arr=["algo1res.txt","algo2res.txt","algo3res.txt"]
    ret_arr=[[],[],[]]
    for i in range(3):
        f=open(file_arr[i],"r")
        for line in f:
            ret_arr[i].append(eval(re.search("Algo\d: (.*)",line).groups(1)[0]))
    return ret_arr


# gets two points and return the distace between them.
def distance_of_2_points(estimatedLocation,realLocation):
    return math.hypot(estimatedLocation[0] - realLocation[0], estimatedLocation[1] - realLocation[1])

def get_error_array(data1,data2):
    return [distance_of_2_points(data1[i],data2[i]) for i in xrange(len)]







