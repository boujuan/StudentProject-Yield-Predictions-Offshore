import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy.stats import linregress
from windrose import WindroseAxes

def prepare_data_for_MCP(df_aligned):
    X = pd.DataFrame(df_aligned['era5_WS100'])
    Y = pd.DataFrame(df_aligned['meas_WS150'].copy())
    valid_values = Y[Y.notnull().all(axis=1)].index
    x = X.loc[valid_values]
    y = Y.loc[valid_values]
    return x, y

def perform_linear_mcp(X_train, y_train, X_test):
    lin_model = LinearRegression()
    lin_model.fit(X_train, y_train)
    y_pred = lin_model.predict(X_test)
    return lin_model, y_pred

def evaluate_mcp_model(y_test, y_pred, data_name):
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    results = linregress(y_test.values.flatten(), y_pred.flatten())
    correlation = results.rvalue**2
   
    print(f'<Evaluation of MCP model for {data_name}>')
    print(f'Mean absolute error: {mae:.3f}')
    print(f'Root mean squared error: {rmse:.3f}')
    print(f'Correlation coefficient: {correlation:.3f}')

    plt.figure(figsize=(12, 8))
    plt.plot(y_test, y_pred, '.', label='Data points')
    plt.xlabel(f'Test - Measured wind speed of {data_name} [m/s]')
    plt.ylabel(f'Test - Predicted wind speed of {data_name} [m/s]')
    plt.title(f'Scatter plot of wind speed - Predicted {data_name} test data vs Actual {data_name} test data')
    reg = LinearRegression().fit(y_test, y_pred)
    plt.plot(y_test, reg.predict(y_test), color='red', label='Regression Line')
    plt.legend()
    plt.show()

def correct_wind_direction(df_aligned, data_name):
    mean_wind_dir_meas = df_aligned['meas_WD150'].mean()
    mean_wind_dir_era5 = df_aligned['era5_WD100'].mean()
    dir_difference = mean_wind_dir_meas - mean_wind_dir_era5
    df_aligned['long-term_WD150'] = (df_aligned['era5_WD100'] + dir_difference) % 360
    mean_LT_wind_dir = df_aligned['long-term_WD150'].mean()

    print(f'<Correction of wind direction for {data_name}>')
    print(f'Mean wind direction of measurement: {mean_wind_dir_meas:.2f} degrees')
    print(f'Mean wind direction of ERA5: {mean_wind_dir_era5:.2f} degrees')
    print(f'Wind directions of ERA 5 are corrected by {dir_difference:.2f} degrees')
    print(f'Mean wind direction of the measurement after the correction is {mean_LT_wind_dir:.2f} degrees')
    
    fig = plt.figure(figsize=(16, 8))
    
    ax1 = fig.add_subplot(1, 2, 1, projection='windrose')
    ax1.bar(df_aligned['meas_WD150'], df_aligned['meas_WS150'], normed=True, opening=0.8, edgecolor='white')
    ax1.set_title(f'{data_name} Wind Rose', fontsize=14)
    ax1.set_legend()

    ax2 = fig.add_subplot(1, 2, 2, projection='windrose')
    ax2.bar(df_aligned['long-term_WD150'], df_aligned['long-term_WS150'], normed=True, opening=0.8, edgecolor='white')
    ax2.set_title(f'Long-term corrected {data_name} Wind Rose', fontsize=14)
    ax2.set_legend()

    plt.show()

    return df_aligned

def calculate_mean_wind_speed(predicted_df, orig_meas, corr_meas, data_name):
    mean_wind_speed_orig = predicted_df[orig_meas].mean()
    mean_wind_speed_corr = predicted_df[corr_meas].mean()

    print(f'\n<Mean wind speeds for {data_name}>')
    print(f'Mean wind speed of the original measurement: {mean_wind_speed_orig:.3f} m/s')
    print(f'Mean wind speed of the long-term corrected measurement: {mean_wind_speed_corr:.3f} m/s')

