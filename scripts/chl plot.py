import xarray as xr
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import geocat.viz.util as gvutil

jan = xr.open_dataset(r"H:\Python project 2021\Bathymetry-Map\data\A20200012020031.L3m_MO_CHL.x_chlor_a.nc")

# extracting lon lat
blon = jan['lon']
blat = jan['lat']
chl = jan['chlor_a']

Blon,Blat = np.meshgrid(blon,blat)

blevels = [0.05,0.1,0.3,0.5,0.7,0.9,1,2,3,4,5]

N = len(blevels)-1

# custom colormap
from matplotlib.colors import LinearSegmentedColormap
cmap = LinearSegmentedColormap.from_list('jet',N=256,colors=[(0, 'DarkBlue'),(0.25,'#33F7FF'),(0.5, '#40FF33'),(0.75, '#F3FF33'),(1, 'DarkRed')])
##

# Simple Plot
fig, ax = plt.subplots(1,1, figsize=(10,7))
ax.set_aspect(1/np.cos(np.average(blat)*np.pi/180)) # set the aspect ratio for a local cartesian grid


pc = plt.contourf(Blon,Blat,chl, vmin=0.1, vmax=5, levels=blevels, cmap=cmap, extend='both')
plt.colorbar(pc, ticks=blevels, spacing='uniform')
###

#        Customize Plot
fig = plt.figure(figsize=(7.6, 6.5))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.coastlines()
ax.add_feature(cfeature.LAND,
                   facecolor="darkgray",
                   edgecolor='black',
                   linewidths=1,
                   zorder=2)

# Usa geocat.viz.util convenience function to set axes parameters
gvutil.set_axes_limits_and_ticks(ax,
                                    ylim=(5,25),
                                    xlim=(80, 100),
                                    xticks=np.arange(80,101 , 5),
                                    yticks=np.arange(5, 26, 5))

    # Use geocat.viz.util convenience function to add minor and major tick lines
gvutil.add_major_minor_ticks(ax, labelsize=14)
gvutil.add_lat_lon_ticklabels(ax)

gvutil.set_titles_and_labels(ax,
                                 maintitle= 'Chlorophyll concentration map in Jan,2020',
                                 maintitlefontsize= 16,
                                 ylabel='Latitude',
                                 xlabel='Longitude',
                                 labelfontsize=16)

# Remove the degree symbol from tick labels
ax.yaxis.set_major_formatter(LatitudeFormatter(degree_symbol=''))
ax.xaxis.set_major_formatter(LongitudeFormatter(degree_symbol=''))

# plot contourmap
p = ax.contourf(blon,
                        blat,
                        chl,
                        vmin=0.05,
                        vmax=5,
                        cmap=cmap,
                        levels=blevels,
                        extend = 'both')

cbar = plt.colorbar(p, ticks=blevels,spacing='uniform',drawedges=True,orientation='vertical',shrink = 0.95)
cbar.set_label('mg/m3',fontsize = 12)
cbar.ax.tick_params(labelsize = 12)
plt.savefig('chl_jan2020.png',dpi = 300)

