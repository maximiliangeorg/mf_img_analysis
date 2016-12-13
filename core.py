# -*- coding: utf-8 -*-

import numpy as np
import mahotas as mh
import matplotlib.pyplot as plt
import math
import sys
from operator import itemgetter
from matplotlib.backends.backend_pdf import PdfPages
from os import listdir

default = True
validanswer = False
while not validanswer:
    userin = raw_input("do you want to use the user_input.py file? (y/n)")
    if userin == "y":
        from user_input import *
        print "continue with user input"
        validanswer = True
        default = False
    elif userin == "n":
        print "continue with default settings"
        validanswer = True
    else:
        print "invalid input, type 'y' or 'n'"
        validanswer = False


plt.gcf().clear()


def listdir_nohidden(path):
    newlist = []
    for f in listdir(path):
        if not f.startswith('.'):
             newlist.append(f)
    return newlist
days = dict()
inputimages = dict()
imcount = 0
path = "input/"
daystemp = listdir_nohidden(path)

for x in range(len(daystemp)):
    days[x] = dict()
    days[x][0] = str(daystemp[x])
    path = "input/" + str(days[x][0]) + "/"
    concentrationstemp = listdir_nohidden(str(path))
    for n in range(len(concentrationstemp)):
        days[x][n+1] = dict()
        days[x][n+1][0] = str(concentrationstemp[n])
        path = "input/" + str(days[x][0]) + "/" + str(days[x][n+1][0]) + "/"
        imagestemp = listdir_nohidden(str(path))
        for i in range(len(imagestemp)):
            path = "input/" + str(days[x][0]) + "/" + str(days[x][n+1][0]) + "/" + str(imagestemp[i])
            print "loaded: " + str(path)
            days[x][n+1][i+1] = mh.imread(str(path))
            days[x][n+1][i+1] = mh.colors.rgb2gray(days[x][n+1][i+1])
            days[x][n+1][i+1] = days[x][n+1][i+1].astype(np.uint8)
            inputimages[imcount] = dict()
            # index 0 is image
            inputimages[imcount][0] = days[x][n+1][i+1]
            # index 1 is day
            inputimages[imcount][1] = days[x][0]
            # index 2 is concentration
            inputimages[imcount][2] = days[x][n+1][0]
            # index 3 is cell area
            inputimages[imcount][3] = 0
            imcount += 1

pp = PdfPages('protocol.pdf')


def cut(image, cuts):
    xcord = image.shape[1]
    ycord = image.shape[0]
    xcord = float(xcord)
    ycord = float(ycord)
    p = 0
    q = 0.0
    k = 0.0
    cuts = float(cuts)
    imdict = dict()
    while p < (cuts ** 2):
        yslicestart = int((k/cuts) * ycord)
        ysliceend = int(((k+1)/cuts) * ycord)
        xslicestart = int((q/cuts) * xcord)
        xsliceend = int(((q+1)/cuts) * xcord)
        imageslice = image[yslicestart:ysliceend, xslicestart:xsliceend]
        imdict[int(p)] = imageslice
        q += 1
        if q == cuts:
            k += 1
            q = 0.0
        p += 1
    return imdict


def adjustsize(origimage, slicedimage, cuts):
    if origimage.shape[0] % cuts != 0 or origimage.shape[1] % cuts != 0:
        allx = []
        ally = []
        for im in range(len(slicedimage)):
            allx.append(slicedimage[im].shape[1])
            ally.append(slicedimage[im].shape[0])
        allx.sort()
        ally.sort()
        xmin = allx[0]
        ymin = ally[0]
        for im in range(len(slicedimage)):
            slicedimage[im] = slicedimage[im][0:ymin, 0:xmin]


def getmins(image):
    minvalues = []
    for h in range(len(image)):
        minvalues.append(image[h].min())
    minvalues.sort()
    return minvalues


def getlimit(image):
    minvalues = getmins(image)
    gaps = []
    avmin = 0
    limit = 0
    for f in range(len(minvalues)):
        avmin = avmin + minvalues[f]
    avmin /= len(minvalues)

    def getmaxdif():
        for g in range(len(minvalues)-1):
            gaps.append(minvalues[g+1]-minvalues[g])
        gaps.sort()
        return gaps[-1]

    def setnewmaxdif():
        gaps.pop(-1)
        return gaps[-1]
    maxdif = getmaxdif()
    while limit == 0:
        for f in range(len(minvalues)-1):
            if minvalues[f+1]-minvalues[f] == maxdif:
                if minvalues[f+1]-minvalues[f] < avmin:
                    limit = minvalues[f]
                    return limit
        maxdif = setnewmaxdif()


def findrim(image, limitmod):
    ignore = []
    limit = getlimit(image) + limitmod
    for a in range(len(image)):
        if image[a].min() <= limit:
            ignore.append(a)
    return ignore


def applyth(image):
    newim = dict()
    for th in range(len(image)):
        newim[th] = mh.rc(image[th])
    return newim


def applygauss(image, intensity):
    newim = dict()
    for gau in range(len(image)):
        newim[gau] = mh.gaussian_filter(image[gau], intensity)
        newim[gau] = newim[gau].astype(np.uint8)
    return newim