def plot_linear_mcp_results(predicted_df, orig_meas, corr_meas, data_name):
    print(f'\n<Plotting data for {data_name}>')

    plt.figure(figsize=(16, 8))
    plt.subplot(1, 2, 1)
    plt.hist(predicted_df['meas_WS150'].dropna(), bins=30, alpha=0.7, label='Original measurement')
    plt.xlabel('Wind speed [m/s]')
    plt.ylabel('Frequency')
    plt.title(f'Short-term measured wind distribution of {data_name}')
    plt.legend()

    plt.subplot(1, 2, 2)
    plt.hist(predicted_df['long-term_WS150'], bins=30, alpha=0.7, label='Predicted measurement')
    plt.xlabel('Wind speed [m/s]')
    plt.ylabel('Frequency')
    plt.title(f'Long-term predicted wind distribution of {data_name}')
    plt.legend()

    plt.show()
    
    predicted_df['month'] = predicted_df.index.month
    monthly_avg_meas = predicted_df.groupby('month')[orig_meas].mean()
    monthly_avg_corr = predicted_df.groupby('month')[corr_meas].mean()
    months = monthly_avg_meas.index
    
    fig, ax = plt.subplots(figsize=(12, 6))

    bar_width = 0.35  

    ax.bar(months - bar_width/2, monthly_avg_meas, bar_width, label='Measured wind speed')
    ax.bar(months + bar_width/2, monthly_avg_corr, bar_width, label='Corrected wind speed')

    ax.set_xlabel('Month')
    ax.set_ylabel('Wind speed [m/s]')
    ax.set_title(f'Comparison of average monthly wind speed of {data_name} - Original vs Long-term corrected')
    ax.set_xticks(months)
    ax.set_xticklabels(['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    ax.legend()

    plt.show()

def run_lin_mcp_workflow(df_aligned, data_name):
    x, y = prepare_data_for_MCP(df_aligned)
    X_train, X_test, y_train, y_test = train_test_split(x, y, test_size=0.3, random_state=42)
    lin_model, y_pred = perform_linear_mcp(X_train, y_train, X_test)
    evaluate_mcp_model(y_test, y_pred, data_name)
    df_aligned['long-term_WS150'] = lin_model.predict(pd.DataFrame(df_aligned[['era5_WS100']]))
    df_aligned = correct_wind_direction(df_aligned, data_name)
    calculate_mean_wind_speed(df_aligned, 'meas_WS150', 'long-term_WS150', data_name)
    plot_linear_mcp_results(df_aligned, 'meas_WS150', 'long-term_WS150', data_name)
    return df_aligned

def calc_diurnal_wsand_wd(df):
        df.index = pd.to_datetime(df.index)
        df['hour'] = df.index.hour
        df_diurnal_WSWD = df.groupby('hour').mean()
        return df_diurnal_WSWD

def plot_dirunal_ws_and_wd(diurnal_index, diurnal_ws, diurnal_wd):
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
    
def calculate_energy_production(windspeed_data, power_curve_data, turbines_N9_1, turbines_N9_2, turbines_N9_3):
    from scipy.stats import weibull_min 
    
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
        shape, _, scale = weibull_min.fit(windspeed_data, floc=0)
        return shape, scale

    def weibull_pdf(ws, shape, scale):        
        return weibull_min.pdf(ws, shape, loc=0, scale=scale)

    def integrand(ws, shape, scale, power_curve_func):
        P = power_curve_func(ws)
        return P * weibull_pdf(ws, shape, scale)

    def calculate_APP(shape, scale, power_curve_func, cut_in_ws, cut_out_ws):
        from scipy.integrate import quad
        APP, error = quad(integrand, cut_in_ws, cut_out_ws, args=(shape, scale, power_curve_func), limit=100, epsabs=1e-05, epsrel=1e-05)
        return APP * T, error * T

    cut_in_ws = cut_in_windspeed(power_curve_data)
    cut_out_ws = cut_out_windspeed(power_curve_data)
    power_curve_func = power_curve_interpolated(power_curve_data)
    shape, scale = calculate_weibull_fit(windspeed_data)

    APP, error = calculate_APP(shape, scale, power_curve_func, cut_in_ws, cut_out_ws)
    
    total_farm_yield_no_wakes = ((APP/1e9) * 366)

    results = {
        "APP_one_turbine": APP / 1e6,
        "APP_error": error / 1e6,
        "AEP_N9_1": (APP/1e9) * turbines_N9_1,
        "AEP_N9_2": (APP/1e9) * turbines_N9_2,
        "AEP_N9_3": (APP/1e9) * turbines_N9_3,
        "total_farm_yield_no_wakes": total_farm_yield_no_wakes,
        "percentage_of_german_consumption": ((((APP/1e9) * 366) / 507) * 100),
        "shape": shape,
        "scale": scale
    }

    return results

def plot_weibull_distribution(windspeed_data, shape, scale):
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

def save_total_farm_yield(total_farm_yield_no_wakes):
    data = {
        'Energy Yield no wakes': [total_farm_yield_no_wakes]
    }
    df = pd.DataFrame(data)
    df.to_csv('total_farmyield_nowakes.csv', index=False)

def plot_power_curve(power_curve_data):
    plt.figure(figsize=(10, 6))
    plt.plot(power_curve_data['ws'], power_curve_data['P'], marker='o', linestyle='-', color='b')
    plt.title('Power Curve')
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('Power (kW)')
    plt.grid(True)
    plt.show()