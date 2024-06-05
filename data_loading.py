import pandas as pd
import xarray as xr
from netCDF4 import Dataset

def load_datasets(bouy6_path, bouy2_path):
    xrbuoy6 = xr.open_dataset(bouy6_path)
    xrbuoy2 = xr.open_dataset(bouy2_path)
    buoy2_file = Dataset(bouy2_path)
    buoy6_file = Dataset(bouy6_path)
    return xrbuoy6, xrbuoy2, buoy2_file, buoy6_file

def load_csv_files(file_N9_1, file_N9_2, file_N9_3):
    data_N9_1 = pd.read_csv(file_N9_1)
    data_N9_2 = pd.read_csv(file_N9_2)
    data_N9_3 = pd.read_csv(file_N9_3)
    return data_N9_1, data_N9_2, data_N9_3