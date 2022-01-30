import xarray as xr
import numpy as np
import matplotlib
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LongitudeFormatter, LatitudeFormatter
import matplotlib.pyplot as plt
import geocat.viz.util as gvutil



# open bathy data
bthy = xr.open_dataset(r"H:\Python project 2021\Bathymetry-Map\data\gebco_2020_n23.0_s5.0_w80.0_e100.0.nc")


# Use custom colormap function from Earle
def custom_div_cmap(numcolors=11, name='custom_div_cmap',
                    mincol='blue', midcol='white', maxcol='red'):
    """ Create a custom diverging colormap with three colors

    Default is blue to white to red with 11 colors.  Colors can be specified
    in any way understandable by matplotlib.colors.ColorConverter.to_rgb()
    """

    from matplotlib.colors import LinearSegmentedColormap

    cmap = LinearSegmentedColormap.from_list(name=name,
                                             colors=[mincol, midcol, maxcol],
                                             N=numcolors)
    return cmap

# make negative contours, normally dashed by default, be solid
matplotlib.rcParams['contour.negative_linestyle'] = 'solid'

blon = bthy['lon']
blat = bthy['lat']
bdepth = bthy['elevation']

bdepth.data.min()
Blon,Blat = np.meshgrid(blon,blat)


blevels = [-5000, -4000, -3500,-3000, -2000, -1500, -1000, -500, -200, 0]

N = len(blevels)-1

cmap2 = custom_div_cmap(N, mincol='DarkBlue', midcol='CornflowerBlue' ,maxcol='w')

# colormap


cmap2.set_over('0.7') # set positive values (land) as light gray

## plot
fig, ax = plt.subplots(1,1, figsize=(10,7))
ax.set_aspect(1/np.cos(np.average(blat)*np.pi/180)) # set the aspect ratio for a local cartesian grid

# line contour
lws = [0.5 if level % 10 else 1 for level in blevels]
params = dict(linestyles='solid', colors=['black'], alpha=0.4)

pc = plt.contour(Blon,Blat,bdepth,levels=blevels,linewidths=lws,**params)
ax.clabel(pc, fmt='%d')
## filled contour
pc = plt.contourf(Blon,Blat,bdepth, vmin=-5000, vmax=0, levels=blevels, cmap=cmap2, extend='both')
plt.colorbar(pc, ticks=blevels, spacing='uniform')

#####
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
                                    ylim=(5,23),
                                    xlim=(80, 100),
                                    xticks=np.arange(80,101 , 5),
                                    yticks=np.arange(5, 24, 5))

    # Use geocat.viz.util convenience function to add minor and major tick lines
gvutil.add_major_minor_ticks(ax, labelsize=14)
gvutil.add_lat_lon_ticklabels(ax)

gvutil.set_titles_and_labels(ax,
                                 maintitle= 'Bathymetry Map of Bay of Bengal',
                                 maintitlefontsize= 16,
                                 ylabel='Latitude',
                                 xlabel='Longitude',
                                 labelfontsize=16)

# Remove the degree symbol from tick labels
ax.yaxis.set_major_formatter(LatitudeFormatter(degree_symbol=''))
ax.xaxis.set_major_formatter(LongitudeFormatter(degree_symbol=''))

p = ax.contourf(blon,
                        blat,
                        bdepth,
                        vmin=-5000,
                        vmax=0,
                        cmap=cmap2,
                        levels=blevels,
                        extend = 'both')

cbar = plt.colorbar(p, ticks=blevels,spacing='uniform',drawedges=True,orientation='vertical',shrink = 0.85)
cbar.set_label('Depth (m)',fontsize = 12)
cbar.ax.tick_params(labelsize = 12)
plt.savefig('bathymetrymap.png',dpi = 300)
