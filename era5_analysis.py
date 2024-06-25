import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from windrose import WindroseAxes

def load_era5_data(path, start_year, end_year):
    all_files = [f for f in os.listdir(path) if f.startswith('ERA5_N-9_') and f.endswith('.csv')]
    all_files.sort()
    era5_data_list = [pd.read_csv(os.path.join(path, file)) for file in all_files 
                      if start_year <= int(file.split('_')[-1].split('.')[0]) <= end_year]
    return pd.concat(era5_data_list, ignore_index=True)

def process_era5_data(era5_data):
    era5_data['WS100'] = np.sqrt(era5_data['u100']**2 + era5_data['v100']**2)
    era5_data['WS10'] = np.sqrt(era5_data['u10']**2 + era5_data['v10']**2)
    era5_data['WD100'] = (np.arctan2(era5_data['u100'], era5_data['v100']) * 180 / np.pi + 180) % 360 
    era5_data['WD10'] = (np.arctan2(era5_data['u10'], era5_data['v10']) * 180 / np.pi + 180) % 360
    era5_data['time'] = pd.to_datetime(era5_data['Time [UTC]'])
    era5_data['year'] = era5_data['time'].dt.year
    era5_data['month'] = era5_data['time'].dt.month
    return era5_data

def calculate_averages(era5_data):
    overall_avg = era5_data[['WS100', 'WS10']].mean()
    yearly_avg = era5_data.groupby('year')[['WS100', 'WS10']].mean()
    monthly_avg = era5_data.groupby('month')[['WS100','WD100', 'WS10','WD10']].mean()
    return yearly_avg, monthly_avg, overall_avg

def check_data_gaps(era5_data):
    era5_data = era5_data.set_index('time')
    full_time_range = pd.date_range(start=era5_data.index.min(), end=era5_data.index.max(), freq='h')
    era5_data = era5_data.reindex(full_time_range)
    missing_data = era5_data[era5_data.isnull().any(axis=1)]
    
    total_expected = len(full_time_range)
    total_actual = len(era5_data.dropna())
    availability = (total_actual / total_expected) * 100
    
    print(f'Data Availability of the ERA5 data is {availability:.2f}%')
    if not missing_data.empty:
        print('Missing time periods are:')
        print(missing_data.index)
    else:
        print('No data gaps are found.')
    
    return missing_data

def plot_histogram(era5_data):
    plt.figure(figsize=(10, 5))
    plt.hist(era5_data['WS100'], bins=30, alpha=0.5, label='100m')
    plt.hist(era5_data['WS10'], bins=30, alpha=0.5, label='10m')
    plt.xlabel('Wind speed [m/s]')
    plt.ylabel('Frequency')
    plt.title('Histogram of wind speed of reanalysis data ERA 5')
    plt.legend()
    plt.show()

def plot_wind_rose(era5_data):
    ax = WindroseAxes.from_ax()
    ax.bar(era5_data['WD100'], era5_data['WS100'], normed=True, opening=0.8, edgecolor='white')
    ax.set_title('Wind rose of ERA5 data')
    ax.set_legend()
    plt.show()

