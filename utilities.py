import math
import sys, getopt
import numpy as np
from math import pow, cos, sin, sqrt, degrees, radians, atan2, pi
from scipy import cos, sin, arctan, sqrt, arctan2

# assume WGS84
wgs84_a = 6378137.0
wgs84_f = 1.0 / 298.257223563
wgs84_e2 = 2 * wgs84_f - np.power(wgs84_f,2)

# code from https://github.com/ethz-asl/StructuralInspectionPlanner/blob/master/utils/ExportToPX4/SIP2PX4.py
# lonLatAlt - conatins LLA in radians
# Coordinate conversion functions from LLA to cartesian
def lla2ecef(lonLatAlt):
    # LLA2ECEF Conversion (meters)
    lon, lat, alt = lonLatAlt
    a, e2 = wgs84_a, wgs84_e2
    chi = sqrt(1 - e2 * sin(lat) ** 2)
    q = (a / chi + alt) * cos(lat)
    return (q * cos(lon),q * sin(lon),((a * (1 - e2) / chi) + alt) * sin(lat))

# code from https://github.com/ethz-asl/StructuralInspectionPlanner/blob/master/utils/ExportToPX4/SIP2PX4.py
# ecef - contains x,y,z in meters
# convert from cartesian coordinate to LLA in radians
def ecef2lla(ecef):
	# ECEF2LLA (radians)
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
    return (lon,lat,alt)


# timestamp - list of timestamps to compare with coordFile
# coordFile - name of coordFile
# returns - list of x, list of y, list of latitude, list of longitude and list of altitude extracts from coordFile.
# list size same as timestamp size
def findLoc(timestamp, coordFile):

    pass

# code converted from https://github.com/subpos/subpos_receiver/blob/master/Trilateration.cpp
# RespLocDic - Dictionary with the location of each responder in cartesian coordinate
# ResultDic - Dictionary with ranges of user from each responder (at least 3 valid ranges)
def trilateration(RespLocDic, ResultDic):
    A = []
    b = []
    seen1 = []
    flag = True
    print ResultDic
    print RespLocDic
    if len(ResultDic) == 0:
        return 0, 0, 0
    for e in ResultDic:
        seen1.append(e)
        # convert from cm to meter
        r1 = (ResultDic[e])*0.01
        if r1 < 0:
            return 0,0,0
        x1 = float(RespLocDic[e][0])
        y1 = float(RespLocDic[e][1])
        z1 = float(RespLocDic[e][2])
        for e1 in ResultDic:
            if e1 in seen1:
                continue
            r2 = (ResultDic[e1])*0.01
            if r2 < 0:
                return 0,0,0
            x2 = float(RespLocDic[e1][0])
            y2 = float(RespLocDic[e1][1])
            z2 = float(RespLocDic[e1][2])
            if z1 != z2:
                flag = False
            b1 = ((pow(x1, 2)-pow(x2, 2)) +
                      (pow(y1, 2)-pow(y2, 2)) +
                      (pow(z1, 2)-pow(z2, 2)) -
                      (pow(r1, 2) - pow(r2, 2))) / 2
            b.append([b1]);
            A1 = [x1-x2, y1-y2, z1-z2]
            A.append(A1)
    x,y,z = np.linalg.lstsq(A,b)[0]
    return (x[0],y[0],z1 if flag else z[0])
    pass

# algorithm from http://journals.sagepub.com/doi/full/10.1155/2015/429104
# f_0 - live RSSI reading from user
# f_i - RSSI from fingerprint
# q - constant in this case 2
# calculate euclidean distance from rssi
def calcDist(f_0, f_i, q):
    sum = 0.0
    for i in range(0,len(f_0)):
        try:
            x = float(f_0[i]) - float(f_i[i])
        except IndexError:
            print f_0, f_i
        sum += pow(x,q)
    d = abs(sum)
    return pow(d,1/q)


