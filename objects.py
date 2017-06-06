import csv
import operator

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

    def __repr__(self):
        s = ""
        for e in self.rangeDic:
            s += "Responder {} range:".format(e) + str(self.rangeDic[e]) + "\n"
        for e in self.rssiDic:
            s += "Responder {} rssi:".format(e) + str(self.rssiDic[e]) + "\n"
        s += "Real location: lat:{} lon:{} alt:{}".format(self.realLat,self.realLon,self.realAlt) + "\n"
        return s


class AllusersData:
    def __init__(self):
        self.list = []
        self.size = 0

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
                sumLat += float(row['Latitude'])
                sumLon += float(row['Longitude'])
                sumAlt += float(row['Altitude'])

