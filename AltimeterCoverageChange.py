"""Make plots of Altimeters."""
import sys, shutil, matplotlib
matplotlib.use('Agg')
sys.path.append('/home/spike/repos')
import netCDF4 as nc
from matplotlib import pyplot as plt
from testbedutils import geoprocess as gp
import datetime as DT
import numpy as np
from getdatatestbed import getDataFRF
from testbedutils import sblib as sb
import socket
####################3333
"""This code generates a altimeter plot to summarize the 'recent' changes in bathymetery"""

def plotAltimeterSummary(minTime, maxTime, **kwargs):
    """Function that makes plots for altimeters and beach change.

    Args:
        minTime: start time in epoch
        maxTime: end time in epoch

    Keyword Arguments:
        frontEnd: utilizes the switch between chl and FRF servers, default will use FRF server

    """
    plt.style.use(['seaborn-poster'])
    chlFront = "https://chldata.erdc.dren.mil/thredds/dodsC/frf/"
    frfFront = "http://bones/thredds/dodsC/FRF/"
    frontEnd = kwargs.get('frontEnd', frfFront)
    url1 = "geomorphology/altimeter/Alt940-340-altimeter/Alt940-340-altimeter.ncml"
    url2 = "geomorphology/altimeter/Alt940-250-altimeter/Alt940-250-altimeter.ncml"
    url3 = "geomorphology/altimeter/Alt940-200-altimeter/Alt940-200-altimeter.ncml"
    # 860 line
    url4 = "geomorphology/altimeter/Alt861-350-altimeter/Alt861-350-altimeter.ncml"
    url5 = "geomorphology/altimeter/Alt861-300-altimeter/Alt861-300-altimeter.ncml"
    url6 = "geomorphology/altimeter/Alt861-250-altimeter/Alt861-250-altimeter.ncml"
    url7 = "geomorphology/altimeter/Alt861-200-altimeter/Alt861-200-altimeter.ncml"
    url8 = "geomorphology/altimeter/Alt861-150-altimeter/Alt861-150-altimeter.ncml"
    # 769 line
    url9 = "geomorphology/altimeter/Alt769-350-altimeter/Alt769-350-altimeter.ncml"
    url10 = "geomorphology/altimeter/Alt769-300-altimeter/Alt769-300-altimeter.ncml"
    url11 = "geomorphology/altimeter/Alt769-250-altimeter/Alt769-250-altimeter.ncml"
    url12 = "geomorphology/altimeter/Alt769-200-altimeter/Alt769-200-altimeter.ncml"
    url13 = "geomorphology/altimeter/Alt769-150-altimeter/Alt769-150-altimeter.ncml"
    # original Line
    url14 = "geomorphology/altimeter/Alt03-altimeter/Alt03-altimeter.ncml"
    url15 = "geomorphology/altimeter/Alt04-altimeter/Alt04-altimeter.ncml"
    url16 = "geomorphology/altimeter/Alt05-altimeter/Alt05-altimeter.ncml"
    # get wave record and smush to one record
    go = getDataFRF.getObs(DT.datetime.fromtimestamp(minTime), DT.datetime.fromtimestamp(maxTime))
    w26 = go.getWaveSpec('waverider-26m')
    w17 = go.getWaveSpec('waverider-17m')
    if w17 is not None:
        w17New = sb.reduceDict(w17, np.argwhere(~np.in1d(w17['time'],w26['time'])).squeeze())
    gm = getDataFRF.getDataTestBed(DT.datetime.fromtimestamp(minTime-365*24*60*60), DT.datetime.fromtimestamp(maxTime))
    bathy = gm.getBathyIntegratedTransect(forceReturnAll=True, xbounds = [0,500], ybounds = [600,1000])

    diffTime, rmses = [], []
    for tt in range(bathy['time'].shape[0]-1):
        rmses.append(np.sqrt((np.square(bathy['elevation'][tt+1] - bathy['elevation'][tt])).mean()))
        timeDiffTemp = bathy['time'][tt+1] - bathy['time'][tt]
        diffTime.append(timeDiffTemp/2 + bathy['time'][tt])
    ## plot z by time (add artificial offset in elevation for each cross-shore gauge)
    multiplier = 10
    maxTimeDT = nc.num2date(maxTime, 'seconds since 1970-01-01')
    minTimeDT = nc.num2date(minTime, 'seconds since 1970-01-01')
    marker = 2  # marker size for wave plot
    lw = 1
    #######################################################################################
    fig = plt.figure(figsize=(12,12))
    plt.suptitle('RMSE calculated between\nyBounds = [600, 1000] xBounds = [0, 500]\nto avoid pier hole')
    ax0 = plt.subplot2grid((8,8),(0,0), colspan=8, rowspan=1)
    ax0.plot(w26['time'], w26['Hs'], 'm.', label='26m', ms=marker)
    if w17New is not None:
        ax0.plot(w17New['time'], w17New['Hs'], 'r.', label='17m', ms=marker)
    ax0.set_ylabel('wave\nheight [m]', fontsize=12)
    plt.legend()
    plt.gca().axes.get_xaxis().set_visible(False)
    ##############################
    ax00 = plt.subplot2grid((8,8),(1,0), colspan=8, rowspan=1, sharex=ax0)
    ax00.plot(diffTime, rmses, color='black', marker = "_", linestyle='solid', ms=150, linewidth=lw)
    ax00.set_ylabel('RMSE between\nsurveys [m]', fontsize=12)
    for tt, time in enumerate(bathy['time']):
        ax00.plot([time, time], [0,max(rmses)], 'C1', linestyle='dashdot', linewidth=lw)
    plt.gca().axes.get_xaxis().set_visible(False)
    ##############################
    ax1 = plt.subplot2grid((8,8),(2,0), colspan=8, rowspan=6, sharex=ax0)
    for uu, url in enumerate([url1, url2, url3, url14, url15, url16]):
        print(frontEnd + url)
        ncfile = nc.Dataset(frontEnd + url)
        try:
            time0 = nc.num2date(ncfile['time'][:], ncfile['time'].units)
            bottom0 = ncfile['bottomElevation'][:]
        except:
            bottom0 = ncfile['bottomElevation'][:-1]
            time0 = nc.num2date(ncfile['time'][:-1], ncfile['time'].units)
        coord = gp.FRFcoord(ncfile['Longitude'][:], ncfile['Latitude'][:])
        ax1.plot(time0, np.tile(coord['xFRF'], len(bottom0)) + bottom0*multiplier,  'b.', ms=marker)
        if url is url16:
            ax1.plot(time0,np.tile(coord['xFRF'],len(bottom0)) + bottom0*multiplier,  'b.', label='940m', ms=marker)
        ax1.plot([minTimeDT, maxTimeDT], [coord['xFRF'],coord['xFRF']], 'b', linestyle='dotted', linewidth=lw)
    ##############################
    for url in [url4, url5, url6, url7, url8]: #,
        print(url)
        ncfile = nc.Dataset(frontEnd + url)
        try:
            time0 = nc.num2date(ncfile['time'][:], ncfile['time'].units)
            bottom0 = ncfile['bottomElevation'][:]
        except:
            bottom0 = ncfile['bottomElevation'][:-1]
            time0 = nc.num2date(ncfile['time'][:-1], ncfile['time'].units)
        coord = gp.FRFcoord(ncfile['Longitude'][:], ncfile['Latitude'][:])
        ax1.plot(time0, np.tile(coord['xFRF'],len(bottom0)) + bottom0*multiplier, 'r.', ms=marker)
        if url is url8:
            ax1.plot(time0, np.tile(coord['xFRF'],len(bottom0)) + bottom0*multiplier, 'r.', label='861m', ms=marker)
        ax1.plot([minTimeDT, maxTimeDT], [coord['xFRF'],coord['xFRF']],'r', linestyle='dotted', linewidth=lw)
    ##############################
    for url in [url9, url10, url11, url12, url13]:
        print(url)
        ncfile = nc.Dataset(frontEnd + url)
        try:
            time0 = nc.num2date(ncfile['time'][:], ncfile['time'].units)
            bottom0 = ncfile['bottomElevation'][:]
        except:
            bottom0 = ncfile['bottomElevation'][:-1]
            time0 = nc.num2date(ncfile['time'][:-1], ncfile['time'].units)
        coord = gp.FRFcoord(ncfile['Longitude'][:], ncfile['Latitude'][:])
        ax1.plot(time0, np.tile(coord['xFRF'],len(bottom0)) + bottom0*multiplier, 'c.', ms=marker)
        if url is url13:
            ax1.plot(time0, np.tile(coord['xFRF'],len(bottom0)) + bottom0*multiplier, 'c.', label='769m', ms=marker)
        ax1.plot([minTimeDT, maxTimeDT], [coord['xFRF'], coord['xFRF']], 'c', linestyle='dotted', linewidth=lw)

    ##############################
    ax1.set_xlim([minTimeDT, maxTimeDT])
    ax1.legend()

    plt.setp(plt.xticks()[1], rotation=30, ha='right')
    ax1.set_xlabel('time')
    ax1.set_ylabel('frf cross-shore location (with change in elevation plotted)', fontsize=12)

    fname = '/todaysPlots/TodaysAltimeterSummary_{}.png'.format(kwargs.get('duration', ''))
    plt.savefig(fname)
    print('Saved File Here: {}'.format(fname))
    plt.close()
    shutil.copy(fname, '/mnt/gaia/rootdir/CMTB/')

if __name__ == '__main__':
    maxTime = DT.datetime.now().timestamp()
    for Duration in [3]:  #duration in months
        minTime = maxTime - DT.timedelta(days=Duration*30).total_seconds()
        ipAddress = socket.gethostbyname(socket.gethostname())
    if ipAddress.startswith('134.164.129'):  # FRF subdomain
        frontEnd = "http://bones/thredds/dodsC/FRF/"
    else:
        frontEnd = "https://chldata.erdc.dren.mil/thredds/dodsC/frf/"
    plotAltimeterSummary(minTime, maxTime, duration=Duration, frontEnd=frontEnd)