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
import numpy as np
import traceback
import datetime
import xarray
import numpy
import math
import pdb
import sys



###############################################
#
# initial config
#
###############################################

appname = "MeanSpread"


###############################################
#
# chart config
#
###############################################

###############################################
#
# main
#
###############################################

if __name__ == "__main__":

    # open dataset STD
    inputFile1 = "input/REG_medens_sdt_T.nc"
    ds1 = xarray.open_dataset(inputFile1)

    # open dataset MEAN
    inputFile2 = "input/REG_medens_mean_T.nc"
    ds2 = xarray.open_dataset(inputFile2)
    
    # grid indices
    x = ds1.x.values
    y = ds1.y.values

    # lats and lons
    lats = ds1.nav_lat.transpose().values[0]
    lons = ds1.nav_lon.values[0]

    # central points
    clat = (lats[-1] - lats[0]) / 2
    clon = (lons[-1] - lons[0]) / 2
    
    # create the grid
    xxx, yyy = meshgrid(lons, lats)

    # iterate over the timestamps
    for t in ds1.time_counter.values:

        d1 = str(t).split("T")[0]        
        hour = str(t).split("T")[1].split(":")[0]
        minu = str(t).split("T")[1].split(":")[1]
        d2 = "%s:%s" % (hour, minu)
        d3 = "%s, %s" % (d1, d2)
        d4 = "%s_%s%s" % (d1, hour, minu)
        
            
        # initialise the map
        bmap = Basemap(resolution='f',
                       llcrnrlon=lons[0],llcrnrlat=lats[0],
                       urcrnrlon=lons[-1],urcrnrlat=lats[-1])
        
        # contourf STD
        std_data =  numpy.round(ds1.sossheig[0,:,:].values, 2)
        std_colormesh = bmap.contourf(xxx, yyy, std_data, cmap='Purples', levels=10, vmin=std_data.min(), vmax=std_data.max())

        # contour MEAN
        # contour
        mean_data =  ds2.sossheig[0,:,:].values
        mean_colormesh = bmap.contour(xxx, yyy, mean_data, cmap='bwr', levels=20, linewidths=0.3)
        
        # title
        plt.title("Ensemble mean and spread for Sea Surface Height.\nTimestep: %s" % d3, fontsize = 8)
        
        # colorbar STD
        std_cb = bmap.colorbar(std_colormesh, location='bottom')
        std_cb.set_label("Spread", fontsize=6)
        for t in std_cb.ax.get_xticklabels():
            t.set_fontsize(6)

        # colorbar MEAN
        mean_cb = bmap.colorbar(mean_colormesh, location='right')
        mean_cb.set_label("Mean Sea Surface Height (m)", fontsize=6)
        for t in mean_cb.ax.get_yticklabels():
            t.set_fontsize(6)

            
        # draw coastlines, country boundaries, fill continents.
        bmap.drawcoastlines(linewidth=0.25)
        bmap.fillcontinents(color='white')
        
        # # show
        # plt.show()

        # save file
        filename = "output/ens_mean_spread_SeaSurfaceHeight_%s.png" % (d4)
        plt.savefig(filename, dpi=300, bbox_inches="tight")
        print("File %s generated" % filename)

