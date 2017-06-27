import numpy as np
import matplotlib.pyplot as plt
import utilities


showPlots=1 # flag which decide if show (1) plots or not (0)
LocationsToShowOnWhiteMap=[0]#,1,2,3]
algoColoreLst=["blue", "red", "green"] # the colors of the algorithms im the results
algoNameLst=["1 Basic RSSI Algorithm","2 RSSI + FTM Algorithm","3 Trilateration Algorithm"]

def calcCDF(arr):
    Z=arr
    length = len(arr)*100
    H, X1 = np.histogram(Z, bins=length , normed=True)
    dx = X1[1] - X1[0]
    F1 = np.cumsum(H) * dx
    return X1[1:], F1



def ErrorsCDF(arrs):
    f2 = plt.figure()
    ax = f2.add_subplot(111)
    ax.legend()
    for i in range(len(arrs)):
        x,f=calcCDF(arrs[i])
        ax.plot(x, f, label=algoNameLst[i], color=algoColoreLst[i])
        labelGraph(x,f,ax,i)
    ax.legend()
    plt.xlabel("Localization Error [m]")
    plt.ylabel("CDF")
    plt.title('Errors Empirical CDF')
    plt.savefig(utilities.folderName+"/Errors_CDF.svg")
    ax.yaxis.set_ticks(np.arange(0, 1.05, 0.05))
    ax.xaxis.set_ticks(np.arange(0, 22, 1))
    plt.grid(True)


def calc_rms(arr):
    return (sum(map(lambda x:x*x,arr))/(1.0*len(arr)))**0.5


def add_label(ax,x,y,label,algo=10):
    positionLst=[(35,-30),(2,33),(50,-26)]
    # for 10DB:
    positionLst = [(15, 15), (8, 33), (50, -26)]
    position = (-12,12)
    color='yellow'
    if algo!=10:
        color=algoColoreLst[algo]
        position=positionLst[algo]
    ax.annotate(
       label,
        xy=(x, y), xytext=position,
        textcoords='offset points',fontsize=8, ha='right', va='bottom',
        bbox=dict(boxstyle='round,pad=0.3', fc=color, alpha=0.4),
        arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'))

def labelGraph(x,y,ax,algo):
    i = utilities.minDiffEntry(y, 0.67)
    add_label(ax, x[i], y[i], "{2}:({1},{0})".format(round(y[i], 2), round(x[i], 2), r'$\sigma$'),algo)
    i = utilities.minDiffEntry(y, 0.9)
    add_label(ax, x[i], y[i], "({1},{0})".format(round(y[i], 2), round(x[i], 2)),algo)
    i = utilities.minDiffEntry(y, 0.95)
    add_label(ax, x[i], y[i], "({1},{0})".format(round(y[i], 2), round(x[i], 2)),algo)


def rssiCDF(arr):
    f1 = plt.figure()

    x, f = calcCDF(arr)
    ax1 = f1.add_subplot(111)
    ax1.plot(x, f)#, label='$Algo %i$' % (i + 1))
    i=utilities.minDiffEntry(f,0.67)
    labelGraph(x, f, ax1,10)
    # plt.xticks(range(len(set(arr))))
    ax1.yaxis.set_ticks(np.arange(0, 1.05, 0.05))
    ax1.legend()
    plt.xlabel("RSSI [dbm]")
    plt.ylabel("CDF")
    plt.title('Empirical CDF')
    plt.savefig(utilities.folderName+"RssiCDF.svg")
    plt.grid(True)



def calc_error(users,resps,algosInfo):
    users.createKML()
    Responder=resps.list[0]
    rssiCDF(users.getAllRssi(1))#1 for ignore from -120 db, 0 to include them.

    users.calc_error_Arrays()
    # choose the origin to be the cartesian coordinates of the first responder
    #whitemap part
    # origin=utilities.lla2ecef((Responder.Latitude,Responder.Longitude,0))
    # powerset = lambda s: [[x for j, x in enumerate(s) if (i >> j) & 1] for i in xrange(2 ** len(s))]
    # for algoset in powerset(LocationsToShowOnWhiteMap)[1:]:
    #   showOnWhiteMap(users,origin,algoset)

    # print max(users.err_arr[1])
    # runAllLst=[]
    # if utilities.runAll:
    for i in range(3):
        rms=calc_rms(users.err_arr[i])
        algosInfo[i].setRMS(rms)
        print algosInfo[i]
        print "time per location: "+str(round(algosInfo[i].time*1000/(users.size+0.0),4))

    print "total users: "+ str(users.size)
    data = [np.array(errr) for errr in users.err_arr]
    ErrorsCDF(data)
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
             [user.UserLocations.realLoc.cartesian[1] - origin[1] for user in users.list], 'o', ms=6,color='black', label='Real Location', fillstyle='none',linewidth=2 )
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
    plt.savefig(utilities.folderName+"whiteMap"+algosstring+".svg")






