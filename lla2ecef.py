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

def main():
    latDeg, lonDeg, alt = 38.889139,-77.049,130.049
    x,y,z = lla2ecef((lonDeg, latDeg, alt))
    print x,y,z;
    
if __name__ == "__main__":
    main()
