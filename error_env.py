# import numpy as np
# import matplotlib.pyplot as plt
#
# N = 100
# # Z = np.random.normal(size = N)
# Z = np.array([0,1,2,3,4,5,6,7,8,9,10,11,12,13])
# print type(Z)
# # method 1
# H,X1 = np.histogram( Z, bins = 10, normed = True )
# print H
# dx = X1[1] - X1[0]
# F1 = np.cumsum(H)*dx
# #method 2
# X2 = np.sort(Z)
# F2 = np.array(range(N))/float(N)
#
# plt.plot(X1[1:], F1)
# plt.plot(X2, F2)
# plt.show()


import numpy as np
import matplotlib.pyplot as plt
import math
import utilities

# gets two points and return the distace between them.
def distance_of_2_points(estimatedLocation,realLocation):
    return math.hypot(estimatedLocation[0] - realLocation[0], estimatedLocation[1] - realLocation[1])

def get_error_array(data1,data2):
    return [distance_of_2_points(data1[i],data2[i]) for i in xrange(len)]


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
    # # plt.plot(X2, F2)
    # axes = plt.gca()
    # # print max(arr)
    # axes.set_xlim([0, max(arr)])
    # axes.set_xlim([0, 15])
    # plt.show()




def print_CDFV1_forAll(arrs):
    fig = plt.figure()
    ax = plt.subplot(111)

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
    plt.show()




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
    plt.show()


def calc_rms(arr):
    return (sum(map(lambda x:x*x,arr))/(1.0*len(arr)))**0.5

# def calc_error(estimatedLocationFile,realLocationFile):
# def calc_error(UsereLst):
#     # estimatedLocationFile=LoadData(estimatedLocationFile)
#     # realLocationFile=LoadData(realLocationFile)
#     estimatedLocationArr=estimatedLocationFile
#     realLocationArr=realLocationFile
#     err_arr=[]
#     for i in xrange(len(estimatedLocationArr)): #assume both arr have the same length
#         estimatedCartesian= lla2ecef((estimatedLocationArr[i][0],estimatedLocationArr[i][1],estimatedLocationArr[i][2]))
#         realCartesian = lla2ecef((realLocationArr[i][0], realLocationArr[i][1], realLocationArr[i][2]))
#         err_arr.append(distance_of_2_points((estimatedCartesian[0],estimatedCartesian[1]),(realCartesian[0],realCartesian[1])))
#     data = np.array(err_array)
#     print "RMS is:" + calc_rms(err_arr)
#     print_CDFV1(data)


def calc_error(UsereLst):
    showOnWhiteMap(UsereLst)
    err_arr=[[],[],[]]
    for user in UsereLst:
        if user.valid!=1:
            continue
        for i in range(3):
            estimatedCartesian=utilities.lla2ecef((user.algoLocations[i][0],user.algoLocations[i][1],0))
            realCartesian=utilities.lla2ecef((user.realLat,user.realLon,0))
            # if distance_of_2_points((estimatedCartesian[0], estimatedCartesian[1]),(realCartesian[0], realCartesian[1])) > 100:
            #     continue
            err_arr[i].append(distance_of_2_points((estimatedCartesian[0], estimatedCartesian[1]), (realCartesian[0], realCartesian[1])))
            # err_arr[i].append(distance_of_2_points((estimatedCartesian[0]/100.0, estimatedCartesian[1]/100.0), (realCartesian[0]/100.0, realCartesian[1]/100.0)))
    # print err_arr[2]
    # print max(err_arr[2])
    data = [np.array(errr) for errr in err_arr]
    for i in range(3):
        print "RMS for " +str(i+1)+" is : " + str(calc_rms(err_arr[i]))
    # print_CDFV1(data)
    # print_CDFV1_forAll([[data], data[5:],data[:7]])
    print_CDFV1_forAll(data)




