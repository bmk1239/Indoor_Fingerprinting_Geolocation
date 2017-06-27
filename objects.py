import csv
import operator
import utilities
from simplekml import Kml

class FpRaw:
    def __init__(self, mac, rssi, range,id):
        self.mac = mac
        self.rssi = rssi
        self.range = range
        self.id = id

    def __repr__(self):
        return "Raw {}: mac:{} rssi:{} range:{} ".format(self.id, self.mac, self.rssi, self.range)

class FingerPrint:
    def __init__(self):
        self.list = []
        self.Latitude = 0.0
        self.Longitude = 0.0
        self.Altitude = 0.0
        self.distance = 0.0
        self.size = 0

    def __repr__(self):
        s = "location: lat:{} lon:{} alt:{}\n".format(self.Latitude,self.Longitude,self.Altitude)
        for i in range(self.size):
            s += str(self.list[i]) + "\n"
        return s

    def appendRaw(self,mac, rssi, range):
        self.list.append(FpRaw(mac, rssi, range,self.size))
        self.size += 1

    def UpdateLoc(self,sumLat, sumLon, sumAlt):
        self.Latitude = sumLat/self.size
        self.Longitude = sumLon / self.size
        self.Altitude = sumAlt / self.size

    def UpdateDistance(self,d):
        self.distance = d

class Database:
    def __init__(self):
        self.list = []
        self.size = 0

    def __repr__(self):
        s = ""
        s += "Database\n"
        for i in range(self.size):
            s += "Fingerprint {}:\n".format(i)
            s += str(self.list[i]) + "\n"
        return s

    def appendFP(self,fp):
        self.list.append(fp)
        self.size += 1

    def readFromCsv(self,csvfilename):
        # go over the csv file and extracts values
        with open(csvfilename) as csvfile:
            sumLat, sumLon, sumAlt = 0.0, 0.0, 0.0
            seen = []
            fp = FingerPrint()
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row['mac'] in seen):
                    fp.UpdateLoc(sumLat, sumLon, sumAlt)
                    self.appendFP(fp)
                    sumLat, sumLon, sumAlt = 0.0, 0.0, 0.0
                    fp = FingerPrint()
                    seen = []
                mac = row['mac']
                rssi = float(row['rssi[db]'])
                # if float(row['range[cm]']) < 0.0:
                #     range=20.0
                # else:
                range = float(row['range[cm]'])
                sumLat += float(row['Latitude'])
                sumLon += float(row['Longitude'])
                sumAlt += float(row['Altitude'])
                fp.appendRaw(mac, rssi, range)
                seen += [row['mac']]



class RespoRaw:
    def __init__(self, mac, lat,lon,alt,desc):
        self.mac = mac
        self.Latitude = lat
        self.Longitude = lon
        self.Altitude = alt
        self.Description = desc

    def __repr__(self):
        return "Responder {}: lat:{} lon:{} alt:{}\nDescription: {}".format(self.mac, self.Latitude, self.Longitude,self.Altitude, self.Description)

class Responders:
    def __init__(self):
        self.list = []
        self.size = 0

    def __repr__(self):
        s = ""
        for i in range(self.size):
            s += str(self.list[i]) + "\n"
        return s

    def appendRaw(self,mac, lat,lon,alt,desc):
        self.list.append(RespoRaw(mac, lat,lon,alt,desc))
        self.size += 1

    def readFromCsv(self,csvfilename):
        # go over the csv file and extracts values
        with open(csvfilename) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                mac = row['mac']
                lat = float(row['Latitude'])
                lon = float(row['Longitude'])
                alt = float(row['Altitude'])
                desc = row['Description']
                self.appendRaw(mac, lat,lon,alt,desc)


