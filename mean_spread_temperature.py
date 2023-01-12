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
import xarray
import numpy
import math
import pdb
import sys
import os


###############################################
#
# initial config
#
###############################################

appname = "PlotTemperature"


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
    meanFile = os.path.join(basePath, inputDate, configParser.get("temperature", "meanFile"))
    stdFile = os.path.join(basePath, inputDate, configParser.get("temperature", "stdFile"))
    outputFolder = configParser.get("temperature", "outputFolder")
    outputFileTemplate = configParser.get("temperature", "outputName")
    print("[%s] -- Mean file set to: %s" % (appname, meanFile))
    print("[%s] -- Std file set to: %s" % (appname, stdFile))
    print("[%s] -- Output folder set to: %s" % (appname, os.path.join(baseOutputPath, outputFolder)))

    # create output folder if needed
    if not os.path.exists(os.path.join(baseOutputPath, outputFolder)):
        os.makedirs(os.path.join(baseOutputPath, outputFolder))
    
    # chart details
    meanColorMap = configParser.get("temperature", "meanColorMap")
    meanMinValue_surf = configParser.getfloat("temperature", "meanMinValue_surf")
    meanMaxValue_surf = configParser.getfloat("temperature", "meanMaxValue_surf")
    meanMinValue_bott = configParser.getfloat("temperature", "meanMinValue_bott")
    meanMaxValue_bott = configParser.getfloat("temperature", "meanMaxValue_bott")
    meanLevels = configParser.getint("temperature", "meanLevels")
    stdColorMap = configParser.get("temperature", "stdColorMap")
    stdMinValue_surf = configParser.getfloat("temperature", "stdMinValue_surf")
    stdMaxValue_surf = configParser.getfloat("temperature", "stdMaxValue_surf")
    stdMinValue_bott = configParser.getfloat("temperature", "stdMinValue_bott")
    stdMaxValue_bott = configParser.getfloat("temperature", "stdMaxValue_bott")    
    stdLevels = configParser.getint("temperature", "stdLevels")    
    resolution = configParser.get("temperature", "resolution")
    print("[%s] -- Mean color map set to: %s" % (appname, meanColorMap))
    print("[%s] -- Mean min value (surf) set to: %s" % (appname, meanMinValue_surf))
    print("[%s] -- Mean max value (surf) set to: %s" % (appname, meanMaxValue_surf))
    print("[%s] -- Mean min value (bott) set to: %s" % (appname, meanMinValue_bott))
    print("[%s] -- Mean max value (bott) set to: %s" % (appname, meanMaxValue_bott))
    print("[%s] -- Std color map set to: %s" % (appname, stdColorMap))
    print("[%s] -- Std min value (surf) set to: %s" % (appname, stdMinValue_surf))
    print("[%s] -- Std max value (surf) set to: %s" % (appname, stdMaxValue_surf))
    print("[%s] -- Std min value (bott) set to: %s" % (appname, stdMinValue_bott))
    print("[%s] -- Std max value (bott) set to: %s" % (appname, stdMaxValue_bott))    
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

    # iterate over the timestamps
    timestep_index = 0
    for t in ds1.time.values:

        d1 = str(t).split("T")[0]        
        hour = str(t).split("T")[1].split(":")[0]
        minu = str(t).split("T")[1].split(":")[1]
        d2 = "%s:%s" % (hour, minu)
        d3 = "%s, %s" % (d1, d2)
        d4 = "%s_%s%s" % (d1, hour, minu)
        
        # iterate over depth
        depth_index = 0
        for d in ds1.depth.values:
            
            # initialise the map
            bmap = Basemap(resolution=resolution,
                           llcrnrlon=lons[0],llcrnrlat=lats[0],
                           urcrnrlon=lons[-1],urcrnrlat=lats[-1])

            if depth_index < 2:
                meanMinValue = meanMinValue_surf
                meanMaxValue = meanMaxValue_surf
                stdMinValue = stdMinValue_surf
                stdMaxValue = stdMaxValue_surf                
            else:
                meanMinValue = meanMinValue_bott
                meanMaxValue = meanMaxValue_bott
                stdMinValue = stdMinValue_bott
                stdMaxValue = stdMaxValue_bott                
            
            
            ############################################
            #
            # Mean
            #
            ############################################                                            

            # contour MEAN
            meanLevelsContour = linspace(meanMinValue, meanMaxValue, num=meanLevels)            
            mean_data_0 =  ds2.votemper[timestep_index,depth_index,:,:]
            mean_data_1 = mean_data_0.where(mean_data_0 >= meanMinValue, other=meanMinValue).where(mean_data_0 <= meanMaxValue, other=meanMaxValue)
            mean_data = mean_data_1.values                        
            mean_colormesh = bmap.contour(xxx, yyy, mean_data, cmap=meanColorMap, levels=meanLevelsContour, linewidths=0.3, vmin=meanMinValue, vmax=meanMaxValue)

            # colorbar MEAN
            meanTicks = range(int(meanMinValue), int(meanMaxValue)+1)
            mean_cb = bmap.colorbar(mean_colormesh, ticks=meanTicks, location='right')
            mean_cb.set_label("Mean Temperature (degC)", fontsize=5)
            for t in mean_cb.ax.get_yticklabels():
                t.set_fontsize(5)
           
            ############################################
            #
            # Std
            #
            ############################################                                            

            # contourf STD
            stdLevelsContourf = linspace(stdMinValue, stdMaxValue, num=stdLevels)
            std_data_0 =  ds1.votemper[timestep_index,depth_index,:,:]
            std_data_1 = std_data_0.where(std_data_0 >= stdMinValue, other=stdMinValue).where(std_data_0 <= stdMaxValue, other=stdMaxValue)
            std_data = std_data_1.values
            std_colormesh = bmap.contourf(xxx, yyy, std_data, cmap=stdColorMap, levels=stdLevelsContourf, vmin=stdMinValue, vmax=stdMaxValue)
            
            # colorbar STD
            stdTicks = numpy.arange(stdMinValue, stdMaxValue+0.1, 0.1)
            std_cb = bmap.colorbar(std_colormesh, location='bottom', ticks = stdTicks)
            std_cb.set_label("Spread", fontsize=5)
            for t in std_cb.ax.get_xticklabels():
                t.set_fontsize(5)
                
            ############################################
            #
            # General configuration
            #
            ############################################                                            

            # title
            finalDate = "%s:30" % (d3.split(":")[0])
            plt.title("Ensemble spread for Sea temperature at %s m.\nTimestep: %s" % (int(d), finalDate), fontsize = 5)
            
            # draw coastlines, country boundaries, fill continents.
            bmap.drawcoastlines(linewidth=0.25)
            bmap.fillcontinents(color='white')

            # save file
            di = ds1.depth.values.tolist().index(d)
            filename = os.path.join(baseOutputPath, outputFolder, outputFileTemplate.format(DATE=d4, DEPTH=di))            
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            print("File %s generated" % filename)
            plt.clf()
            
            # increment depth_index
            depth_index += 1
            
        # increment timestep index
        timestep_index += 1