def plot_yearly_average_with_trendline(yearly_avg):
    years = yearly_avg.index
    ws100_year = yearly_avg['WS100']
    ws10_year = yearly_avg['WS10']
    
    z_100m = np.polyfit(years, ws100_year, 1)
    z_10m = np.polyfit(years, ws10_year, 1)
    p_100m = np.poly1d(z_100m)
    p_10m = np.poly1d(z_10m)
    
    plt.figure(figsize=(10, 5))
    plt.plot(years, ws100_year, marker='o', label='Wind speed @100m')
    plt.plot(years, ws10_year, marker='o', label='Wind speed @10m')
    plt.plot(years, p_100m(years), linestyle='--', label='100m Trendline', color='blue')
    plt.plot(years, p_10m(years), linestyle='--', label='10m Trendline', color='orange')
    
    eq_100m = f'100m: y = {z_100m[0]:.3f}x + {z_100m[1]:.3f}'
    eq_10m = f'10m: y = {z_10m[0]:.3f}x + {z_10m[1]:.3f}'
    plt.text(0.05, 0.95, eq_100m, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top', color='blue')
    plt.text(0.05, 0.90, eq_10m, transform=plt.gca().transAxes, fontsize=10, verticalalignment='top', color='orange')
    
    plt.xlabel('Year')
    plt.ylabel('Wind speed [m/s]')
    plt.title('Yearly average wind speeds of ERA5 with trendlines')
    plt.legend()
    plt.grid(True)
    plt.show()

def plot_monthly_average(monthly_avg):
    fig, ax1 = plt.subplots(figsize=(10, 4))
    months = monthly_avg.index
    ws100 = monthly_avg['WS100']
    wd100 = monthly_avg['WD100']

    ax1.bar(months, ws100, width=0.4, label='Wind Speed 100m (ERA 5)', color='b', align='center')
    ax1.set_xlabel('Month')
    ax1.set_ylabel('Wind speed [m/s]')
    ax1.set_title('Monthly average wind speed and direction - ERA5')
    ax1.set_xticks(months)
    ax1.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    
    ax2 = ax1.twinx()
    ax2.plot(months, wd100, 'r--o', label='Wind Direction 100m (ERA 5)', markersize=5)
    ax2.set_ylabel('Wind Direction [degrees]', color='r')
    ax2.tick_params(axis='y', labelcolor='r')
    
    fig.legend(loc="upper right", bbox_to_anchor=(1,1), bbox_transform=ax1.transAxes)
    plt.show()

def analyze_era5_data(era5_path, start_year, end_year):
    era5_data = load_era5_data(era5_path, start_year, end_year)
    era5_data = process_era5_data(era5_data)
    
    yearly_avg, monthly_avg, overall_avg = calculate_averages(era5_data)
    missing_data = check_data_gaps(era5_data)   

    plot_histogram(era5_data)
    plot_wind_rose(era5_data)
    plot_monthly_average(monthly_avg)
    plot_yearly_average_with_trendline(yearly_avg)

    print('\nThe average wind speed of ERA 5 over the whole period in m/s:')
    print(overall_avg)

    return era5_data, yearly_avg, monthly_avg, overall_avg, missing_data

def resample_and_merge_data(df_buoy, df_era5, data_name):
    df_buoy['time'] = pd.to_datetime(df_buoy['time'])
    df_buoy.set_index('time', inplace=True)
    df_buoy = df_buoy.resample('h').mean()  # Resample the data to hourly frequency

    # Ensure df_era5 has a 'time' column as index
    if 'time' in df_era5.columns:
        df_era5.set_index('time', inplace=True)
    elif df_era5.index.name != 'time':
        df_era5.index.name = 'time'

    # Merge the dataframes using the index
    df_aligned = pd.merge(df_buoy, df_era5, left_index=True, right_index=True, how='right')

    # Calculate data period
    data_start = df_aligned.index.min()
    data_end = df_aligned.index.max()

    print(f'The period of merged data({data_name} & ERA 5) is: {data_start} to {data_end}')
   
    return df_aligned

def calculate_statistics(df_aligned, data_name):
    from scipy.stats import linregress
    valid_data = df_aligned.dropna(subset=['meas_WS150', 'meas_WD150', 'era5_WS100', 'era5_WD100'])
    results = linregress(valid_data['meas_WS150'], valid_data['era5_WS100'])
    mean_meas_WS = valid_data['meas_WS150'].mean()
    mean_era5_WS = valid_data['era5_WS100'].mean()
    mean_meas_WD = valid_data['meas_WD150'].mean()
    mean_era5_WD = valid_data['era5_WD100'].mean()
    
    print(f'\n<Statistics for {data_name}>')
    print(f'Correlation coefficient between the measurement and Era5 wind speed: {results.rvalue**2:.3f}')
    print(f'Mean wind speed of the measurement at 150m: {mean_meas_WS:.3f} m/s')
    print(f'Mean wind speed of Era 5 data at 100m: {mean_era5_WS:.3f} m/s')
    print(f'Mean wind direction of the measurement at 150m: {mean_meas_WD:.3f} degree')
    print(f'Mean wind direction of Era 5 data at 100m: {mean_era5_WD:.3f} degree')

def plot_meas_era5_comparison_WS(df_aligned, data_name):
    from sklearn.linear_model import LinearRegression
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))
    
    ax1.hist(df_aligned['meas_WS150'].dropna(), bins=30, alpha=0.7, label=f'{data_name}', color='blue')
    ax1.set_title(f'Measurement {data_name} - Wind speed distribution', fontsize=14)
    ax1.set_xlabel('Wind speed at 150m [m/s]', fontsize=12)
    ax1.set_ylabel('Frequency', fontsize=12)
    ax1.legend(fontsize=12)
    ax1.tick_params(axis='both', which='major', labelsize=12)
    
    ax2.hist(df_aligned['era5_WS100'].dropna(), bins=30, alpha=0.7, label='ERA 5', color='blue')
    ax2.set_title('ERA5 - Wind speed distribution', fontsize=14)
    ax2.set_xlabel('Wind speed at 100m [m/s]', fontsize=12)
    ax2.set_ylabel('Frequency', fontsize=12)
    ax2.legend(fontsize=12)
    ax2.tick_params(axis='both', which='major', labelsize=12)
    
    plt.tight_layout()
    plt.show()
    
    plt.figure(figsize=(16, 8))
    plt.scatter(df_aligned['meas_WS150'], df_aligned['era5_WS100'], alpha=0.5, label=f'{data_name} data points')
    plt.xlabel(f'{data_name} wind speed at 150m [m/s]')
    plt.ylabel('ERA5 wind speed at 100m [m/s]')
    plt.title(f'Scatter plot of wind speed - {data_name} vs ERA 5')
    
    valid_data = df_aligned.dropna(subset=['meas_WS150', 'era5_WS100'])
    X = valid_data['meas_WS150'].values.reshape(-1, 1)
    y = valid_data['era5_WS100'].values.reshape(-1, 1)
    reg = LinearRegression().fit(X, y)
    y_pred = reg.predict(X)
    plt.plot(valid_data['meas_WS150'], y_pred, color='red', label='Regression Line')
    plt.legend(fontsize=12)
    
    plt.show()

