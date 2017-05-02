import math
import sys, getopt
import numpy as np
from math import pow, cos, sin, sqrt, degrees, radians, atan2, pi
from scipy import cos, sin, arctan, sqrt, arctan2

# assume WGS84
wgs84_a = 6378137.0
wgs84_f = 1.0 / 298.257223563
wgs84_e2 = 2 * wgs84_f - np.power(wgs84_f,2)

# Coordinate conversion functions
def lla2ecef(lonLatAlt):
    # LLA2ECEF Conversion (meters)

    lonDeg, latDeg, alt = lonLatAlt
    a, e2 = wgs84_a, wgs84_e2
    lon = radians(lonDeg) 
    lat = radians(latDeg) 
    chi = sqrt(1 - e2 * sin(lat) ** 2)
    q = (a / chi + alt) * cos(lat)
    return (q * cos(lon),q * sin(lon),((a * (1 - e2) / chi) + alt) * sin(lat))

def calcLoc(RespLocDic, ResultDic):
    sum = 0.0
    x , y, z = 0.0, 0.0, 0.0
    if len(ResultDic) == 0:
        return 0, 0, 0
    for e in ResultDic:
        if (ResultDic[e][0] == 0):
            w = 0
        else:
            w = 1.0 / (ResultDic[e][0])
        sum += w
        x += (w * float(RespLocDic[e][0]))
        y += (w * float(RespLocDic[e][1]))
        z += (w * float(RespLocDic[e][2]))
    try:
        x = x / sum
    except ZeroDivisionError:
        x = 0.0
    try:
        y = y / sum
    except ZeroDivisionError:
        y = 0.0
    try:
        z = z / sum
    except ZeroDivisionError:
        z = 0.0
    return (x,y,z)
    pass

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

