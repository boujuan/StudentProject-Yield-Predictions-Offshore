import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.io.shapereader import Reader

def plot_wind_farm(data, title, ax, color):
    ax.scatter(data['x'], data['y'], transform=ccrs.UTM(zone=32), label=title, color=color, s=10)
    ax.legend()

def create_base_map():
    fig = plt.figure(figsize=(10, 15))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.RIVERS)
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN)
    return fig, ax

def plot_wind_farms_and_buoys(shapefiles_path, data_N9_1, data_N9_2, data_N9_3):
    fig = plt.figure(figsize=(10, 15))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.set_facecolor('#9bb7df')
    country_colors = {
        f'{shapefiles_path}DEU/DEU_adm1.shp': 'lightgreen',
        f'{shapefiles_path}DNK/gadm36_DNK_1.shp': 'lightblue',
        f'{shapefiles_path}NLD/gadm36_NLD_1.shp': 'beige'
    }

    for shapefile_path, color in country_colors.items():
        ax.add_geometries(Reader(shapefile_path).geometries(),
                          ccrs.PlateCarree(),
                          facecolor=color, edgecolor='black')

    plot_wind_farm(data_N9_1, 'Wind Farm N9.1', ax, 'blue')
    plot_wind_farm(data_N9_2, 'Wind Farm N9.2', ax, 'green')
    plot_wind_farm(data_N9_3, 'Wind Farm N9.3', ax, 'purple')

    ax.plot(5.521086, 54.40289, 'm^', markersize=7, transform=ccrs.PlateCarree(), label='Buoy 6')
    ax.plot(5.792266, 54.50248, 'k^', markersize=7, transform=ccrs.PlateCarree(), label='Buoy 2')

    ax.text(7.5, 53.25, 'Germany', transform=ccrs.Geodetic(), fontsize=10)
    ax.text(5.6, 53.1, 'Netherlands', transform=ccrs.Geodetic(), fontsize=10)

    ax.set_extent([4.5, 9, 53, 55], crs=ccrs.PlateCarree())
    ax.gridlines(draw_labels=True)
    ax.legend(loc='upper right')

    plt.title('Wind Farms in the North Sea')
    plt.show()
    
def plot_wind_farms_and_buoys_zoomed(data_N9_1, data_N9_2, data_N9_3):
    fig = plt.figure(figsize=(10, 15))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.set_facecolor('#9bb7df')
    
    plot_wind_farm(data_N9_1, 'Wind Farm N9.1', ax, 'blue')
    plot_wind_farm(data_N9_2, 'Wind Farm N9.2', ax, 'green')
    plot_wind_farm(data_N9_3, 'Wind Farm N9.3', ax, 'purple')
    
    ax.plot(5.521086, 54.40289, 'm^', markersize=7, transform=ccrs.PlateCarree(), label='Buoy 6')
    ax.plot(5.792266, 54.50248, 'k^', markersize=7, transform=ccrs.PlateCarree(), label='Buoy 2')
    
    ax.set_extent([5.5, 6.025, 54.35, 54.65], crs=ccrs.PlateCarree())
    ax.gridlines(draw_labels=True)
    ax.legend(loc='upper right')
    
    plt.title('Wind Farms in the North Sea')
    plt.show()


