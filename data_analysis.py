import pandas as pd
import numpy as np

def check_data_gaps(dataframe):
    
    dataframe.index = dataframe.index.floor('s')  # Truncate microseconds

    # Round timestamps to the nearest 10 minutes
    dataframe.index = dataframe.index.round('10min')
    
    # Generate a complete time range based on the data frequency
    full_time_range = pd.date_range(start=dataframe.index.min(), end=dataframe.index.max(), freq='10min')
    dataframe = dataframe.reindex(full_time_range)
    
    missing_data = dataframe[dataframe.isnull().any(axis=1)]
    
    total_expected = len(full_time_range)
    total_actual = len(dataframe.dropna())
    availability = (total_actual / total_expected) * 100
    
    print(f"Data Availability is {availability:.2f}%")
    
    if not missing_data.empty:
        print("Missing time periods are:")
        print(missing_data.index)
    else:
        print("No data gaps are found.")
    
    return missing_data

def drop_duplicates(dataframe):
    # Identify duplicate rows
    duplicates = dataframe[dataframe.duplicated(keep=False)]
    
    # Drop duplicates
    no_duplicate_data = dataframe.drop_duplicates()
    
    # Calculate data availability
    total_expected = len(dataframe)
    total_actual = len(no_duplicate_data)
    availability = (total_actual / total_expected) * 100
    
    print(f"Data Availability is {availability:.2f}%")
    
    if not duplicates.empty:
        # Set display options to show the entire DataFrame
        #with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(duplicates)
    else:
        print("No duplicates are found.")
    
    return duplicates

def explore_and_prefilter_df(dataframe):
   check_data_gaps(dataframe)
   drop_duplicates(dataframe)
   
def replace_nan_and_select_1yr(dataframe):
    #dataframe = dataframe.fillna(dataframe.mean())
    dataframe = dataframe.ffill()
    dataframe = dataframe.iloc[:52560]
    return dataframe

def group_month_and_calc_mean(df):
    df.index = pd.to_datetime(df.index)
    df['month'] = df.index.month
    df_month_mean = df.groupby('month').mean()
    return df_month_mean

def group_month_and_calc_mean_year(df):
    df = df.copy()  # Ensure working with a copy of the DataFrame
    df.index = pd.to_datetime(df.index)
    df.loc[:, 'year'] = df.index.year  # Use .loc to avoid the SettingWithCopyWarning
    df_month_mean = df.groupby('year').mean()
    return df_month_mean

# Calculate yearly statistics for wind speed
def calc_yearly_statistics(windspeed, winddirection):
    yearly_mean_ws = np.mean(windspeed)
    yearly_std_ws = np.std(windspeed)
    yearly_mean_wd = np.mean(winddirection)
    yearly_std_wd = np.std(winddirection)
    print(f"Yearly Mean of Wind Speed: {yearly_mean_ws:.2f}, Standard Deviation: {yearly_std_ws:.2f}")
    print(f"Yearly Mean of Wind Direction: {yearly_mean_wd:.2f}, Standard Deviation: {yearly_std_wd:.2f}")
    
def calc_diurnal_wsand_wd(df):
        df.index = pd.to_datetime(df.index)
        df['hour'] = df.index.hour
        df_diurnal_WSWD = df.groupby('hour').mean()
        return df_diurnal_WSWD
    
def calculate_aep(windspeed_data, power_curve_data, turbines_N9_1, turbines_N9_2, turbines_N9_3):
    # Constants
    T = 8760  # total hours/year [h]
    rho = 1.225  # air density [kg/m^3]
    D = 240  # rotor diameter [m]
    A = np.pi * (D / 2)**2  # swept area [m^2]

    def cut_in_windspeed(power_curve_data):
        return power_curve_data.loc[power_curve_data['P'] > 0, 'ws'].min()

    def cut_out_windspeed(power_curve_data):
        return power_curve_data.loc[power_curve_data['P'] > 0, 'ws'].max()

    def power_curve_interpolated(power_curve_data):
        from scipy.interpolate import interp1d
        power_curve_func = interp1d(power_curve_data['ws'], power_curve_data['P'], fill_value="extrapolate")
        return power_curve_func

    def calculate_weibull_fit(windspeed_data):
        from scipy.stats import weibull_min
        shape, _, scale = weibull_min.fit(windspeed_data, floc=0)  # floc=0 => location parameter defaults to 0
        return shape, scale

    def weibull_pdf(ws, shape, scale):
        from scipy.stats import weibull_min
        return weibull_min.pdf(ws, shape, loc=0, scale=scale)

    def integrand(ws, shape, scale, power_curve_func):
        P = power_curve_func(ws)  # Use interpolated power curve values
        return P * weibull_pdf(ws, shape, scale)

    def calculate_APP(shape, scale, power_curve_func, cut_in_ws, cut_out_ws):
        from scipy.integrate import quad
        APP, error = quad(integrand, cut_in_ws, cut_out_ws, args=(shape, scale, power_curve_func), limit=100, epsabs=1e-05, epsrel=1e-05)
        return APP * T, error * T  # Multiply by total hours per year to get AEP

    # Process data
    cut_in_ws = cut_in_windspeed(power_curve_data)
    cut_out_ws = cut_out_windspeed(power_curve_data)
    power_curve_func = power_curve_interpolated(power_curve_data)
    shape, scale = calculate_weibull_fit(windspeed_data)

    # Calculate APP (Annual Power Production)
    APP, error = calculate_APP(shape, scale, power_curve_func, cut_in_ws, cut_out_ws)
    
    results = {
        "APP_one_turbine": APP / 1e6,
        "APP_error": error / 1e6,
        "AEP_N9_1": (APP/1e9) * turbines_N9_1,
        "AEP_N9_2": (APP/1e9) * turbines_N9_2,
        "AEP_N9_3": (APP/1e9) * turbines_N9_3,
        "AEP_total": (APP/1e9) * 366,
        "percentage_of_german_consumption": ((((APP/1e9) * 366)/507)*100),
        "shape": shape,
        "scale": scale
    }
    
    return results

def print_aep_results(results, turbines_N9_1, turbines_N9_2, turbines_N9_3):
    # Print results
    print(f"APP of one Turbine: {results['APP_one_turbine']:.4f} GWh")
    print(f"Estimated error: {results['APP_error']:.4f} GWh")
    print(f"Annual Energy Production of N-9.1 ({turbines_N9_1} Turbines): {results['AEP_N9_1']:.4f} TWh")
    print(f"Annual Energy Production of N-9.2 ({turbines_N9_2} Turbines): {results['AEP_N9_2']:.4f} TWh")
    print(f"Annual Energy Production of N-9.3 ({turbines_N9_3} Turbines): {results['AEP_N9_3']:.4f} TWh")
    print(f"Total Energy Production of all three fields (366 Turbines): {results['AEP_total']:.4f} TWh")
    print(f"This is {results['percentage_of_german_consumption']:.2f}% of the electricity consumed in one yr in Germany.")