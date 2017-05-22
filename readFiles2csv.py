#!/usr/bin/python

import sys
import csv
import utilities
import xlrd

# list of responder macs in second floor
responders = []

# ResultDic - Dictionary contains rssi value and range value from each responder
# timestamp - list of timestamp to compare with timestamp in coordFile
# coordFile - name of coord file with the location of irobot in each measurement
# writer - writer of the open csv file
# create fingerprint entity in the DB
def createFingerprint(ResultDic, timestamp, coordFile, writer):
    # TODO - Tomer
    x, y, lat, lon, alt = utilities.findLoc(timestamp, coordFile)
    i = 0;
    # go over each measurement in the fingerprint and write it to csv file
    for e in ResultDic:
        if str(e) not in responders:
            continue;
        writer.writerow({'mac': str(e), 'rssi[db]': str(ResultDic[e][0]),'x[m]' : str(x[i]),'y[m]' : str(y[i]),'Latitude' : str(lat[i]),
                         'Longitude' : str(lon[i]),'Altitude':str(alt[i]) ,'range[cm]': str(ResultDic[e][1])})
        i += 1

# listOfFiles - tuple of result file and coord file
# create csv file with DB of fingerprints
def readFiles2csv(listOfFiles):
    # data base of fingerprint in csv format
    csvfile = open("Database.csv", "w");
    # header of DB
    fieldnames = ['mac', 'rssi[db]', 'x[m]', 'y[m]', 'Latitude', 'Longitude','Altitude' ,'range[cm]']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    # go over each file in the list
    j = 0
    with open("responders.csv") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            responders.append(row['mac'])
    while j < len(listOfFiles):
        result = listOfFiles[j]
        with open(result) as fp:
            k = 0;
            n = 0
            ResultDic = dict()
            # go over each line in the file
            for line in fp:
                i = 0
                # mac address
                key = ''
                l = []
                timestamp = []
                # go over each part of the line
                for s in line.split():
                    if i == 0:
                        key = s;
                    if i == 1:
                        timestamp.append(float(s))
                    # rssi value or range value
                    if i == 2 or i == 7:
                        l.append(float(s))
                    # if measurement failed set rssi with -120 db
                    if i == 10:
                        if s != "SUCCESS":
                            l[0] = -120
                    i += 1
                tmp = l[0]
                l[0] = l[1]
                l[1] = tmp
                # save it in Dictionary
                ResultDic[key] = l;
                # if we finished go over each responder in the fingerprint(16 responders at all), write result into DB
                if k == 15:
                    # write fingerprint into csv file
                    createFingerprint(ResultDic, timestamp, listOfFiles[j+1], writer)
                    # go to next fingerprint
                    ResultDic.clear()
                    k = 0
                else:
                    k += 1
                n += 1
        j += 2
    csvfile.close();
    pass

# xls file with responders locations
# create csv file contains responder location and Description
def readXls2csv(File):
    sheet = xlrd.open_workbook(File).sheet_by_index(0)
    # responder file in csv format
    csvfile = open("responders.csv", "w");
    # header of responder csv file
    fieldnames = ['mac', 'Latitude', 'Longitude','Altitude', 'Description']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    # go over each raw in file
    for i in range(4, 47):
        flag = False
        descrip, mac = "",""
        lat, lon = 0.0,0.0
        # go over each cell in file
        for j in range(0, len(sheet.row_values(i))):
            if j == 1:
                if int(sheet.cell_value(i,j)) != 2:
                    flag = True
                    break
            if j == 3:
                descrip = sheet.cell_value(i,j)
            if j == 4:
                mac = sheet.cell_value(i,j).lower()
            if j == 6:
                lat = float(sheet.cell_value(i,j))
            if j == 7:
                lon = float(sheet.cell_value(i,j))
        if flag:
            continue
        writer.writerow(
            {'mac': mac, 'Latitude': str(lat),
             'Longitude': str(lon), 'Altitude': str(2.5),'Description': descrip})
    csvfile.close();
pass

def main(argv):
    # at least 1 args(one tuple)
    if(len(argv) < 1):
        print("Error: wrong number of arguments");
        return -1
    if (len(argv) == 1):
        # read responders from 2 floor locations
        readXls2csv(argv[0])
    else:
        # read measurements into DB in csv format
        readFiles2csv(argv[0:])

    pass

if __name__ == "__main__":
    main(sys.argv[1:])
