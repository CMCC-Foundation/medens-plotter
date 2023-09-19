#!/usr/bin/python3

###############################################
#
# global reqs
#
###############################################

from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from numpy import meshgrid
from numpy import linspace
from matplotlib import cm
import configparser
import numpy as np
import matplotlib
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
    meanFile = os.path.join(basePath, inputDate, configParser.get("temperature", "meanFile"))
    stdFile = os.path.join(basePath, inputDate, configParser.get("temperature", "stdFile"))
    outputFolder = configParser.get("temperature", "outputFolder")
    outputFileTemplate = configParser.get("temperature", "outputName")
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
    
    # read min and max values for mean temperature
    meanMinValues_surf = []
    meanMaxValues_surf = []
    stdMinValues_surf = []
    stdMaxValues_surf = []
    meanMinValues_bott = []
    meanMaxValues_bott = []
    stdMinValues_bott = []
    stdMaxValues_bott = []        
    for i in range(0, 12):
        
        # read surface values    
        meanMinValues_surf.append(configParser.getfloat("temperature", "meanMinValue_surf_%s" % str(i+1)))
        meanMaxValues_surf.append(configParser.getfloat("temperature", "meanMaxValue_surf_%s" % str(i+1)))
        stdMinValues_surf.append(configParser.getfloat("temperature", "stdMinValue_surf_%s" % str(i+1)))
        stdMaxValues_surf.append(configParser.getfloat("temperature", "stdMaxValue_surf_%s" % str(i+1)))

        # read bottom values
        meanMinValues_bott.append(configParser.getfloat("temperature", "meanMinValue_bott_%s" % str(i+1)))
        meanMaxValues_bott.append(configParser.getfloat("temperature", "meanMaxValue_bott_%s" % str(i+1)))
        stdMinValues_bott.append(configParser.getfloat("temperature", "stdMinValue_bott_%s" % str(i+1)))
        stdMaxValues_bott.append(configParser.getfloat("temperature", "stdMaxValue_bott_%s" % str(i+1)))

    # chart details
    meanColorMap = configParser.get("temperature", "meanColorMap")
    meanLevels = configParser.getint("temperature", "meanLevels")
    stdColorMap = configParser.get("temperature", "stdColorMap")
    stdLevels = configParser.getint("temperature", "stdLevels")    
    resolution = configParser.get("temperature", "resolution")
    print("[%s] -- Mean color map set to: %s" % (appname, meanColorMap))
    print("[%s] -- Mean min values (surf) set to: %s" % (appname, meanMinValues_surf))
    print("[%s] -- Mean max values (surf) set to: %s" % (appname, meanMaxValues_surf))
    print("[%s] -- Mean min values (bott) set to: %s" % (appname, meanMinValues_bott))
    print("[%s] -- Mean max values (bott) set to: %s" % (appname, meanMaxValues_bott))
    print("[%s] -- Std color map set to: %s" % (appname, stdColorMap))
    print("[%s] -- Std min values (surf) set to: %s" % (appname, stdMinValues_surf))
    print("[%s] -- Std max values (surf) set to: %s" % (appname, stdMaxValues_surf))
    print("[%s] -- Std min values (bott) set to: %s" % (appname, stdMinValues_bott))
    print("[%s] -- Std max values (bott) set to: %s" % (appname, stdMaxValues_bott))    
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

        print(d1)
        
        month = str(int(d1.split("-")[1]))
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

            fig, axes = plt.subplots(nrows=2, ncols=1)
            
            ax_index = 0
            for ax in axes.flat:
                    
                if depth_index < 2:
                    meanMinValue = meanMinValues_surf[int(month)+1]
                    meanMaxValue = meanMaxValues_surf[int(month)+1]
                    stdMinValue = stdMinValues_surf[int(month)+1]
                    stdMaxValue = stdMaxValues_surf[int(month)+1]       
                else:
                    meanMinValue = meanMinValues_bott[int(month)+1]
                    meanMaxValue = meanMaxValues_bott[int(month)+1]
                    stdMinValue = stdMinValues_bott[int(month)+1]
                    stdMaxValue = stdMaxValues_bott[int(month)+1]       
                
                if ax_index == 0:

                    # meanMinValue = numpy.min(ds2.votemper[timestep_index,depth_index,:,:])
                    # meanMaxValue = numpy.max(ds2.votemper[timestep_index,depth_index,:,:])
                    
                    ############################################
                    #
                    # Mean
                    #
                    ############################################                                            
                
                    # initialise the map
                    bmap = Basemap(resolution=resolution,
                                   llcrnrlon=lons[0],llcrnrlat=lats[0],
                                   urcrnrlon=lons[-1],urcrnrlat=lats[-1], ax=ax)
        
                    # customize colormap
                    min_val, max_val = 0, 0.7
                    n = 10            
                    orig_cmap = cm.gist_rainbow
                    colors = orig_cmap(np.linspace(min_val, max_val, n))
                    cmap = cm.colors.LinearSegmentedColormap.from_list("mycmap", colors)
                    cmap = meanColorMap

                    # set adaptive min and max
                    meanMinValue = numpy.nanmin(ds2.votemper[timestep_index,depth_index,:,:])
                    meanMaxValue = numpy.nanmax(ds2.votemper[timestep_index,depth_index,:,:])
                    
                    # get the mean -- part 1                
                    mean_data_0 =  ds2.votemper[timestep_index,depth_index,:,:]
                    mean_data_1 = mean_data_0.where(mean_data_0 > 0, other=np.nan)
                  
                    # get the mean -- mask the black sea -- part 2
                    mean_data_2 = mean_data_1.where((mean_data_1['lat'] <= blackSeaMaskLat) | (mean_data_1['lon'] <= blackSeaMaskLon), np.nan)                    
                    mean_data = mean_data_2.values

                    # set adaptive min and max
                    meanMinValue = numpy.nanmin(mean_data_2.values)
                    meanMaxValue = numpy.nanmax(mean_data_2.values)
                    
                    # contour range
                    meanLevelsContour = linspace(meanMinValue, meanMaxValue, num=meanLevels)            
                    
                    mean_colormesh = bmap.contourf(xxx, yyy, mean_data, cmap=cmap, levels=meanLevelsContour, linewidths=0.15, vmin=meanMinValue, vmax=meanMaxValue, extend='both')
                    
                    # colorbar MEAN
                    meanTicks = range(int(meanMinValue), int(meanMaxValue)+1)
                    mean_cb = bmap.colorbar(mean_colormesh, ticks=meanTicks, location='right')
                    mean_cb.set_label("Mean Temperature (degC)", fontsize=5)
                    for t in mean_cb.ax.get_yticklabels():
                        t.set_fontsize(3)
                    
                    # draw coastlines, country boundaries, fill continents.
                    bmap.drawcoastlines(linewidth=0.15)
                    bmap.fillcontinents()
                    bmap.drawparallels(range(0, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)
                    bmap.drawmeridians(range(-90, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)

                    # title
                    # finalDate = "%s:30" % (d3.split(":")[0])
                    finalDate = d1
                    plt.title("Ensemble mean for Sea temperature at %s m\nDaily mean: %s" % (int(d), finalDate), fontsize = 5)
                    
                else:
                        
                    ############################################
                    #
                    # Std
                    #
                    ############################################                                            
    
                    # initialise the map
                    bmap = Basemap(resolution=resolution,
                                   llcrnrlon=lons[0],llcrnrlat=lats[0],
                                   urcrnrlon=lons[-1],urcrnrlat=lats[-1], ax=ax)
        
                    # define the colormap
                    max_percentage = 100
                    white_percentage = 20
                    white = np.array([256/256, 256/256, 256/256, 1])
                    reds = cm.get_cmap(stdColorMap, 256)
                    fv = reds(np.linspace(0, 1, max_percentage))
                    fv[:white_percentage, :] = white
                    fv[white_percentage:, :] = reds(np.linspace(0, 1, max_percentage-white_percentage))
                    newcmp = ListedColormap(fv)

                    # contourf STD
                    stdLevelsContourf = linspace(stdMinValue, stdMaxValue, num=stdLevels+1)
                    std_data_0 =  ds1.votemper[timestep_index,depth_index,:,:]
                    std_data_1 = std_data_0.where((std_data_0.lat <= blackSeaMaskLat) | (std_data_0.lon <= blackSeaMaskLon))
                    std_data = std_data_1.values
                    std_colormesh = bmap.contourf(xxx, yyy, std_data, cmap=newcmp, levels=stdLevelsContourf, vmin=stdMinValue, vmax=stdMaxValue, extend='both')
                        
                    # colorbar STD
                    stdTicks = numpy.arange(stdMinValue, stdMaxValue+0.1, 0.1)
                    std_cb = bmap.colorbar(std_colormesh, location='right', ticks = stdTicks, shrink = 0.5)
                    std_cb.set_label("Spread (degC)", fontsize=5)
                    for t in std_cb.ax.get_yticklabels():
                        t.set_fontsize(3)
                            
                    # title
                    # finalDate = "%s:30" % (d3.split(":")[0])
                    finalDate = d1
                    plt.title("Ensemble spread for Sea temperature at %s m\nDaily mean: %s" % (int(d), finalDate), fontsize = 5)
                    
                    # draw coastlines, country boundaries, fill continents.
                    bmap.drawcoastlines(linewidth=0.15)
                    bmap.fillcontinents()
                    bmap.drawparallels(range(0, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)
                    bmap.drawmeridians(range(-90, 90, 5), linewidth=0.1, labels=[1,0,0,1], fontsize=2)
    
                ax_index += 1
                    
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
