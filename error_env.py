import numpy as np
import matplotlib.pyplot as plt
import math
import utilities


showPlots=1 # flag which decide if show (1) plots or not (0)
LocationsToShowOnWhiteMap=[0,1,2,3]

def print_CDFV1(arr):
    Z=arr
    # N = length = 10000
    N = length = len(arr)*100
    H, X1 = np.histogram(Z, bins=length , normed=True)
    # print H
    dx = X1[1] - X1[0]
    F1 = np.cumsum(H) * dx
    # method 2
    X2 = np.sort(Z)
    F2 = np.array(range(N)) / float(N)
    return X1[1:], F1
    # plt.plot(X1[1:], F1, "r")
    # plt.plot(X2, F2)
    # axes = plt.gca()
    # # print max(arr)
    # axes.set_xlim([0, max(arr)])
    # axes.set_xlim([0, 15])
    # plt.show()


def print_CDFV1_forAll(arrs):
    f2 = plt.figure()
    ax = f2.add_subplot(111)

    ax.legend()

    for i in range(len(arrs)):
        x,f=print_CDFV1(arrs[i])
        ax.plot(x, f, label='$Algo %i$' % (i+1))
        # plt.plot(x, f, label='$algo%i$' % i )
    # plt.plot(X2, F2)
    axes = plt.gca()
    # print max(arr)
    # axes.set_xlim([0, max([max(arr) for arr in arrs])])
    # axes.set_xlim([0, 10])
    ax.legend()
    # ax.set_xlim([0, 15])
    plt.xlabel("Localization Error [m]")
    plt.ylabel("CDF")
    plt.title('Empirical CDF')
    plt.savefig("figures/CDF.png")




## version 2 of code which plots CDF graph
def print_CDFV2(err_array):
    x2 = []
    y2 = []
    y = 0
    err_file = open("err.txt", "r")
    err_array = [abs(float(line)) for line in err_file]
    sorted = np.sort(err_array)
    for x in sorted:
        x2.extend([x, x])
        y2.append(y)
        y += 1.0 / len(err_array)
        y2.append(y)
    plt.plot(x2, y2, "g")
    axes = plt.gca()
    axes.set_xlim([0, 10])
    plt.savefig("figures/CDF.png")
    plt.show()


def calc_rms(arr):
    return (sum(map(lambda x:x*x,arr))/(1.0*len(arr)))**0.5


def rssiHistogram(arr):
    f1 = plt.figure()
    print len(set(arr))
    ax1 = f1.add_subplot(111)
    ax1.hist(arr, bins=len(set(arr))+1,edgecolor='black', linewidth=1.2)
    # plt.xticks(range(len(set(arr))))
    ax1.legend()
    plt.xlabel("RSSI [db]")
    plt.ylabel("Count")
    plt.title('Histogram')
    plt.savefig("figures/RssiHistogram.pdf")
    # plt.show()


# users- AllusersData object, suposed to contain all users data ,created in findLocation
# resps - object of responder locations which created in findLocation
def calc_error(users,resps,algosInfo):
    users.createKML()
    Responder=resps.list[0]
    rssiHistogram(users.getAllRssi(1))
    # rssiHistogram([1,2,3,3,4,1,2,5,1])
    users.calc_error_Arrays()
    # choose the origin to be the cartesian coordinates of the first responder
    origin=utilities.lla2ecef((Responder.Latitude,Responder.Longitude,0))
    powerset = lambda s: [[x for j, x in enumerate(s) if (i >> j) & 1] for i in xrange(2 ** len(s))]
    for algoset in powerset(LocationsToShowOnWhiteMap)[1:]:
      showOnWhiteMap(users,origin,algoset)
    print max(users.err_arr[1])
    for i in range(3):
        rms=calc_rms(users.err_arr[i])
        algosInfo[i].setRMS(rms)
        print algosInfo[i]
        # print "RMS for Algo" +str(i+1)+" is : " + str(rms)
    # print_CDFV1(data)
    # print_CDFV1_forAll([[data], data[5:],data[:7]])
    data = [np.array(errr) for errr in users.err_arr]
    print_CDFV1_forAll(data)
    if showPlots:
        plt.show()




# users- AllusersData object, suposed to contain all users data
# origin- (x,y) the origin of the cartesian system
#the function plots the locations
def showOnWhiteMap(users,origin,LocationsToShow):
    shapes=['r.','bp','g^']
    f3 = plt.figure()
    ax = f3.add_subplot(111)
    ax.legend()
    #plt.ion()
    if 0 in LocationsToShow:
        ax.plot([user.UserLocations.realLoc.cartesian[0] - origin[0] for user in users.list],
             [user.UserLocations.realLoc.cartesian[1] - origin[1] for user in users.list], 'o', ms=6,color='black', label='FingerPrints', fillstyle='none',linewidth=2 )
    for i in xrange(2,-1,-1):
        if i+1 in LocationsToShow:
            XYArray=users.getCartesianLocations(i,origin)
            #for j in range(len(XYArray[0])):
          #      ax.plot(XYArray[0][:j], XYArray[1][:j], shapes[i],ms=(3+i), label='Algo %i' % (i+1), fillstyle='none')
             #   plt.pause(0.05)
            ax.plot(XYArray[0], XYArray[1], shapes[i], ms=(3 + i), label='Algo %i' % (i + 1), fillstyle='none')
    ax.legend()
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    algosstring="_"+"_".join(str(algo) for algo in LocationsToShow)
    plt.savefig("figures/whiteMap"+algosstring+".svg")
    # plt.pause(0.05)
    # plt.title('Space')
    # plt.plot(arr[0], arr[1], 'ro')
    # plt.plot(arr[0][:10], arr[1][5:15], 'bs')
    # plt.axis([0, 6, 0, 20])
    # plt.show()




# function for tries, not paet from the released code
#TODO:delete
def calc_error_try():
    N=length=10000
    data1=[(i,i+1) for i in xrange(length)]
    data2=[(i,i+i**(0.5)) for i in xrange(length/2)]+[(i,i+i**(0.2)) for i in xrange(length/2,length)]
    # err_array=get_error_array(data1,data2)
    err_file=open("err.txt","r")
    err_array=[abs(float(line)) for line in err_file]
    # print err_array
    # # N=length = len(err_array)
    # # print err_array
    data = np.array(err_array)
    print_CDFV1(data)



