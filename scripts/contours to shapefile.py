from shapely import geometry
import matplotlib.pyplot as plt
import matplotlib
from matplotlib import cm
import numpy as np
import fiona
import os,json
from descartes.patch import PolygonPatch
import xarray as xr
import rasterio.features

# load data
bthy = xr.open_dataset(r"H:\Python project 2021\Bathymetry-Map\data\gebco_2020_n23.0_s5.0_w80.0_e100.0.nc")

blon = bthy['lon']
blat = bthy['lat']
bdepth = bthy['elevation']

Blon,Blat = np.meshgrid(blon,blat)

## custom tick
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

blevels = list(np.arange(-5000,-3000,500)) + list(np.arange(-3000,-1000,250)) + list(np.arange(-1000,-100,200)) + list(np.arange(-100,0,25)) + [0]
N = len(blevels)-1
##
fig, ax = plt.subplots(1,1, figsize=(10,7))
ax.set_aspect(1/np.cos(np.average(blat)*np.pi/180)) # set the aspect ratio for a local cartesian grid

# line contour
lws = [0.5 if level % 10 else 1 for level in blevels]
params = dict(linestyles='solid', colors=['black'], alpha=0.4)

pc = plt.contour(Blon,Blat,bdepth,levels=blevels,linewidths=lws,**params)
ax.clabel(pc, fmt='%d')
###
len(pc.collections)

from shapely import geometry
for col in pc.collections:
    # Loop through all polygons that have the same intensity level
    for contour_path in col.get_paths():
        # Create the polygon for this intensity level
        # The first polygon in the path is the main one, the following ones are "holes"
        for ncp,cp in enumerate(contour_path.to_polygons()):
            x = cp[:,0]
            y = cp[:,1]
            new_shape = geometry.Polygon([(i[0], i[1]) for i in zip(x,y)])
            if ncp == 0:
                poly = new_shape
            else:
                # Remove the holes if there are any
                poly = poly.difference(new_shape)
                # Can also be left out if you want to include all rings



















###########################################################################################
## Stroring the contour result
# create lookup table for levels
lvl_lookup = dict(zip(pc.collections, pc.levels))

# loop over collections (and polygons in each collection), store in list for fiona
PolyList = []
for col in pc.collections:
    z = lvl_lookup[col]  # the value of this level
    for contour_path in col.get_paths():
        # create the polygon for this level
        for ncp, cp in enumerate(contour_path.to_polygons()):
            lons = cp[:, 0]
            lats = cp[:, 1]
            new_shape = geometry.Polygon([(i[0], i[1]) for i in zip(lons, lats)])
            if ncp == 0:
                poly = new_shape  # first shape
            else:
                poly = poly.difference(new_shape)  # Remove the holes

            PolyList.append({'poly': poly, 'props': {'z': z}})


# define ESRI schema, write each polygon to the file
outname = r"H:\Python project 2021\Bathymetry-Map\data"
outfi=os.path.join(outname,'shaped_contour.shp')

schema = {'geometry': 'Polygon','properties': {'z': 'float'}}


##
with fiona.collection(outfi, "w", "ESRI Shapefile", schema) as output:
    for p in PolyList:
        output.write({'properties': p['props'],
            'geometry': geometry.mapping(p['poly'])})

# save the levels and global min/max as a separate json for convenience
Lvls={'levels':pc.levels.tolist(),'min':bdepth.min(),'max':bdepth.max()}
with open(os.path.join(outname,'levels.json'), 'w') as fp:
    json.dump(Lvls, fp)