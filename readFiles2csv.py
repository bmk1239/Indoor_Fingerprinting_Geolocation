#!/usr/bin/python

import sys
import csv
import utilities
import xlrd


# ResultDic - Dictionary contains rssi value and range value from each responder
# timestamp - Dictionary of timestamp to compare with timestamp in coordFile
# Cord_arr - coord array with the location of irobot in each measurement
# writer - writer of the open csv file
# create fingerprint entity in the DB
def createFingerprint(ResultDic, timestamp, Cord_arr, writer):
    lat, lon, alt = utilities.findLoc(timestamp, Cord_arr)
    # go over each measurement in the fingerprint and write it to csv file
    for e in ResultDic:
        writer.writerow({'mac': str(e), 'rssi[db]': str(ResultDic[e][0]),'Latitude' : str(lat[e]),
                         'Longitude' : str(lon[e]),'Altitude':alt[e][:-1] ,'range[cm]': str(ResultDic[e][1])})

# listOfFiles - tuple of result file and coord file
# create csv file with DB of fingerprints
def readFiles2csv(listOfFiles, floor, countNum):
    # data base of fingerprint in csv format
    csvfile1 = open(''.join(["Database_",str(floor),"_0.",str(countNum-1),".csv"]), "wb");
    csvfile2 = open(''.join(["User_",str(floor),"_0.",str(10-(countNum-1)),".csv"]), "wb");
    # header of DB
    fieldnames = ['mac', 'rssi[db]', 'Latitude', 'Longitude','Altitude' ,'range[cm]']
    writer1 = csv.DictWriter(csvfile1, fieldnames=fieldnames)
    writer1.writeheader()
    writer2 = csv.DictWriter(csvfile2, fieldnames=fieldnames)
    writer2.writeheader()
    # go over each file in the list
    j = 0
    # list of responder macs in second floor
    responders = []
    with open(''.join(["responders_",str(floor),".csv"])) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            responders.append(row['mac'])
    print len(responders)
    while j < len(listOfFiles):
        print listOfFiles[j], listOfFiles[j + 1]
        result = listOfFiles[j]
        with open(result) as fp:
            ResultDic = dict()
            timestamp = {}
            with open(listOfFiles[j + 1], 'r') as f:
                data = f.readlines()
            Cord_arr = []
            for lines in data:
                params = lines.split(" ")
                Cord_arr.append((round(float(params[0]), 6) * (10 ** 6), params[3], params[4], params[5]))
            seen = ""
            count = 1
            # go over each line in the file
            for line in fp:
                i = 0
                # mac address
                key = ''
                l = []
                # go over each part of the line
                for s in line.split():
                    # if we finished go over each responder in the fingerprint(16 responders at most), write result into DB
                    if s == seen:
                        # write fingerprint into csv file
                        if count < countNum:
                            createFingerprint(ResultDic, timestamp, Cord_arr , writer1)
                        else:
                            createFingerprint(ResultDic, timestamp, Cord_arr, writer2)
                        if count == 10:
                            count = 1
                        else:
                            count += 1
                        # go to next fingerprint
                        ResultDic.clear()
                        timestamp.clear()
                        seen = ""
                        i = 0
                    if i == 0:
                        if seen == "":
                            seen = s
                        if s not in responders:
                            break;
                        key = s;
                    if i == 1:
                        timestamp[key] = float(s)
                    # rssi value or range value
                    if i == 2 or i == 7:
                        l.append(float(s))
                    # if measurement failed set rssi with -120 db
                    if i == 10:
                        if s != "SUCCESS":
                            l[0] = -120
                        ResultDic[key] = l;
                    i += 1
                # save it in Dictionary
            if bool(ResultDic):
                if count < countNum:
                    createFingerprint(ResultDic, timestamp, Cord_arr, writer1)
                else:
                    createFingerprint(ResultDic, timestamp, Cord_arr, writer2)
        j += 2
    csvfile.close();
    pass

# xls file with responders locations
# create csv file contains responder location and Description
def readXls2csv(File, floor):
    sheet = xlrd.open_workbook(File).sheet_by_index(0)
    # responder file in csv format
    csvfile = open(''.join(["responders_",str(floor),".csv"]), "wb");
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
                if int(sheet.cell_value(i,j)) != floor:
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
             'Longitude': str(lon), 'Altitude': str(0),'Description': descrip})
    csvfile.close();
pass

def main(argv):
    # at least 1 args(one tuple)
    if(len(argv) < 1):
        print("Error: wrong number of arguments");
        return -1
    floors = [0,1,2]
    if (len(argv) == 1):
        for floor in floors:
            print "floor:" , floor
            # read responders from 2 floor locations
            readXls2csv(argv[0], floor)
    else:
        l = [10, 8, 6, 4, 2]
        for floor in floors:
            print "floor:", floor
            for num in l:
                print "count: ", num
                # read measurements into DB in csv format
                readFiles2csv(argv[0:], floor,num)
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
