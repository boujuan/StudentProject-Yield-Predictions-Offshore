import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

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