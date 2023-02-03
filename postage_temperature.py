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

appname = "PlotPostageTemp"


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
    baseEnsPathTemplate = configParser.get("default", "baseEnsPath")
    baseOutputPath = configParser.get("default", "baseOutputPath")    
    inputFileTemplate = configParser.get("postcardTemp", "inputFile")
    inputFiles = []
    outputFolder = configParser.get("postcardTemp", "outputFolder")
    outputFileTemplate = configParser.get("postcardTemp", "outputName")
    print("[%s] -- Input files set to:" % (appname))
    for i in range(10):
        inputFile = os.path.join(baseEnsPathTemplate.format(INSTANCE=i, DATE=inputDate), inputFileTemplate.format(DATE=inputDate))
        inputFiles.append(inputFile)
        print(inputFile)

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
    resolution = configParser.get("postcardTemp", "resolution")
    colorMap = configParser.get("postcardTemp", "colorMap")
    minValue_surf = configParser.getfloat("postcardTemp", "minValue_surf")
    maxValue_surf = configParser.getfloat("postcardTemp", "maxValue_surf")
    minValue_bott = configParser.getfloat("postcardTemp", "minValue_bott")
    maxValue_bott = configParser.getfloat("postcardTemp", "maxValue_bott")    
    levels = configParser.getint("postcardTemp", "levels")
    print("[%s] -- Resolution set to: %s" % (appname, resolution))
    print("[%s] -- Min Value (surf) set to: %s" % (appname, minValue_surf))
    print("[%s] -- Max Value (surf) set to: %s" % (appname, maxValue_surf))
    print("[%s] -- Min Value (bott) set to: %s" % (appname, minValue_bott))
    print("[%s] -- Max Value (bott) set to: %s" % (appname, maxValue_bott))    
    print("[%s] -- Color map set to: %s" % (appname, colorMap))
    print("[%s] -- Levels set to: %s" % (appname, levels))
                    
        
    ###############################################
    #
    # start processing
    #
    ###############################################

    # open files
    datasets = []
    for i in inputFiles:
        datasets.append(xarray.open_dataset(i))

    # grid indices
    x = datasets[0].nav_lon.transpose().values[0]
    y = datasets[0].nav_lat.values[0]

    # lats and lons
    lats = datasets[0].nav_lat.transpose().values[0]
    lons = datasets[0].nav_lon.values[0]

    # create the grid
    xxx, yyy = meshgrid(lons, lats)
    
    # define a timestep index (to keep track of the timesteps) and an index to keep track of the day we are in
    timestep_index = 0
    day_current_index = 0
    old_day = str(datasets[0].time_counter[0].values).split("T")[0]

    # iterate over timesteps    
    for t in datasets[0].time_counter:

        # get the date of the current timestep, and optionally update the variable and index keeping track of the day
        d1 = str(t.values).split("T")[0]
        if d1 != old_day:
            old_day = d1
            day_current_index += 1

        # get days string
        hour = str(t).split("T")[1].split(":")[0]
        minu = 30
        d2 = "%s:%s" % (hour, minu)
        d3 = "%s, 12:30" % (d1)
        d4 = "%s_1230" % (d1)

        # debug print
        print("[%s] -- Timestep: %s" % (appname, d3))

        # iterate over depth
        depth_index = 0
        for d in datasets[0].deptht:
            
            if depth_index < 2:
                minValue = minValue_surf
                maxValue = maxValue_surf
            else:
                minValue = minValue_bott
                maxValue = maxValue_bott
                
            fig, axes = plt.subplots(nrows=5, ncols=2)
            
            ax_index = 0
            for ax in axes.flat:
                # create basemap
                bmap = Basemap(resolution=resolution,
                               llcrnrlon=lons[0],llcrnrlat=lats[0],
                               urcrnrlon=lons[-1],urcrnrlat=lats[-1], ax=ax)                

                # contourf
                mean_data_0 = datasets[ax_index].votemper[timestep_index,depth_index,:,:]
                mean_data = mean_data_0.where(((mean_data_0.nav_lat <= blackSeaMaskLat) | (mean_data_0.nav_lon <= blackSeaMaskLon)))                
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
             
            # colorbar
            ticks = range(int(minValue), int(maxValue)+1, 1)
            cb = fig.colorbar(im, ax=axes.ravel().tolist(), ticks=ticks, shrink=0.5)
            cb.set_label("Temperature (degC)", fontsize = 3)
            cb.ax.tick_params(labelsize=3)
            for t in cb.ax.get_xticklabels():
                t.set_fontsize(1)
            
            # title
            finalDate = "%s:30" % (d3.split(":")[0])
            plt.suptitle("Temperature at %s m.\nTimestep: %s" % (int(d), finalDate), fontsize = 5)
                
            # save file
            di = datasets[0].deptht.values.tolist().index(d)
            filename = os.path.join(dst, outputFileTemplate.format(DATE=d4, DEPTH=di))                    
            plt.savefig(filename, dpi=300, bbox_inches="tight")
            print("File %s generated" % filename)

            fig.clear()
            plt.close(fig)
        
            # increment depth
            depth_index += 1

        # increment timestep
        timestep_index += 1
