#!/usr/bin/python

import sys
import utilities
import objects

# database - object of fingerprint DB
# list of live rssi reading from user
# update distance for each fingerprint
def allDistances(database, myRssi):
    assert isinstance(database, objects.Database)
    for i in range(database.size):
        fp = database.list[i]
        assert isinstance(fp, objects.FingerPrint)
        d = utilities.calcDist(myRssi,fp, 2)
        fp.UpdateDistance(d)
    pass


# database - object of fingerprint DB
#  user - object for user
# first algorithm using rssi and fingerprints only to get user location
def algorithm1(database, user):
    assert isinstance(database, objects.Database)
    assert isinstance(user, objects.userData)
    allDistances(database, user.rssiDic)
    min = -1
    imin = -1
    # using 1 nearest neighbor algorithm1 to find user location
    for i in range(database.size):
        fp = database.list[i]
        assert isinstance(fp, objects.FingerPrint)
        if imin == -1:
            min = fp.distance
            imin = i
        else:
            if min > fp.distance:
                min = fp.distance
                imin = i
    fp = database.list[imin]
    assert isinstance(fp, objects.FingerPrint)
    lat = fp.Latitude
    lon = fp.Longitude
    alt = fp.Altitude
    return  lat, lon, alt
    pass

# database - object of fingerprint DB
#  user - object for user
# second algorithm using rssi and fingerprints and range to get user location
def algorithm2(database, user):
    assert isinstance(database, objects.Database)
    assert isinstance(user, objects.userData)
    allDistances(database, user.rssiDic)
    imins = []
    myRanges = user.rangeDic
    while True:
        min = -1
        imin = -1
        for i in range(database.size):
            fp = database.list[i]
            assert isinstance(fp, objects.FingerPrint)
            if i in imins:
                continue
            if imin == -1:
                min = fp.distance
                imin = i
            else:
                if min > fp.distance:
                    min = fp.distance
                    imin = i
        if imin == -1:
            fp = database.list[imins[0]]
            assert isinstance(fp, objects.FingerPrint)
            lat = fp.Latitude
            lon = fp.Longitude
            alt = fp.Altitude
            return lat, lon, alt
        imins.append(imin)
        flag = True
        fp = database.list[imin]
        assert isinstance(fp, objects.FingerPrint)
        for i in range(fp.size):
            fpRaw = fp.list[i]
            assert isinstance(fpRaw, objects.FpRaw)
            if fpRaw.mac in myRanges:
                if (((myRanges[fpRaw.mac] + fp.distance*100) < fpRaw.range) or
                        (abs(myRanges[fpRaw.mac] - fp.distance*100) > fpRaw.range)):
                    flag = False
                    break
        if flag:
            lat = fp.Latitude
            lon = fp.Longitude
            alt = fp.Altitude
            return lat, lon, alt
    pass

# resps - object of responder locations
#  user - object for user
# third algorithm using rssi and fingerprints and range to get user location
def algorithm3(resps, user):
    assert isinstance(resps, objects.Responders)
    assert isinstance(user, objects.userData)
    lat, lon, alt = utilities.trilateration(resps,user.rangeDic)
    return lat, lon, alt
    pass

def main(argv):
    if (len(argv) < 3):
        print("Error: wrong number of arguments");
    db = objects.Database()
    resps = objects.Responders()
    users = objects.AllusersData()
    db.readFromCsv(argv[0])
    resps.readFromCsv(argv[1])
    users.readFromCsv(argv[2])
    i = 0
    print db
    print "*************"
    print resps
    print "*************"
    print users
    pass
    for user in users.list:
        print "user {}: {}".format(i,(user.realLat,user.realLon,user.realAlt))
        lla1 = algorithm1(db,user)
        lla2 = algorithm2(db, user)
        lla3 = algorithm3(resps, user)
        print "Algo1: {}".format(lla1)
        print "Algo2: {}".format(lla2)
        print "Algo3: {}".format(lla3)
        i += 1
    pass

if __name__ == "__main__":
    main(sys.argv[1:])