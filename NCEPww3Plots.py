import numpy as np
import netCDF4 as nc
import datetime as dt
from matplotlib import pyplot as plt
import pytz, sys, glob, os
sys.path.append('/home/spike/repos')
from testbedutils import sblib as sb


def makeWW3forecast(date = dt.date.today().strftime('%Y%m%d'), pathStart = '/home/spike/repos/LivePlots/ww3Files',
                    **kwargs):
    """ Makes ww3 forecast
    
    Args:
        date:
        pathStart:
    Keyword Args:
        lonBounds: tuple of min,max for longitude values (default=(278, 290))
        latBounds: tuple of min,max for latitude values  (default=(30,40))
        ofname: output for gif
    Returns:

    """
    lonBounds=kwargs.get('lonBounds', (278,290))
    latBounds=kwargs.get('latBounds', (30,40))
    now = dt.datetime.utcnow().hour - dt.datetime.utcnow().hour%6       # latest forecast hour
    last = dt.datetime.utcnow().hour - dt.datetime.utcnow().hour%6 - 6  # last forecast hour
    # load the data url
    try:
        url = 'https://nomads.ncep.noaa.gov:9090/dods/wave/mww3/{}/multi_1.at_10m{}_{}z'.format(date, date, now)
        ncfile = nc.Dataset(url)
        print('successfully grabbed {}'.format(url))
    except OSError:
        print('unable to grab {}'.format(url))
        url = 'https://nomads.ncep.noaa.gov:9090/dods/wave/mww3/{}/multi_1.at_10m{}_{}z'.format(date, date, last)
        ncfile = nc.Dataset(url)
        print('successfully grabbed {}'.format(url))
    
    ## unpack file
    times = nc.num2date(ncfile['time'][:], ncfile['time'].units)
    
    lon = ncfile['lon'][:]
    lat = ncfile['lat'][:]
    idxLon = (lon > lonBounds[0]) & (lon <  lonBounds[-1])
    idxLat = (lat > latBounds[0])  & (lat < latBounds[-1])
    
    HsTot = ncfile['htsgwsfc'][:, idxLat, idxLon]
    TpTot = ncfile['perpwsfc'][:, idxLat, idxLon]
    DpTot = ncfile['dirpwsfc'][:, idxLat, idxLon]
    
    Hs_ss = ncfile['wvhgtsfc'][:, idxLat, idxLon]
    Tm_ss = ncfile['wvpersfc'][:, idxLat, idxLon]
    Dp_ss = ncfile['wvdirsfc'][:, idxLat, idxLon]
    
    Hs_1 = ncfile['swell_1'][:, idxLat, idxLon]
    Tm_1 = ncfile['swper_1'][:, idxLat, idxLon]
    Dp_1 = ncfile['swdir_1'][:, idxLat, idxLon]
    
    Hs_2 = ncfile['swell_2'][:, idxLat, idxLon]
    Tm_2 = ncfile['swper_2'][:, idxLat, idxLon]
    Dp_2 = ncfile['swdir_2'][:, idxLat, idxLon]
    print(' Successfully downloaded data')
    ###################
    # # set masks for % calculation
    # Hs_ss.data[Hs_ss.data == 9.999e+20] = 0
    # Hs_1.data[Hs_1.data == 9.999e+20] = 0
    # Hs_2.data[Hs_2.data == 9.999e+20] = 0
    ########################
    
    lon = lon[idxLon]
    lat = lat[idxLat]
    xxLon, yyLat = np.meshgrid(lon, lat)
    
    for tt in range(len(times)):
        ## loop over this
        quiverX = np.ma.array(xxLon, mask=DpTot.mask[0])
        quiverY = np.ma.array(yyLat, mask=DpTot.mask[0])
        
        cmap = 'hot_r'
        TmCmax = np.max([TpTot.max(), Tm_ss.max(), Tm_1.max(), Tm_2.max()])
        TmCmin = np.min([TpTot.min(), Tm_ss.min(), Tm_1.min(), Tm_2.min()])
        hsCmax = np.max([HsTot[tt].max(), Hs_ss[tt].max(), Hs_1[tt].max(), Hs_2[tt].max()])
        hsCmin = np.min([HsTot[tt].min(), Hs_ss[tt].min(), Hs_1[tt].min(), Hs_2[tt].min()])
        #######################################################################################################################
        #######################################################################################################################
        plt.figure(figsize=(10, 14))
        VarHs = HsTot
        varDp = DpTot
        varTm = TpTot
        ax00 = plt.subplot2grid((4,6), (0,0), colspan=2, rowspan=1)
        hsField = ax00.pcolormesh(lon, lat, VarHs[tt], cmap=cmap, vmin=hsCmin, vmax=hsCmax)
        cbar00 = plt.colorbar(hsField, ax=ax00)
        cbar00.set_label('[m]')
        ax00.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax00.set_title('$H_s$ Total')
        
        ax04 = plt.subplot2grid((4,6), (0,2), colspan=2, rowspan=1)
        ax04.axis('off')
        ax04.text(0, 0, 'print interesting info here')
        # field = ax04.pcolormesh(lon, lat, varPercent, cmap=cmap)
        
        ax02 = plt.subplot2grid((4,6), (0,4), sharex=ax00, sharey=ax00, colspan=2, rowspan=1)
        hsField = ax02.pcolormesh(lon, lat, varTm[tt], cmap=cmap, vmin=TmCmin, vmax=TmCmax)
        cbar02 = plt.colorbar(hsField, ax=ax02)
        cbar02.set_label('[s]')
        ax02.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax02.set_title('$T_p$ Total')
        
        ########## Wind Sea
        VarHs = Hs_ss
        varDp = Dp_ss
        varTm = Tm_ss
        varPercent = Hs_ss**2/HsTot**2
        ax10 = plt.subplot2grid((4,6),(1,0), colspan=2, rowspan=1)
        hsField = ax10.pcolormesh(lon, lat, VarHs[tt], cmap=cmap, vmin=hsCmin, vmax=hsCmax)
        cbar10 = plt.colorbar(hsField, ax=ax10)
        cbar10.set_label('[m]')
        ax10.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax10.set_title('$H_s$ windSea')
        
        
        ax12 = plt.subplot2grid((4,6), (1,2), sharex=ax00, sharey=ax00, colspan=2, rowspan=1)
        field = ax12.pcolormesh(lon, lat, varPercent[tt], cmap=cmap, vmin=0, vmax=1)
        cbar12 = plt.colorbar(field, ax=ax12)
        cbar12.set_label('%')
        ax12.set_title('% of total')
        
        ax12 = plt.subplot2grid((4,6), (1,4), sharex=ax00, sharey=ax00, colspan=2, rowspan=1)
        hsField = ax12.pcolormesh(lon, lat, varTm[tt], cmap=cmap, vmin=TmCmin, vmax=TmCmax)
        cbar12 = plt.colorbar(hsField, ax=ax12)
        cbar12.set_label('[s]')
        ax12.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax12.set_title('$T_p$ windSea')
        ########## swell 1
        VarHs = Hs_1
        varDp = Dp_1
        varTm = Tm_1
        varPercent = Hs_1**2/HsTot**2
        
        ax00 = plt.subplot2grid((4,6),(2,0), colspan=2, rowspan=1)
        hsField = ax00.pcolormesh(lon, lat, VarHs[tt], cmap=cmap, vmin=hsCmin, vmax=hsCmax)
        cbar00 = plt.colorbar(hsField, ax=ax00)
        cbar00.set_label('[m]')
        ax00.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax00.set_title('$H_s$ swell 1')
        
        ax22 = plt.subplot2grid((4,6), (2,2), sharex=ax00, sharey=ax00, colspan=2, rowspan=1)
        field = ax22.pcolormesh(lon, lat, varPercent[tt], cmap=cmap, vmin=0, vmax=1)
        cbar22 = plt.colorbar(field, ax=ax22)
        cbar22.set_label('%')
        ax22.set_title('% of total')
        
        ax24 = plt.subplot2grid((4,6), (2,4), sharex=ax00, sharey=ax00, colspan=2, rowspan=1)
        hsField = ax24.pcolormesh(lon, lat, varTm[tt], cmap=cmap, vmin=TmCmin, vmax=TmCmax)
        cbar24 = plt.colorbar(hsField, ax=ax24)
        cbar24.set_label('[s]')
        ax24.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax24.set_title('$T_m$ swell 1')
        ########## swell 2
        VarHs = Hs_2
        varDp = Dp_2
        varTm = Tm_2
        varPercent = Hs_2**2/HsTot**2
        
        ax30 = plt.subplot2grid((4,6),(3,0), colspan=2, rowspan=1)
        hsField = ax30.pcolormesh(lon, lat, VarHs[tt], cmap=cmap, vmin=hsCmin, vmax=hsCmax)
        cbar30 = plt.colorbar(hsField, ax=ax30)
        cbar30.set_label('[m]')
        ax30.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax30.set_title('$H_s$ swell 2')
        
        ax32 = plt.subplot2grid((4,6), (3,2), sharex=ax00, sharey=ax00, colspan=2, rowspan=1)
        field = ax32.pcolormesh(lon, lat, varPercent[tt], cmap=cmap, vmin=0, vmax=1)
        cbar32 = plt.colorbar(field, ax=ax32)
        cbar32.set_label('%')
        ax32.set_title('% of total')
        
        ax34 = plt.subplot2grid((4,6), (3,4), sharex=ax00, sharey=ax00, colspan=2, rowspan=1)
        hsField = ax34.pcolormesh(lon, lat, varTm[tt], cmap=cmap, vmin=TmCmin, vmax=TmCmax)
        cbar34 = plt.colorbar(hsField, ax=ax34)
        cbar34.set_label('[s]')
        ax34.quiver(quiverX, quiverY, np.sin(varDp[tt]), np.cos(varDp[tt]), pivot='tail', scale=70)
        ax34.set_title('$T_p$ swell 2')
        
        plt.tight_layout()
        a = dt.datetime.strptime(times[tt].strftime('%Y%m%d%H%M%S'), '%Y%m%d%H%M%S').replace(tzinfo=pytz.utc)
        plt.suptitle('valid {}z from\nforecast {}'.format(a.astimezone(pytz.timezone('US/Eastern')),
                                                         url.split('/')[-1].split('m')[-1]), fontsize=12)
        
        fname = os.path.join(pathStart, 'ww3_forecast_{}.png'.format(a.strftime('%Y%m%d%H%M%S')))
        print(fname)
        plt.savefig(fname)
        plt.close()
    
    files = glob.glob(os.path.join(pathStart,'*ww3*.png'))
    ofname = kwargs.get('ofname','/todaysPlots/ww3_{}.gif'.format(a.strftime('%Y%m%dT%H%M%SZ')))
    sb.makegif(files, ofname, dt=2.5)
    
if __name__ == "__main__":
    plt.ioff()
    makeWW3forecast(ofname='/todaysPlots/todaysSouthAtlantic.gif')
    makeWW3forecast(latBounds=[34,36], lonBounds=[284,287], ofname='/todaysPlots/todaysSouthAtlantic.gif')