def printprogress(iteration, total, prefix='', suffix='', decimals=2, barLength=100):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barlength   - Optional  : character length of bar (Int)
    """
    formatStr = "{0:." + str(decimals) + "f}"
    percent = formatStr.format(100 * (iteration / float(total)))
    filledLength = int(round(barLength * iteration / float(total)))
    bar = '█' * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


def measure(origimage, cuts, gaussintensity, iteration):
    image = cut(origimage, cuts)
    adjustsize(origimage, image, cuts)
    if not default and iteration in modifyselection:
        limitmod = modifyselection[iteration]
    else:
        limitmod = 0
    ignore = findrim(image, limitmod)
    if rim and len(ignore) <= (cuts ** 2)*0.33:
        while len(ignore) <= (cuts ** 2)*0.33:
            limitmod += 3
            ignore = findrim(image, limitmod)
    elif len(ignore) >= (cuts ** 2)*0.66:
        while len(ignore) >= (cuts ** 2)*0.66:
            limitmod -= 3
            ignore = findrim(image, limitmod)
    avmod = len(ignore)
    threshold = applyth(image)
    if not default and iteration in increasegauss:
        usedgaussintensity = gaussintensity ** increasegauss[iteration]
    else:
        usedgaussintensity = gaussintensity
    gauss = applygauss(image, usedgaussintensity)
    totalcellarea = 0.0
    subcount = int(math.sqrt(len(image)))
    for r in range(len(image)):
        printprogress((iteration * len(image) + r + 1), (len(inputimages) * len(image)),
                      prefix="processing " + str(len(inputimages)-len(badimages)) + " images", suffix="complete")
        if len(ignore) == 0 or r != ignore[0]:
            cellarea = 0.0
            area = image[r].shape[0] * image[r].shape[1]

            gaussth = gauss[r] > threshold[r]

            for array in gaussth:
                for pixel in array:
                    # variabel machen wenn Zellen hell
                    if pixel == 0:
                        cellarea += 1

            cellperc = (cellarea / area)
            inputimages[iteration][3] = cellperc * 100

            rmin = mh.regmin(gaussth)
            rmin = rmin.astype(np.uint8)

            plt.subplot(subcount, subcount, r+1)
            plt.axis('off')
            plt.imshow(mh.overlay(image[r], rmin))

            totalcellarea += cellperc
        else:
            plt.subplot(subcount, subcount, r+1)
            plt.axis('off')
            ignore.pop(0)
    plt.text(-7, 7, str("ID: " + str(iteration) + ", day: " + str(inputimages[iteration][1]) + ", " + str(substancename) + " concentration: " + str(
        inputimages[iteration][2]) + " %"))
    plt.text(-7, 6.5, str(cellname) + " coverage: " + str(round((totalcellarea / ((len(image)) - avmod)) * 100, 2)) + " %")
    plt.axis('off')
    pp.savefig()
    plt.gcf().clear()

if not default:
    rim = boundary
    substancename = substance
    cellname = cells
else:
    rim = True
    substancename = ""
    cellname = ""
    badimages = []

for s in range(len(inputimages)):
    if s not in badimages:
        measure(inputimages[s][0], 6, 2, s)

print "creating pdf file..."


def getgroups(inputdata):
    groups = dict()
    groups[0] = dict()
    groups[0][0] = inputdata[0]
    grcount = 0
    grmemcount = 0
    for c in range(len(inputdata)-1):
        if groups[grcount][grmemcount][2] == inputdata[c+1][2]:
            grmemcount += 1
            groups[grcount][grmemcount] = inputdata[c+1]
        else:
            grcount += 1
            grmemcount = 0
            groups[grcount] = dict()
            groups[grcount][grmemcount] = inputdata[c+1]
    return groups


def sumgroup(group):
    singlelastadded = False
    gsum = group[0][3]
    daycount = 1
    groupav = []
    for gr in range(len(group)-1):
        singlelastadded = False
        if group[gr][1] == group[gr+1][1]:
            gsum += group[gr+1][3]
            daycount += 1
        elif x == len(group)-1:
            groupav.append(gsum/daycount)
            groupav.append(group[gr+1][3])
            singlelastadded = True
        else:
            groupav.append(gsum/daycount)
            gsum = group[gr+1][3]
            daycount = 1
    if not singlelastadded:
        groupav.append(gsum / daycount)
    return groupav

concentrationgroups = list()
for x in range(len(inputimages)):
    concentrationgroups.append(inputimages[x])
concentrationgroups = sorted(concentrationgroups, key=itemgetter(2, 1))
concentrationgroups = getgroups(concentrationgroups)
congroupav = dict()
for x in range(len(concentrationgroups)):
    congroupav[x] = (sumgroup(concentrationgroups[x]))

daysdata = []
for x in range(len(inputimages)):
    daysdata.append(inputimages[x][1])
uniquedays = list(sorted(set(daysdata)))

condata = []
for x in range(len(inputimages)):
    condata.append(float(inputimages[x][2]))
uniquecons = list(sorted(set(condata)))

conatday = dict()
for x in range(len(congroupav[0])):
    conatday[x] = list()
    for y in range(len(congroupav)):
        conatday[x].append(congroupav[y][x])

for x in range(len(congroupav)):
    plt.plot(uniquedays, list(congroupav[x]), label=str(uniquecons[x]) + " % " + str(substancename))
    plt.title("all " + str(substancename) + " groups over total time")
    plt.xlabel("days since experiment has started")
    plt.ylabel(str(cellname) + " cell coverage in %")
    plt.legend(loc='upper left')

pp.savefig()
plt.gcf().clear()

for x in range(len(conatday)):
    plt.plot(uniquecons, list(conatday[x]))
    plt.title(str(substancename) + " group comparison at day " + str(uniquedays[x]))
    plt.xlabel(str(substancename) + " concentration in %")
    plt.ylabel(str(cellname) + " cell coverage in %")
    pp.savefig()
    plt.gcf().clear()

pp.close()
