import xarray as xr
from netCDF4 import Dataset

def read_csv(path):
    import pandas as pd
    data = pd.read_csv(path)
    return data

def datasets(bouy6_path, bouy2_path):
    xrbuoy6 = xr.open_dataset(bouy6_path)
    xrbuoy2 = xr.open_dataset(bouy2_path)
    buoy2_file = Dataset(bouy2_path)
    buoy6_file = Dataset(bouy6_path)
    return xrbuoy6, xrbuoy2, buoy2_file, buoy6_file

def csv_files(file_N9_1, file_N9_2, file_N9_3):
    data_N9_1 = read_csv(file_N9_1)
    data_N9_2 = read_csv(file_N9_2)
    data_N9_3 = read_csv(file_N9_3)
    return data_N9_1, data_N9_2, data_N9_3

def other_windfarm_data(file_paths):
    data_frames = []
    for file_path in file_paths:
        data_frame = read_csv(file_path)
        data_frames.append(data_frame)
    return data_frames

def create_buoy_dataframes(time, windspeed_140, winddirection_140, windspeed_200, winddirection_200):
    import pandas as pd
    # Convert time variables to pandas datetime (though it's already in datetime64[ns] format)
    time = pd.to_datetime(time, unit='ns', origin='unix')
    
    # Create a single DataFrame for the buoy with measurements at 140m and 200m heights
    df_buoy = pd.DataFrame({
        'time': time,
        'wind_speed_140m': windspeed_140,
        'wind_direction_140m': winddirection_140,
        'wind_speed_200m': windspeed_200,
        'wind_direction_200m': winddirection_200
    }).set_index('time')    
    return df_buoy

def read_LT_data_to_df(filepath):
    import pandas as pd
    df = pd.read_csv(filepath)
    df.set_index('time', inplace=True)
    return df