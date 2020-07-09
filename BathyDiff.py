"""Code to take difference of bathymetry on a automated basis."""
import matplotlib
matplotlib.use('Agg')
import netCDF4 as nc
from matplotlib import  pyplot as plt
import sys, os, shutil
import numpy as np
import datetime as DT
sys.path.append('/home/spike/repos')
sys.path.append('/home/spike/cmtb')

def runSurveyDiff(**kwargs):
    """Function that will Run each survey difference.

    Will just look at the last 2 dem's from survey/DEM

    Keyword Args:
        'bounds' (list): a list of [x0, x1, y0, y1] in FRF coordinates for the plot
        'filebase' (str): the file path for where to save image once created NOT IMPLMENTED
        'start' (str): start date (YYYY-MM-DD) format NOT IMPLMENTED
        'end' (str): end date (YYYY-MM-DD) format NOT IMPLMENTED

    """
    import plotting.plottingTools as pt
    if 'start' in kwargs:
        start = kwargs['start']
    if 'end' in kwargs:
        end = kwargs['end']
    filebase = kwargs.get('filebase','/todaysPlots' )
    bounds = kwargs.get('bounds', [100, 800, 0, 1400])
    # set min and max values in FRF coordinates
    xmin = kwargs.get('xmin', bounds[0])
    xmax = kwargs.get('xmax', bounds[1])
    ymin = kwargs.get('ymin', bounds[2])
    ymax = kwargs.get('ymax', bounds[3])
    #######################
    cmap = 'coolwarm'
    ncfile=nc.Dataset('http://134.164.129.55/thredds/dodsC/FRF/geomorphology/DEMs/surveyDEM/surveyDEM.ncml')
    dems = ncfile['elevation'][-2:]                                         # grab 2 most recent processed surveys
    times = nc.num2date(ncfile['time'][-2:], ncfile['time'].units)          # grab 2 most recent times
    xminIdx = np.argmin(np.abs(xmin - ncfile['xFRF'][:]))
    xmaxIdx = np.argmin(np.abs(xmax - ncfile['xFRF'][:]))
    yminIdx = np.argmin(np.abs(ymin - ncfile['yFRF'][:]))
    ymaxIdx = np.argmin(np.abs(ymax - ncfile['yFRF'][:]))
    xVals = ncfile['xFRF'][slice(xminIdx, xmaxIdx)]                                 # grab x values
    yVals = ncfile['yFRF'][slice(yminIdx, ymaxIdx)]                                 # grab y values
    #############  Now grab survey data ##########################################
    from getdatatestbed import getDataFRF
    go = getDataFRF.getObs(times[1], times[1]+DT.timedelta(days=1))
    survey = go.getBathyTransectFromNC()

    ################### Make Plot ###################################
    plt.figure(figsize=(5,10))
    plt.pcolormesh(xVals, yVals, dems[1, slice(yminIdx,ymaxIdx), slice(xminIdx,xmaxIdx)] -
                   dems[0, slice(yminIdx,ymaxIdx), slice(xminIdx,xmaxIdx)],
                    cmap=cmap) #norm =pt.MidpointNormalize(midpoint=0))
    cbar = plt.colorbar()
    plt.plot(survey['xFRF'], survey['yFRF'], 'k.', ms= 0.25, alpha=0.25)
    cbar.set_label('Blue is erosion, Red is accretion')
    plt.xlim([100, 800])
    plt.plot([100,530], [515, 515], 'k-', lw=5)
    plt.title('Surface Difference:\n{} - {}'.format(times[1].date(), times[0].date()))
    cont = plt.contour(xVals, yVals, -dems[1, slice(yminIdx, ymaxIdx), slice(xminIdx, xmaxIdx)], levels=[0,2,3,4,5,6,8], colors='k')
    plt.clabel(cont, fmt='%d')
    cont = plt.contour(xVals, yVals, -dems[0, slice(yminIdx, ymaxIdx), slice(xminIdx, xmaxIdx)],colors='k',
                       levels=[0, 2, 3, 4, 5, 6, 8], linestyles='dotted', linewidths=0.5)
    plt.xlabel('FRF Cross-shore Coordinate')
    plt.ylabel('FRF alongshore Coordinate')
    plt.text(0, -100, 'Note: solid contour lines are most recent survey', fontsize=12)
    plt.tight_layout(rect=[0.02, 0.05, .98, .95])
    fname = os.path.join(filebase, 'BathyDifference.png')
    plt.savefig(fname); plt.close()
    shutil.copy(fname, '/mnt/gaia/rootdir/CMTB/')

if __name__ == "__main__":
    runSurveyDiff()