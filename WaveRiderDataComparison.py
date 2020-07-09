"""script runs plot."""
import matplotlib
matplotlib.use('Agg')
import netCDF4 as nc
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.ticker import PercentFormatter
import shutil

def plotTodaysWaveriders():
    """Make plots of todays wave statistics.

    gathers most recent waverider data and plots the data in a histogram plot and timeseries for most recent
    100 records.

    Returns:
        None

    """
    ############################
    url1 = 'http://bones/thredds/dodsC/FRF/oceanography/waves/waverider-nags-head-nc/waverider-nags-head-nc.ncml'
    url2 = 'http://bones/thredds/dodsC/FRF/oceanography/waves/waverider-oregon-inlet-nc/waverider-oregon-inlet-nc.ncml'
    url3 = 'http://bones/thredds/dodsC/FRF/oceanography/waves/waverider-26m/waverider-26m.ncml'

    ncfile1 = nc.Dataset(url1)
    ncfile2 = nc.Dataset(url2)
    ncfile3 = nc.Dataset(url3)
    recordNumber = 100
    markerSize = 4
    lenRecordInYears = (nc.num2date(ncfile3['time'][:], ncfile3['time'].units)[-1]-nc.num2date(ncfile3['time'][:], ncfile3['time'].units)[0]).days/365.
    all430Hs = ncfile3['waveHs'][1:]
    ##############################
    fig = plt.figure(figsize=(6,8))
    ax1 = plt.subplot(211)
    ax1.plot(nc.num2date(ncfile1['time'][-recordNumber:], ncfile1['time'].units), ncfile1['waveHs'][-recordNumber:],
             'o--', ms=markerSize, label='Nags Head')
    ax1.plot(nc.num2date(ncfile2['time'][-recordNumber:], ncfile2['time'].units), ncfile2['waveHs'][-recordNumber:],
             's:', ms=markerSize, label='Oregon Inlet')
    ax1.plot(nc.num2date(ncfile3['time'][-recordNumber:], ncfile3['time'].units), ncfile3['waveHs'][-recordNumber:],
             'd-', ms=markerSize, label='26m Waverider')
    ax1.legend()
    ax1.set_ylabel('wave Height [m]')
    ax1.set_xlabel('time')
    fig.autofmt_xdate()

    ax2 = plt.subplot(212)
    n, bins, patches = ax2.hist(all430Hs, bins=50, weights=np.ones(len(all430Hs))*lenRecordInYears / len(all430Hs))
    ax2.semilogy()
    plt.gca().yaxis.set_major_formatter(PercentFormatter(1, 2))
    for percentage in [1, 0.1, 0.01]:
        plt.plot([bins[np.argwhere(n > percentage/100.).squeeze().max()], bins[np.argwhere(n > percentage/100.).squeeze().max()]],
                 [0.00001, 1], linestyle='dotted', label='{}% chance happening in a year'.format(percentage))
    plt.legend(loc='lower left')
    ax2.set_ylabel('Percentage wave height happens in any given year')
    ax2.set_xlabel('Wave Height [m]')
    plt.tight_layout()
    fname = '/todaysPlots/TodaysWaveriderSummary.png'
    plt.savefig(fname)
    plt.close()
    shutil.copy(fname, '/mnt/gaia/rootdir/CMTB/')

if __name__ == '__main__':
    """run main script"""
    plotTodaysWaveriders()