class userData:
    def __init__(self,rangeDic, rssiDic, sumLat, sumLon, sumAlt):
        self.rangeDic = rangeDic
        self.rssiDic = rssiDic
        self.realLat = (sumLat/len(rssiDic))
        self.realLon = (sumLon/len(rssiDic))
        self.realAlt = (sumAlt/len(rssiDic))
        self.UserLocations = AllUserLocations(Location((self.realLat,self.realLon,self.realAlt)),(-1, -1, -1))
        self.valid=-1 # if algo 3 succeed




    def __repr__(self):
        s = ""
        for e in self.rangeDic:
            s += "Responder {} range:".format(e) + str(self.rangeDic[e]) + "\n"
        for e in self.rssiDic:
            s += "Responder {} rssi:".format(e) + str(self.rssiDic[e]) + "\n"
        s += "Real location: lat:{} lon:{} alt:{}".format(self.realLat,self.realLon,self.realAlt) + "\n"
        return s

    def updateAlgoLocation(self,loc1,loc2,loc3):
        self.UserLocations.algoLocations=(Location(loc1),Location(loc2),Location(loc3))
        self.valid = 1



class AllusersData:
    def __init__(self):
        self.list = []
        self.size = 0
        self.err_arr = [[], [], []]

    def __repr__(self):
        s = ""
        s += "AllusersData\n"
        for i in range(self.size):
            s += "User {}:\n".format(i)
            s += str(self.list[i]) + "\n"
        return s

    def appendUser(self,rangeDic, rssiDic, sumLat, sumLon, sumAlt):
        self.list.append(userData(rangeDic, rssiDic, sumLat, sumLon, sumAlt))
        self.size += 1

    def readFromCsv(self,csvfilename):
        # go over the csv file and extracts values
        with open(csvfilename) as csvfile:
            rangeDic = {}
            rssiDic = {}
            sumLat, sumLon, sumAlt = 0.0, 0.0, 0.0
            reader = csv.DictReader(csvfile)
            for row in reader:
                if (row['mac'] in rssiDic):
                    self.appendUser(rangeDic, rssiDic, sumLat, sumLon, sumAlt)
                    rangeDic = {}
                    rssiDic = {}
                    sumLat, sumLon, sumAlt = 0.0, 0.0, 0.0
                mac = row['mac']
                rssiDic[mac] = float(row['rssi[db]'])
                if float(row['range[cm]']) > 0.0:
                    rangeDic[mac] = float(row['range[cm]'])
                # if float(row['range[cm]']) < 0.0:
                #     rangeDic[mac] = 20.0
                sumLat += float(row['Latitude'])
                sumLon += float(row['Longitude'])
                sumAlt += float(row['Altitude'])

        csvfile.close()


    def calc_error_Arrays(self):
        for user in self.list:
            if user.valid != 1:
                continue
            realCartesian = user.UserLocations.realLoc.cartesian
            for i in range(3):
                if user.UserLocations.algoLocations[i].valid:
                    estimatedCartesian = user.UserLocations.algoLocations[i].cartesian
                # if distance_of_2_points((estimatedCartesian[0], estimatedCartesian[1]),(realCartesian[0], realCartesian[1])) > 100:
                #     continue
                    self.err_arr[i].append(utilities.distance_of_2_points((estimatedCartesian[0], estimatedCartesian[1]),
                                                       (realCartesian[0], realCartesian[1])))
    def getCartesianLocations(self,i,origin):
        XYArray=([],[])
        for user in self.list:
            if user.valid!=-1:
                if user.UserLocations.algoLocations[i].valid:
                    XYArray[0].append(user.UserLocations.algoLocations[i].cartesian[0]-origin[0])
                    XYArray[1].append(user.UserLocations.algoLocations[i].cartesian[1]-origin[1])
        return XYArray

    def getAllRssi(self,ignore):
        arr=[]
        for user in self.list:
            for rssi in user.rssiDic:
                value=user.rssiDic[rssi]
                if ignore and value==-120:
                    continue
                arr.append(value)
        return  arr
    # def createCSVforGoogleEarth(self):
    #     csvfile1 = open("AlgoResultsToGoogleEarth.csv", "wb");
    #     fieldnames = ['Name', 'Latitude', 'Longitude', 'LabelScale', 'IconColor', 'Folder','Icon']
    #     writer1 = csv.DictWriter(csvfile1, fieldnames=fieldnames)
    #     writer1.writeheader()
    #     for user in self.list:
    #         if user.valid != -1:
    #             writer1.writerow({'mac': str(e), 'rssi[db]': str(ResultDic[e][0]), 'Latitude': str(lat[e]),
    #                  'Longitude': str(lon[e]), 'Altitude': alt[e][:-1], 'range[cm]': str(ResultDic[e][1])})


    # icons -http://kml4earth.appspot.com/icons.html
    # simplekml- http://simplekml.readthedocs.io/en/latest/index.html
    def createKML(self):
        lat1=[32.1086076,32.1086076,32.1088341,32.10887584,32.1088403,32.1088447,32.1088341,32.1088394,32.1088344,32.1088297,32.1088297]
        lon1=[34.8047626,34.8047626,34.8052631,34.80518219,34.8052278,34.8052696,34.8052631,34.8052783,34.8052862,34.8052952,34.8052952]
        kml = Kml()
        algoNameLst = ["1 Basic RSSI Algorithm", "2 RSSI + FTM Algorithm", "3 Trilateration Algorithm"]
        folders=[kml.newfolder(name=algoNameLst[0]),kml.newfolder(name=algoNameLst[1]), kml.newfolder(name=algoNameLst[2]), kml.newfolder(name="Real Locations")]
        colors=['ff0000ff','ffff0000','FF008000','FF000000']
        icons=["http://maps.google.com/mapfiles/dir_0.png","http://maps.google.com/mapfiles/kml/pal4/icon48.png","http://maps.google.com/mapfiles/kml/pal4/icon60.png"]
        iconsSize=[0.6,0.5,0.4]
        i=0
        for user in self.list:
            if user.valid != -1:
                j = 3
                fol = folders[j]
                a1 = user.UserLocations.realLoc.lla[0]
                b1 = user.UserLocations.realLoc.lla[1]
                pnt = fol.newpoint(name="RL_P_" + str(i), coords=[(b1, a1)])
                pnt.style.labelstyle.scale = 0.2
                pnt.style.iconstyle.color = colors[j]
                pnt.style.iconstyle.scale = 0.5  # Icon thrice as big
                pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal4/icon56.png'
                iconSize = 0.8
                for j in range(3):
                # for j in range(2,-1,-1):
                    fol=folders[j]
                    if user.UserLocations.algoLocations[j].valid==0:
                        continue
                    a1=user.UserLocations.algoLocations[j].lla[0]
                    b1=user.UserLocations.algoLocations[j].lla[1]
                    pnt = fol.newpoint(name="A_"+str(j)+"_P_"+str(i), coords=[(b1, a1)])
                    pnt.style.labelstyle.scale = 0.2
                    # pnt.style.iconstyle.color = colors[j]
                    pnt.style.iconstyle.scale = iconsSize[j]  # Icon thrice as big
                    # pnt.style.iconstyle.icon.href = 'http://maps.google.com/mapfiles/kml/pal4/icon57.png'
                    pnt.style.iconstyle.icon.href = icons[j]
                    iconSize=iconSize-0.1


                i = i + 1
        # ground = kml.newgroundoverlay(name='GroundOverlay')
        # ground.icon.href = 'map.png'
        # ground.gxlatlonquad.coords = [(34.8055585549771,32.1089857421224),(34.8055585549771,32.108480189356),(34.8048439153402,32.108480189356),(34.8048439153402,32.1089857421224),(34.8055585549771,32.1089857421224)]
        kml.save(utilities.folderName+"AllLocations.kml")

#holds lla and cartesian location
class Location:
    def __init__(self,lla): #assume lla is tuple of (latDeg, lonDeg, alt)
        self.lla = lla
        self.cartesian = utilities.lla2ecef((lla[0],lla[1],0)) # alt allwas 0
        self.valid=[1,0][lla==(0,0,0) or lla==(-1,-1,-1)]

class AllUserLocations:
    def __init__(self, realLoc,algoLocations):
        self.realLoc=realLoc
        self.algoLocations=algoLocations

class AlgoInfo:
    def __init__(self, id,time):
        self.time=time
        self.id = id

    def setRMS(self,rms):
        self.rms=rms

    def __repr__(self):
        return "Algo {} RMSE:{} Run Time:{}".format(self.id, str(round(self.rms,4)), str(round(self.time,4)))


