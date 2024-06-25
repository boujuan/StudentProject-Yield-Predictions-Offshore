import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from windrose import WindroseAxes

def plot_wind_farm(data, title, ax, color):
    ax.scatter(data['x'], data['y'], transform=ccrs.UTM(zone=32), label=title, color=color, s=10)
    ax.legend()

def create_base_map():
    import cartopy.feature as cfeature
    fig = plt.figure(figsize=(10, 15))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.RIVERS)
    ax.add_feature(cfeature.LAND, edgecolor='black')
    ax.add_feature(cfeature.OCEAN)
    return fig, ax

def plot_wind_farms_and_buoys(shapefiles_path, data_N9_1, data_N9_2, data_N9_3, other_wind_farm_data):
    fig = plt.figure(figsize=(10, 15))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.Mercator())
    ax.set_facecolor('#9bb7df')
    country_colors = {
        f'{shapefiles_path}DEU/DEU_adm1.shp': 'lightgreen',
        f'{shapefiles_path}DNK/gadm36_DNK_1.shp': 'lightblue',
        f'{shapefiles_path}NLD/gadm36_NLD_1.shp': 'beige'
    }

    for shapefile_path, color in country_colors.items():
        from cartopy.io.shapereader import Reader
        ax.add_geometries(Reader(shapefile_path).geometries(),
                          ccrs.PlateCarree(),
                          facecolor=color, edgecolor='black')

    plot_wind_farm(data_N9_1, 'Wind Farm N9.1', ax, 'blue')
    plot_wind_farm(data_N9_2, 'Wind Farm N9.2', ax, 'green')
    plot_wind_farm(data_N9_3, 'Wind Farm N9.3', ax, 'purple')

    # Plot other wind farms without labels and in a less conspicuous way
    for data_frame in other_wind_farm_data:
        ax.scatter(data_frame['x'], data_frame['y'], transform=ccrs.UTM(zone=32), color='gray', s=5)

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
    
def plot_buoy_data(time2, windspeed2, time6, windspeed6, windspeed_mcp_buoy2, windspeed_mcp_buoy6):
    # Creating a figure with 4 subplots arranged in a 2x2 grid
    fig, axes = plt.subplots(2, 2, figsize=(13, 8), sharey=True, sharex=True)

    axes[0, 0].plot(time6, windspeed6[:, 0, 0, 2])
    axes[0, 0].set_title('Buoy 6')
    axes[0, 0].set_xlabel('Time')
    axes[0, 0].set_ylabel('Wind Speed (m/s)')

    axes[0, 1].plot(time2, windspeed2[:, 0, 0, 2])
    axes[0, 1].set_title('Buoy 2')
    axes[0, 1].set_xlabel('Time')
    axes[0, 1].set_ylabel('Wind Speed (m/s)')

    axes[1, 0].plot(time6, windspeed_mcp_buoy6[:, 0, 0, 2])
    axes[1, 0].set_title('MCP Data buoy 6')
    axes[1, 0].set_xlabel('Time')
    axes[1, 0].set_ylabel('Wind Speed (m/s)')

    axes[1, 1].plot(time2, windspeed_mcp_buoy2[:, 0, 0, 2])
    axes[1, 1].set_title('MCP Data buoy 2')
    axes[1, 1].set_xlabel('Time')
    axes[1, 1].set_ylabel('Wind Speed (m/s)')

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Display the plots
    plt.show()
    
def plot_scatter_with_regression(x, y, xlabel, ylabel, title):
    from scipy.stats import linregress
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(x, y)

    # Create scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(x, y, label='Data points') #s=1 change scatter point size 

    # Plot regression line
    plt.plot(x, slope * x + intercept, color='red', label=f'Regression line (R^2 = {r_value**2:.2f})')

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.legend()
    plt.show()
    
