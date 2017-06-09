#!/usr/bin/python

import sys

import utilities
import objects
import itertools
import error_env

# database - object of fingerprint DB
# list of live rssi reading from user
# update distance for each fingerprint
def allDistances(database, myRssi):
    assert isinstance(database, objects.Database)
    for i in range(database.size):
        fp = database.list[i]
        assert isinstance(fp, objects.FingerPrint)
        d = utilities.calcDist(myRssi,fp, 2.0)
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
        count = 0
        for i in range(fp.size):
            if count == 2:
                break;
            fpRaw = fp.list[i]
            assert isinstance(fpRaw, objects.FpRaw)
            if fpRaw.mac in myRanges:
                if (((myRanges[fpRaw.mac] + fp.distance) < fpRaw.range) or
                        (abs(myRanges[fpRaw.mac] - fp.distance) > fpRaw.range)):
                    flag = False
                    break
                count += 1
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
    if len(user.rangeDic) < 3:
        print "Error: less than 3 ranges"
        return (0,0,0)
    len1 = len(user.rangeDic)
    min = 0.0
    lat, lon, alt = -1,-1,-1
    while True:
        result_list = map(dict, itertools.combinations(user.rangeDic.iteritems(), len1))
        for dic in result_list:
            lat1, lon1, alt1, factor = utilities.trilateration(resps, dic)
            if (lat1, lon1, alt1) != (0,0,0):
                if min == 0 or min > factor:
                    min = factor
                    lat, lon, alt = lat1, lon1, alt1
        len1 -= 1
        if len1 == 2:
            break
    return (lat, lon, alt)
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
    count = 0
    for user in users.list:
        # print "user {}: {}".format(i,(user.realLat,user.realLon,user.realAlt))
        res_arr=utilities.readFromResult()
        # lla1 = algorithm1(db,user)
        lla1 = res_arr[0][i]
        # lla2 = algorithm2(db, user)
        lla2 = res_arr[1][i]
        # lla2 = (0,0,0)
        lla3 = algorithm3(resps, user)
        # lla3 = res_arr[2][i]
        # lla3 = (1,0,0)
        if lla3 == (-1,-1,-1):
            count += 1
        if lla3!=(0,0,0) and lla3!=(-1,-1,-1):
            user.updateAlgoLocation(lla1,lla2,lla3)
        print "Algo1: {}".format(lla1)
        print "Algo2: {}".format(lla2)
        print "Algo3: {}".format(lla3)
        i += 1
        # if i>50:
        #     break
    # print count
    error_env.calc_error(users.list)
    pass

if __name__ == "__main__":
    main(sys.argv[1:])