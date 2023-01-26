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

appname = "PlotSalinity"


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
    basePath = configParser.get("default", "basePath")
    baseOutputPath = configParser.get("default", "baseOutputPath")
    meanFile = os.path.join(basePath, inputDate, configParser.get("salinity", "meanFile"))
    stdFile = os.path.join(basePath, inputDate, configParser.get("salinity", "stdFile"))
    outputFolder = configParser.get("salinity", "outputFolder")
    outputFileTemplate = configParser.get("salinity", "outputName")
    print("[%s] -- Mean file set to: %s" % (appname, meanFile))
    print("[%s] -- Std file set to: %s" % (appname, stdFile))

    # create output folder if needed
    dst = os.path.join(baseOutputPath, outputFolder.format(DATE=inputDate))
    if not os.path.exists(dst):
        os.makedirs(dst, exist_ok=True)
    print("[%s] -- Output folder set to: %s" % (appname, dst))

    # black sea mask
    blackSeaMaskLat = configParser.getfloat("default", "blackSeaMaskLat")
    blackSeaMaskLon = configParser.getfloat("default", "blackSeaMaskLon")
    print("[%s] -- Black sea boundaries set to: %s, %s" % (appname, blackSeaMaskLat, blackSeaMaskLon))
    
    # chart details
    meanColorMap = configParser.get("salinity", "meanColorMap")
    meanMinValue = configParser.getfloat("salinity", "meanMinValue")
    meanMaxValue = configParser.getfloat("salinity", "meanMaxValue")
    meanLevels = configParser.getint("salinity", "meanLevels")
    stdColorMap = configParser.get("salinity", "stdColorMap")
    stdMinValue = configParser.getfloat("salinity", "stdMinValue")
    stdMaxValue = configParser.getfloat("salinity", "stdMaxValue")
    stdLevels = configParser.getint("salinity", "stdLevels")    
    resolution = configParser.get("salinity", "resolution")
    print("[%s] -- Mean color map set to: %s" % (appname, meanColorMap))
    print("[%s] -- Mean min value set to: %s" % (appname, meanMinValue))
    print("[%s] -- Mean max value set to: %s" % (appname, meanMaxValue))
    print("[%s] -- Std color map set to: %s" % (appname, stdColorMap))
    print("[%s] -- Std min value set to: %s" % (appname, stdMinValue))
    print("[%s] -- Std max value set to: %s" % (appname, stdMaxValue))
    print("[%s] -- Resolution set to: %s" % (appname, resolution))

    
    ###############################################
    #
    # start processing
    #
    ###############################################
    
    # open dataset STD    
    ds1 = xarray.open_dataset(stdFile)

    # open dataset MEAN
    ds2 = xarray.open_dataset(meanFile)
    
    # grid indices
    x = ds1.lon.values
    y = ds1.lat.values

    # lats and lons
    lats = ds1.lat.transpose().values
    lons = ds1.lon.values
    
    # central points
    clat = (lats[-1] - lats[0]) / 2
    clon = (lons[-1] - lons[0]) / 2
    
    # create the grid
    xxx, yyy = meshgrid(lons, lats)

    # define a timestep index (to keep track of the timesteps) and an index to keep track of the day we are in
    timestep_index = 0
    day_current_index = 0
    old_day = str(ds1.time[0].values).split("T")[0]

    # iterate over the timestamps
    for t in ds1.time.values:

        # get the date of the current timestep, and optionally update the variable and index keeping track of the day
        d1 = str(t).split("T")[0]
        if d1 != old_day:
            old_day = d1
            day_current_index += 1

        # get days string
        d1 = str(t).split("T")[0]        
        hour = str(t).split("T")[1].split(":")[0]
        minu = str(t).split("T")[1].split(":")[1]
        d2 = "%s:%s" % (hour, minu)
        d3 = "%s, %s" % (d1, d2)
        d4 = "%s_%s30" % (d1, hour)

        # check if it's the desired day, otherwise move on
        if day_current_index != day_index:
            timestep_index += 1
            continue
        
        # iterate over depth
        depth_index = 0
        for d in ds1.depth.values:
            
            # initialise the map
            bmap = Basemap(resolution=resolution,
                           llcrnrlon=lons[0],llcrnrlat=lats[0],
                           urcrnrlon=lons[-1],urcrnrlat=lats[-1])
            
            fig, ax = plt.subplots()
            
            ############################################
            #
            # Mean
            #
            ############################################
            
            # contour MEAN
            meanLevelsContour = linspace(meanMinValue, meanMaxValue, num=meanLevels)            
            mean_data_0 =  ds2.vosaline[timestep_index,depth_index,:,:]
            mean_data_1 = mean_data_0
            mean_data = mean_data_1.values            
            mean_colormesh = bmap.contour(xxx, yyy, mean_data, cmap=meanColorMap, levels=meanLevelsContour, linewidths=0.15, extend='both')
            
            ############################################
            #
            # Std
            #
            ############################################

            # contourf STD
            stdLevelsContourf = linspace(stdMinValue, stdMaxValue, num=stdLevels)
            std_data_0 =  ds1.vosaline[timestep_index,depth_index,:,:]
            std_data_1 = std_data_0.where(((std_data_0.lat <= blackSeaMaskLat) | (std_data_0.lon <= blackSeaMaskLon)))
            std_data = std_data_1.values
            std_colormesh = bmap.contourf(xxx, yyy, std_data, cmap=stdColorMap, levels=stdLevelsContourf, extend='both')
            
            ############################################
            #
            # Colorbars
            #
            ############################################
            
            # colorbar MEAN
            meanTicks = range(int(meanMinValue), int(meanMaxValue)+1)
            mean_cb = bmap.colorbar(mean_colormesh, ticks=meanTicks, location="right", shrink = 0.2)
            mean_cb.set_label("Mean salinity (psu)", fontsize=5)
            for t in mean_cb.ax.get_yticklabels():
                t.set_fontsize(3)
            
            # colorbar STD
            stdTicks = numpy.arange(stdMinValue, stdMaxValue+0.1, 0.1)
            std_cb = fig.colorbar(std_colormesh, location='bottom', ticks = stdTicks, pad = -0.35, shrink = 0.5)
            std_cb.set_label("Spread", fontsize=5)
            for t in std_cb.ax.get_xticklabels():
                t.set_fontsize(3)
        
            ############################################
            #
            # General configuration
            #
            ############################################            
                
            # title
            finalDate = "%s:30" % (d3.split(":")[0])
            plt.title("Ensemble mean and spread for salinity at %s m.\nTimestep: %s" % (int(d), finalDate), fontsize = 5)
                            
            # draw coastlines, country boundaries, fill continents.
            bmap.drawcoastlines(linewidth=0.15)
            bmap.fillcontinents()
            bmap.drawparallels(range(0, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)
            bmap.drawmeridians(range(-90, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)
                
            # save file
            di = ds1.depth.values.tolist().index(d)
            filename = os.path.join(dst, outputFileTemplate.format(DATE=d4, DEPTH=di))
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            print("File %s generated" % filename)

            # clear memory
            fig.clear()
            plt.close(fig)

            # increment depth_index
            depth_index += 1

        # increment timestep index
        timestep_index += 1
