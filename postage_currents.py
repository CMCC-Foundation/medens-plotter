#!/usr/bin/python3


###############################################
#
# global reqs
#
###############################################

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from numpy import meshgrid
from numpy import linspace
import configparser
import numpy as np
import traceback
import datetime
import warnings
import xarray
import numpy
import math
import pdb
import sys
import os

# suppress warnings
warnings.filterwarnings('ignore')

###############################################
#
# initial config
#
###############################################

appname = "PlotPostageCurr"


###############################################
#
# main
#
###############################################

if __name__ == "__main__":

    ###############################################
    #
    # read input parameters
    #
    ###############################################    
    
    # read config file name
    configFile = None
    try:
        configFile = sys.argv[1]
    except:
        print("[ERROR] -- Config file not provided!")
        sys.exit(1)

    # read date
    inputDate = None
    try:
        inputDate = sys.argv[2]
    except:
        inputDate = datetime.datetime.today().strftime("%Y%m%d")

    # read day index
    day_index = None
    try:
        day_index = int(sys.argv[3])
    except:
        day_index = 0

        
    ###############################################
    #
    # parse config file
    #
    ###############################################
        
    configParser = configparser.ConfigParser()
    configParser.read(configFile)

    # paths
    baseEnsPathTemplate = configParser.get("default", "baseEnsPath")
    baseOutputPath = configParser.get("default", "baseOutputPath")    
    inputFileTemplateU = configParser.get("postcardCurrents", "inputFileU")
    inputFileTemplateV = configParser.get("postcardCurrents", "inputFileV")
    inputFilesU = []
    inputFilesV = []
    outputFolder = configParser.get("postcardCurrents", "outputFolder")
    outputFileTemplate = configParser.get("postcardCurrents", "outputName")
    print("[%s] -- Input files set to:" % (appname))
    for i in range(10):
        inputFileU = os.path.join(baseEnsPathTemplate.format(INSTANCE=i, DATE=inputDate), inputFileTemplateU.format(DATE=inputDate))        
        inputFilesU.append(inputFileU)
        print(inputFileU)

        inputFileV = os.path.join(baseEnsPathTemplate.format(INSTANCE=i, DATE=inputDate), inputFileTemplateV.format(DATE=inputDate))        
        inputFilesV.append(inputFileV)
        print(inputFileV)
        
    print("[%s] -- Output folder set to: %s" % (appname, os.path.join(baseOutputPath, outputFolder)))

    # create output folder if needed
    if not os.path.exists(os.path.join(baseOutputPath, outputFolder)):
        os.makedirs(os.path.join(baseOutputPath, outputFolder))

    # black sea mask
    blackSeaMaskLat = configParser.getfloat("default", "blackSeaMaskLat")
    blackSeaMaskLon = configParser.getfloat("default", "blackSeaMaskLon")
    print("[%s] -- Black sea boundaries set to: %s, %s" % (appname, blackSeaMaskLat, blackSeaMaskLon))

    # chart details
    resolution = configParser.get("postcardCurrents", "resolution")
    colorMap = configParser.get("postcardCurrents", "colorMap")
    minValue = configParser.getfloat("postcardCurrents", "minValue")
    maxValue = configParser.getfloat("postcardCurrents", "maxValue")
    levels = configParser.getint("postcardCurrents", "levels")
    print("[%s] -- Resolution set to: %s" % (appname, resolution))
    print("[%s] -- Min Value set to: %s" % (appname, minValue))
    print("[%s] -- Max Value set to: %s" % (appname, maxValue))
    print("[%s] -- Color map set to: %s" % (appname, colorMap))
    print("[%s] -- Levels set to: %s" % (appname, levels))
                    
        
    ###############################################
    #
    # start processing
    #
    ###############################################

    # open files
    datasetsU = []
    for i in inputFilesU:
        datasetsU.append(xarray.open_dataset(i))

    datasetsV = []
    for i in inputFilesV:
        datasetsV.append(xarray.open_dataset(i))

        
    # grid indices
    x = datasetsU[0].nav_lon.transpose().values[0]
    y = datasetsU[0].nav_lat.values[0]

    # lats and lons
    lats = datasetsU[0].nav_lat.transpose().values[0]
    lons = datasetsU[0].nav_lon.values[0]

    # create the grid
    xxx, yyy = meshgrid(lons, lats)

    # define a timestep index (to keep track of the timesteps) and an index to keep track of the day we are in
    timestep_index = 0
    day_current_index = 0
    old_day = str(datasetsU[0].time_counter[0].values).split("T")[0]
    
    # iterate over timesteps
    timestep_index = 0
    for t in datasetsU[0].time_counter:

        # get the date of the current timestep, and optionally update the variable and index keeping track of the day
        d1 = str(t.values).split("T")[0]
        if d1 != old_day:
            old_day = d1
            day_current_index += 1

        # get days string
        d1 = str(t.values).split("T")[0]        
        hour = str(t).split("T")[1].split(":")[0]
        minu = 30
        d2 = "%s:%s" % (hour, minu)
        d3 = "%s, %s" % (d1, d2)
        d4 = "%s_%s%s" % (d1, hour, minu)

        # check if it's the desired day, otherwise move on
        if day_current_index != day_index:
            timestep_index += 1
            continue

        # debug print
        print("[%s] -- Timestep: %s" % (appname, d3))

        # iterate over depth
        depth_index = 0
        for d in datasetsU[0].depthu:

            fig, axes = plt.subplots(nrows=5, ncols=2)
            
            ax_index = 0
            for ax in axes.flat:

                # create basemap
                bmap = Basemap(resolution=resolution,
                               llcrnrlon=lons[0],llcrnrlat=lats[0],
                               urcrnrlon=lons[-1],urcrnrlat=lats[-1], ax=ax)                

                # contourf
                mean_data_0u = datasetsU[ax_index].vozocrtx[timestep_index,depth_index,:,:]
                mean_data_0v = datasetsV[ax_index].vomecrty[timestep_index,depth_index,:,:]                
                mean_data_u = mean_data_0u.where(((mean_data_0u.nav_lat <= blackSeaMaskLat) | (mean_data_0u.nav_lon <= blackSeaMaskLon)))
                mean_data_v = mean_data_0v.where(((mean_data_0v.nav_lat <= blackSeaMaskLat) | (mean_data_0v.nav_lon <= blackSeaMaskLon)))
                mean_data = numpy.sqrt(mean_data_u ** 2 + mean_data_v ** 2)                
                
                contour_levels = linspace(minValue, maxValue, levels)
                im = ax.contourf(xxx, yyy, mean_data, cmap=colorMap, levels=contour_levels, extend='both')
                ax.set_title("Member %s" % ax_index, fontsize = 5, pad = 4)
                ax.axis('off')
                ax_index += 1

                # draw coastlines, country boundaries, fill continents.
                bmap.drawcoastlines(linewidth=0.25)
                bmap.fillcontinents(color='white')
                bmap.drawparallels(range(0, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)
                bmap.drawmeridians(range(-90, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)

                # quiver
                mean_colormesh = bmap.streamplot(xxx, yyy, mean_data_0u, mean_data_0v, linewidth=0.15, arrowsize=0.15, density=2, color='k')
                                    
            # colorbar
            ticks = range(int(minValue), int(maxValue)+1, 1)
            cb = fig.colorbar(im, ax=axes.ravel().tolist(), ticks=ticks, shrink=0.5)
            cb.set_label("Currents (m/s)", fontsize = 3)
            cb.ax.tick_params(labelsize=3)
            for t in cb.ax.get_xticklabels():
                t.set_fontsize(1)
            
            # title
            finalDate = "%s:30" % (d3.split(":")[0])
            plt.suptitle("Currents at %s m.\nTimestep: %s" % (int(d), finalDate), fontsize = 5)
                
            # save file
            di = datasetsU[0].depthu.values.tolist().index(d)
            filename = os.path.join(baseOutputPath, outputFolder, outputFileTemplate.format(DATE=d4, DEPTH=di))                    
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            print("File %s generated" % filename)
            plt.close()
            
            # increment depth
            depth_index += 1

        # increment timestep
        timestep_index += 1
