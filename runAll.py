import findLocation
import utilities
import time

utilities.runAll=1

for j in range(1,10,2):
    print j
    utilities.folderName = "figures/db"
    # ratio=(j+1)*0.1
    # print "Database_2_0." + str(j) + ".csv", "User_2_0." + str(10-j) + ".csv"
    findLocation.main(["Database_2_0." + str(10-j) + ".csv","responders.csv", "User_2_0." + str(j) + ".csv"])
    print "it was "+str(10-j)
    # time.sleep(30)