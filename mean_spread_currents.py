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

appname = "Plotcurrents"


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
    meanUFile = os.path.join(basePath, inputDate, configParser.get("currents", "meanUFile"))
    meanVFile = os.path.join(basePath, inputDate, configParser.get("currents", "meanVFile"))
    stdUFile = os.path.join(basePath, inputDate, configParser.get("currents", "stdUFile"))
    stdVFile = os.path.join(basePath, inputDate, configParser.get("currents", "stdVFile"))
    outputFolder = configParser.get("currents", "outputFolder")
    outputFileTemplate = configParser.get("currents", "outputName")
    print("[%s] -- Mean U file set to: %s" % (appname, meanUFile))
    print("[%s] -- Mean V file set to: %s" % (appname, meanVFile))
    print("[%s] -- Std U file set to: %s" % (appname, stdUFile))
    print("[%s] -- Std V file set to: %s" % (appname, stdVFile))
    
    # create output folder if needed
    if not os.path.exists(os.path.join(baseOutputPath, outputFolder)):
        os.makedirs(os.path.join(baseOutputPath, outputFolder))
    
    # chart details
    meanColorMap = configParser.get("currents", "meanColorMap")
    meanMinValue = configParser.getfloat("currents", "meanMinValue")
    meanMaxValue = configParser.getfloat("currents", "meanMaxValue")
    meanLevels = configParser.getint("currents", "meanLevels")
    stdColorMap = configParser.get("currents", "stdColorMap")
    stdMinValue = configParser.getfloat("currents", "stdMinValue")
    stdMaxValue = configParser.getfloat("currents", "stdMaxValue")
    stdLevels = configParser.getint("currents", "stdLevels")    
    resolution = configParser.get("currents", "resolution")
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
    
    # open datasets STD    
    ds1u = xarray.open_dataset(stdUFile)
    ds1v = xarray.open_dataset(stdVFile)

    # open datasets MEAN
    ds2u = xarray.open_dataset(meanUFile)
    ds2v = xarray.open_dataset(meanVFile)
    
    # grid indices
    x = ds1u.lon.values
    y = ds1u.lat.values

    # lats and lons
    lats = ds1u.lat.transpose().values
    lons = ds1u.lon.values
    
    # central points
    clat = (lats[-1] - lats[0]) / 2
    clon = (lons[-1] - lons[0]) / 2
    
    # create the grid
    xxx, yyy = meshgrid(lons, lats)

    # iterate over the timestamps
    timestep_index = 0
    for t in ds1u.time.values:

        d1 = str(t).split("T")[0]        
        hour = str(t).split("T")[1].split(":")[0]
        minu = str(t).split("T")[1].split(":")[1]
        d2 = "%s:%s" % (hour, minu)
        d3 = "%s, %s" % (d1, d2)
        d4 = "%s_%s%s" % (d1, hour, minu)
        
        # iterate over depth
        depth_index = 0
        for d in ds1u.depth.values:
        
            # initialise the map
            bmap = Basemap(resolution=resolution,
                           llcrnrlon=lons[0],llcrnrlat=lats[0],
                           urcrnrlon=lons[-1],urcrnrlat=lats[-1])
            
            ############################################
            #
            # Mean
            #
            ############################################
            
            # contour MEAN
            meanLevelsContour = linspace(meanMinValue, meanMaxValue, num=meanLevels)            

            # u and v, then norm
            mean_data_0u =  ds2u.vozocrtx[timestep_index,depth_index,:,:].values
            mean_data_0v =  ds2v.vomecrty[timestep_index,depth_index,:,:].values
            mean_data = numpy.sqrt(mean_data_0u ** 2 + mean_data_0v ** 2)
            
            # contour
            mean_colormesh = bmap.contour(xxx, yyy, mean_data, cmap=meanColorMap, levels=meanLevelsContour, linewidths=0.3, vmin=meanMinValue, vmax=meanMaxValue)
    
            # colorbar MEAN
            meanTicks = range(int(meanMinValue), int(meanMaxValue)+1)
            mean_cb = bmap.colorbar(mean_colormesh, ticks=meanTicks, location="right")
            mean_cb.set_label("Mean currents (m/s)", fontsize=5)
            for t in mean_cb.ax.get_yticklabels():
                t.set_fontsize(5)

            ############################################
            #
            # Std
            #
            ############################################
    
            # contourf STD
            stdLevelsContourf = linspace(stdMinValue, stdMaxValue, num=stdLevels)
            std_data_0u =  ds1u.vozocrtx[timestep_index,depth_index,:,:].values
            std_data_0v =  ds1v.vomecrty[timestep_index,depth_index,:,:].values
            std_data = numpy.sqrt(std_data_0u ** 2 +  std_data_0v ** 2)
            
            # contourf
            std_colormesh = bmap.contourf(xxx, yyy, std_data, cmap=stdColorMap, levels=stdLevelsContourf, vmin=stdMinValue, vmax=stdMaxValue)
    
            # colorbar STD
            stdTicks = numpy.arange(stdMinValue, stdMaxValue+0.1, 0.1)
            std_cb = bmap.colorbar(std_colormesh, location='bottom', ticks = stdTicks)
            std_cb.set_label("Spread", fontsize=5)
            for t in std_cb.ax.get_xticklabels():
                t.set_fontsize(5)

            ############################################
            #
            # Mean vector
            #
            ############################################
            
            u = ds2u.vozocrtx[timestep_index,depth_index,::10,::10].values
            v = ds2v.vomecrty[timestep_index,depth_index,::10,::10].values

            # Normalize the arrows:
            uu = u / np.sqrt(u**2 + v**2)
            vv = v / np.sqrt(u**2 + v**2)
            
            xx = xxx[::10,::10]
            yy = yyy[::10,::10]
            
            # quiver
            mean_colormesh = bmap.quiver(xx, yy, u, v, headlength=5, headwidth=2, scale=50)    
                                
            ############################################
            #
            # general configuration
            #
            ############################################            
                
            # title
            finalDate = "%s:30" % (d3.split(":")[0])
            plt.title("Ensemble mean and spread for currents.\nTimestep: %s" % (finalDate), fontsize = 5)
                            
            # draw coastlines, country boundaries, fill continents.
            bmap.drawcoastlines(linewidth=0.25)
            bmap.fillcontinents(color='white')
                
            # save file
            filename = os.path.join(baseOutputPath, outputFolder, outputFileTemplate.format(DATE=d4, DEPTH=depth_index))
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            print("File %s generated" % filename)
            plt.clf()

            # increment depth index
            depth_index += 1

        # increment timestep index
        timestep_index += 1