def showOnWhiteMap(UsereLst):
    arr=[[],[]]
    for user in UsereLst:
        if user.valid != 1:
            continue
        i=2
        estimatedCartesian = utilities.lla2ecef((user.algoLocations[i][0], user.algoLocations[i][1], 0))
        arr[0].append(estimatedCartesian[0])
        arr[1].append(estimatedCartesian[1])
    plt.plot(arr[0], arr[1], 'ro')
    # plt.plot(arr[0][:10], arr[1][5:15], 'bs')
    # plt.axis([0, 6, 0, 20])
    plt.show()





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
    # print_CDFV2(err_array)
    # Z = np.array(err_array)
    # # values, base = np.histogram(data, bins=50, normed = True)
    # # # evaluate the cumulative
    # # cumulative = np.cumsum(values)
    # # # plot the cumulative function
    # # plt.plot(base[:-1], cumulative, c='blue')
    # # plt.show()
    # # method 1
    # H,X1 = np.histogram( Z, bins = length/10, normed = True )
    # # print H
    # dx = X1[1] - X1[0]
    # F1 = np.cumsum(H)*dx
    # #method 2
    # X2 = np.sort(Z)
    # F2 = np.array(range(N))/float(N)
    #
    # plt.plot(X1[1:], F1,"r")
    # # plt.plot(X2, F2)
    # axes = plt.gca()
    # axes.set_xlim([0,10])
    # x2 = []
    # y2 = []
    # y = 0
    # err_file = open("err.txt", "r")
    # err_array = [abs(float(line)) for line in err_file]
    # sorted = np.sort(err_array)
    # for x in sorted:
    #     x2.extend([x, x])
    #     y2.append(y)
    #     y += 1.0 / len(err_array)
    #     y2.append(y)
    # plt.plot(x2, y2,"g")
    # axes = plt.gca()
    # axes.set_xlim([0, 10])
    # plt.show()
    # plt.show()


# some fake data
# data = np.random.randn(1000)
# data = np.array([0,1,1,1,1,1,1,1,1,1,2,3,4,5,6,7,8,9,10,11,12,13])
# data = np.array([0,1,1,1,1,1,1,1,1,1,2,3,4,5,6,7,8,9,10,11,12,13])
# print data
# # evaluate the histogram
# values, base = np.histogram(data, bins=50)
# #evaluate the cumulative
# cumulative = np.cumsum(values)
# # plot the cumulative function
# plt.plot(base[:-1], cumulative, c='blue')
# #plot the survival function
# plt.plot(base[:-1], len(data)-cumulative, c='green')

# plt.show()











# err_file=open("err.txt","r")
# err_array=[abs(float(line)) for line in err_file]
# sorted=np.sort(err_array)
# x2 = []
# y2 = []
# y = 0
# for x in sorted:
#     x2.extend([x,x])
#     y2.append(y)
#     y += 1.0 / len(err_array)
#     y2.append(y)
# plt.plot(x2,y2)
# axes = plt.gca()
# axes.set_xlim([0, 10])
# plt.show()
# print "here"





# import numpy as np
# import statsmodels.api as sm # recommended import according to the docs
# import matplotlib.pyplot as plt
#
# err_file=open("err.txt","r")
# err_array=[abs(float(line)) for line in err_file]
# # sample = np.random.uniform(0, 1, 50)
# sample = np.array(err_array)
# ecdf = sm.distributions.ECDF(sample)
#
# x = np.linspace(min(sample), max(sample))
# y = ecdf(x)
# plt.step(x, y)
# plt.show()








# from bisect import bisect_left
#
# class discrete_cdf:
#     def __init__(data):
#         self._data = data # must be sorted
#         self._data_len = float(len(data))
#
#     def __call__(point):
#         return (len(self._data[:bisect_left(self._data, point)]) /
#                 self._data_len)
# err_file=open("err.txt","r")
# err_array=[abs(float(line)) for line in err_file]
# cdf = discrete_cdf(sorted(err_array))
# xvalues = range(0, max(your_data))
# yvalues = [cdf(point) for point in xvalues]
# plt.plot(xvalues, yvalues)