#!/usr/bin/python

import sys
import csv
import utilities

def createFingerprint(RespLocDic, ResultDic, writer):
    x, y, z = utilities.calcLoc(RespLocDic, ResultDic)
    if x == 0 and y == 0 and z == 0:
        return
    for e in ResultDic:
        writer.writerow({'mac': e, 'rssi': str(ResultDic[e][0]),'x' : str(x),'y' : str(y),'z' : str(z)})

def readFiles2csv(RespLoc,results):
    RespLocDic = dict()
    with open(RespLoc) as fp:
        for line in fp:
            i = 0
            key = ''
            l = []
            for s in line.split():
                if i == 0:
                    key = s;
                if i > 2:
                    l.append(float(s))
                i += 1
            RespLocDic[key] = l;
    j = 0;
    for result in results:
        csvfile = open(''.join(["result", str(j), ".csv"]), "w");
        fieldnames = ['mac', 'rssi', 'x', 'y', 'z']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        with open(result) as fp:
            k = 0;
            n = 0
            ResultDic = dict()
            for line in fp:
                i = 0
                key = ''
                l = []
                for s in line.split():
                    if i == 0:
                        key = s;
                    if i == 2 or i == 7:
                        l.append(float(s))
                    if i == 10:
                        if s != "SUCCESS":
                            l[0] = -120
                    i += 1
                tmp = l[0]
                l[0] = l[1]
                l[1] = tmp
                ResultDic[key] = l;
                if k == 4:
                    createFingerprint(RespLocDic, ResultDic, writer)
                    ResultDic.clear()
                    k = 0
                else:
                    k += 1
                print n
                n += 1
        j += 1
        csvfile.close();
    RespLocDic.clear()
    pass

def main(argv):
    if(len(argv) < 2):
        print("Error: wrong number of arguments");
        return -1
    readFiles2csv(argv[0],argv[1:])
    pass

if __name__ == "__main__":
    main(sys.argv[1:])