def plot_meas_era5_comparison_WD(df_aligned, data_name):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8), subplot_kw=dict(projection='windrose'))
    
    ax1.bar(df_aligned['meas_WD150'], df_aligned['meas_WS150'], normed=True, opening=0.8, edgecolor='white')
    ax1.set_title(f'{data_name} Wind Rose', fontsize=14)
    ax1.set_legend()

    ax2.bar(df_aligned['era5_WD100'], df_aligned['era5_WS100'], normed=True, opening=0.8, edgecolor='white')
    ax2.set_title('ERA5 Wind Rose', fontsize=14)
    ax2.set_legend()

    plt.tight_layout()
    plt.show()

def analyze_buoy_data(meas_data, era5_data, buoy_name):
    df_buoy = meas_data[['time', f'ws{buoy_name}_150m', f'wd{buoy_name}_150m']].copy()
    df_buoy.rename(columns={f'ws{buoy_name}_150m': 'meas_WS150', f'wd{buoy_name}_150m': 'meas_WD150'}, inplace=True)

    era5_selected = era5_data[['WS100', 'WD100']].copy()
    era5_selected.rename(columns={'WS100': 'era5_WS100', 'WD100': 'era5_WD100'}, inplace=True)

    aligned_data = resample_and_merge_data(df_buoy, era5_selected, f'Buoy{buoy_name}')
    calculate_statistics(aligned_data, f'Buoy{buoy_name}')
    plot_meas_era5_comparison_WS(aligned_data, f'Buoy{buoy_name}')
    plot_meas_era5_comparison_WD(aligned_data, f'Buoy{buoy_name}')

    return aligned_data