def plot_interpolated_wind_speeds(filtered_buoy6, filtered_buoy2, ws6_150m, ws2_150m, start_index=0, end_index=None, marker=None):
    fig, axes = plt.subplots(1, 2, figsize=(10, 3), sharey=True, sharex=True)

    if marker:
        axes[0].scatter(filtered_buoy6.index[start_index:end_index], ws6_150m[start_index:end_index], marker=marker)
        axes[1].scatter(filtered_buoy2.index[start_index:end_index], ws2_150m[start_index:end_index], marker=marker)
    else:
        axes[0].plot(filtered_buoy6.index[start_index:end_index], ws6_150m[start_index:end_index])
        axes[1].plot(filtered_buoy2.index[start_index:end_index], ws2_150m[start_index:end_index])

    axes[0].set_title('Wind Speed for interpolated 150 m at Buoy 6')
    axes[0].set_xlabel('Time')
    axes[0].set_ylabel('Wind Speed (m/s)')
    axes[0].tick_params(axis='x', rotation=45)

    axes[1].set_title('Wind Speed for interpolated 150 m at Buoy 2')
    axes[1].set_xlabel('Time')
    axes[1].set_ylabel('Wind Speed (m/s)')
    axes[1].tick_params(axis='x', rotation=45)

    # Adjust layout to prevent overlap
    plt.tight_layout()

    # Display the plots
    plt.show()
    
def plot_histogram_mounthly_mean(monthly_mean_ws, monthly_mean_wd):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot wind speed histogram on the left y-axis
    ax1.bar(months, monthly_mean_ws, width=0.4, label='Wind Speed 150m (Buoy 6)', color='b', align='center')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Wind Speed (m/s)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Create a second y-axis to plot wind direction
    ax2 = ax1.twinx()
    ax2.plot(months, monthly_mean_wd, 'r--o', label='Wind Direction 150m (Buoy 6)', markersize=5)
    ax2.set_ylabel('Wind Direction (degrees)', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.title('Monthly Profile of Wind Speed and Wind Direction for Buoy 6')
    plt.grid(True)
    plt.show()
    
def plot_diurnal_ws_and_wd(diurnal_index, diurnal_ws, diurnal_wd):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    # Plot wind speed histogram on the left y-axis
    ax1.bar(diurnal_index, diurnal_ws, width=0.4, label='Wind Speed 150m (Buoy 6)', color='b', align='center')
    ax1.set_xlabel('Hour of the Day')
    ax1.set_ylabel('Wind Speed (m/s)', color='b')
    ax1.tick_params(axis='y', labelcolor='b')
    # Create a second y-axis to plot wind direction
    ax2 = ax1.twinx()
    ax2.plot(diurnal_index, diurnal_wd, 'r--o', label='Wind Direction 150m (Buoy 6)', markersize=5)
    ax2.set_ylabel('Wind Direction (degrees)', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.title('Diurnal Profile of Wind Speed and Wind Direction for Buoy 6')
    plt.grid(True)
    plt.show()
    
def plot_wind_rose(wd, ws, title):    
    ax = WindroseAxes.from_ax()
    ax.bar(wd, ws, normed=True, opening=0.8, edgecolor='white')
    ax.set_legend()
    plt.title(title)
    plt.show()
    
def plot_weibull_distribution(windspeed_data, shape, scale):
    import numpy as np
    from scipy.stats import weibull_min
    plt.figure(figsize=(10, 6))
    ws_range = np.linspace(0, max(windspeed_data), 100)
    weibull_pdf_values = weibull_min.pdf(ws_range, shape, loc=0, scale=scale)

    plt.hist(windspeed_data, bins=30, density=True, alpha=0.6, color='blue', edgecolor='black', label='Wind Speed Data')
    plt.plot(ws_range, weibull_pdf_values, 'r-', lw=2, label='Weibull Distribution')
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Density')
    plt.title('Wind Speed Data and Weibull Distribution Fit')
    plt.legend()
    plt.grid(True)
    plt.show()
    
def plot_power_curve(power_curve_data):
    plt.figure(figsize=(10, 6))
    plt.plot(power_curve_data['ws'], power_curve_data['P'], marker='o', linestyle='-', color='b')
    plt.title('Power Curve')
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Power (kW)')
    plt.grid(True)
    plt.show()
    
def plot_wind_rose(wd, ws, title):
    ax = WindroseAxes.from_ax()
    ax.bar(wd, ws, normed=True, opening=0.8, edgecolor='white')
    ax.set_legend()
    plt.title(title)
    plt.show()