import pandas as pd
import foxes
import foxes.variables as FV
import foxes.constants as FC
import os

def load_layouts(areas):
    layout_paths = [f"NoWake_Layout_{area}.csv" for area in areas]
    layout_dfs = [pd.read_csv(file) for file in layout_paths]
    geo_cluster_turb_df = pd.concat(layout_dfs, ignore_index=True)
    return [geo_cluster_turb_df, "gem.Layout N9 Cluster"]

def load_turbine_layouts(turbines_area_of_interest_path, areas):
    turb_files = os.listdir(turbines_area_of_interest_path)
    Turb_dfs = [(pd.read_csv(os.path.join(turbines_area_of_interest_path, file)), file) for file in turb_files]
    
    Layout_Path = [f"NoWake_Layout_{area}.csv" for area in areas]
    Layout_dfs = [pd.read_csv(file) for file in Layout_Path]
    
    for i, (turb_df, filename) in enumerate(Turb_dfs):
        layout_df = Layout_dfs[i]
        turb_df[['x', 'y']] = layout_df[['x', 'y']]
        Turb_dfs[i] = (turb_df, filename)
    
    return Turb_dfs

def create_states(data_2023):
    return foxes.input.states.Timeseries(
        data_source=data_2023,
        output_vars=[FV.WS, FV.WD, FV.TI, FV.RHO],
        var2col={FV.WS: "long-term_WS150", FV.WD: "long-term_WD150"},
        fixed_vars={FV.RHO: 1.225, FV.TI: 0.05},
    )

def compute_farm_results(geo_cluster_turb_df, states, parameters):
    result_all_farms = Foxes_Farm_Power(geo_cluster_turb_df, states, parameters)
    all_results_inter_wakes = result_all_farms[0]
    turb_results_inter_wakes = result_all_farms[1]
    return all_results_inter_wakes, turb_results_inter_wakes

def compute_farm_results_10(Turb_dfs, states, parameters):
    Farm_Results = []
    for Farm in Turb_dfs:
        Farm_Results.append(Foxes_Farm_Power(Farm, states, parameters))
    return Farm_Results

def analyze_farm_yield(data_2023, areas, wake_model="Bastankhah2014_linear"):
    geo_cluster_turb_df = load_layouts(areas)
    states = create_states(data_2023)
    
    parameters = {
        "TType": "IEA15MW",
        "rotor_model": "centre",
        "wake_models": [wake_model],
        "partial_wakes": None,
    }
    
    all_results, turb_results = compute_farm_results(geo_cluster_turb_df, states, parameters)
    
    #print(f'Summary Results: {all_results}')
    all_results.style.format(precision=1)
    
    all_results.to_csv(f'yield_N9-1-3_internal_wakes_{wake_model}.csv')
    
    return all_results, turb_results

def Foxes_Farm_Power(Farm_Name, States, Parameters):
    import matplotlib.pyplot as plt
    
    Farm = Farm_Name[0]
    Name = Farm_Name[1]
    
    # Create Wind Farm
    farm = foxes.WindFarm(name="my_farm")

    # Add Turbine
    foxes.input.farm_layout.add_from_df(farm, Farm, turbine_models=["kTI_02", Parameters['TType']], verbosity=0)

    # Plot with foxes
    ax = foxes.output.FarmLayoutOutput(farm).get_figure(figsize=(4, 4))
    plt.show()

    mbook = foxes.ModelBook()

    # Configure the Downwind algorithm
    algo = foxes.algorithms.Downwind(
        farm,
        states=States,
        rotor_model=Parameters['rotor_model'],
        wake_models=Parameters['wake_models'],
        partial_wakes=Parameters['partial_wakes'],
        chunks={FC.STATE: 100},
        verbosity=0,
    )

    # Calculate the results
    print(f"Calculating wind farm power for {Name} for Wake Model: {Parameters['wake_models']}:")
    with foxes.utils.runners.DaskRunner() as runner:
        farm_results = runner.run(algo.calc_farm)
        
    # Process Output
    o = foxes.output.FarmResultsEval(farm_results)
    o.add_efficiency()

    # Print Mean REWS + Mean efficiency
    fig, axs = plt.subplots(1, 2, figsize=(16, 19))
    layout_output = foxes.output.FarmLayoutOutput(farm, farm_results)
    layout_output.get_figure(fig=fig, ax=axs[0], color_by="mean_REWS", title="Mean REWS [m/s]", s=150, annotate=1)
    layout_output.get_figure(fig=fig, ax=axs[1], color_by="mean_EFF", title="Mean efficiency [%]", s=150, annotate=0)
    plt.show()
   

    P0 = o.calc_mean_farm_power(ambient=True)
    P = o.calc_mean_farm_power()
    
    # Create summary results
    data = {
        'Farm power [MW]': [P / 1000],  # MW
        'Farm ambient power [MW]': [P0 / 1000],  # MW
        'Farm efficiency [%]': [o.calc_farm_efficiency() * 100],  # %
        'Annual farm yield [TWh]': [o.calc_farm_yield(algo=algo) / 1000],  # TWh
    }
    
    Results = pd.DataFrame(data, index=[Name])
    turbine_df1 = o.reduce_states({FV.REWS: "mean", FV.P: "mean", FV.X:'mean', FV.Y: 'mean'})
    turbine_df2 = o.calc_turbine_yield(algo, annual=True)
    turbine_df = pd.concat([turbine_df1, turbine_df2], axis=1)

    return Results, turbine_df

def compare_yield_scenarios(all_results_inter_wakes, N9_farm_yield):
    total_farmyield_nowakes = pd.read_csv('total_farmyield_nowakes.csv')
    energy_yield_no_wakes = total_farmyield_nowakes.loc[0, 'Energy Yield no wakes']  # TWh

    all_results_inter_wakes_reset = all_results_inter_wakes.reset_index()
    energy_yield_int_wakes = all_results_inter_wakes_reset.loc[0, 'Annual farm yield [TWh]']
    energy_yield_ext_wakes = N9_farm_yield

    results = {
        'Energy yield no wakes': f'{energy_yield_no_wakes:.2f} TWh',
        'Energy yield internal wakes': f'{energy_yield_int_wakes:.2f} TWh',
        'Energy yield with external wakes': f'{energy_yield_ext_wakes:.2f} TWh',
        'Energy yield percentage, no wakes': '100 %',
        'Energy we lose due internal wakes': f'{(100-(100/energy_yield_no_wakes)*energy_yield_int_wakes):.0f} %',
        'Energy we lose due external + internal wakes': f'{100-((100/energy_yield_no_wakes)*energy_yield_ext_wakes):.0f} %'
    }

    # for key, value in results.items():
    #     print(f'{key}: {value}')

    return results

def analyze_farm_yield_with_external_effects(df_month_mean, areas):
    # Paths
    turbines_area_of_interest_path = 'data/turbine-info/coordinates/area_of_interest/'
    external_farms_path = 'data/turbine-info/coordinates/existing_planned/'

    # Read internal turbine layout files
    internal_files = os.listdir(turbines_area_of_interest_path)
    Turb_dfs = [pd.read_csv(os.path.join(turbines_area_of_interest_path, file)) for file in internal_files]
    Cluster_Turb_df = pd.concat(Turb_dfs, ignore_index=True)

    # Read external turbine layout files
    external_files = os.listdir(external_farms_path)
    external_dfs = [pd.read_csv(os.path.join(external_farms_path, file)) for file in external_files]
    external_combined_df = pd.concat(external_dfs, ignore_index=True)

    # Combine internal and external layouts for wake effect calculation
    combined_df = pd.concat([Cluster_Turb_df, external_combined_df], ignore_index=True)
    Combined_Turb_df = (combined_df, "Combined_Cluster")

    # Define States
    States = foxes.input.states.Timeseries(
        data_source=df_month_mean,
        output_vars=[FV.WS, FV.WD, FV.TI, FV.RHO],
        var2col={FV.WS: "long-term_WS150", FV.WD: "long-term_WD150", FV.TI: "time"},
        fixed_vars={FV.RHO: 1.225, FV.TI: 0.05},
    )

    # Define Parameters
    Parameters = {
        'TType': "IEA15MW",
        'rotor_model': "centre",
        'wake_models': ["Bastankhah2014_linear"],
        'partial_wakes': None,
    }

    # Calculate the farm results with wake effects
    combined_results = Foxes_Farm_Power(Combined_Turb_df, States, Parameters)
    
    # Extract the results for the farm of interest (Cluster_Turb_df)
    summary_results, turbine_results = combined_results
    matched_turbines = turbine_results.merge(Cluster_Turb_df, left_on=['X', 'Y'], right_on=['x', 'y'])
    matched_turbines.drop(['x', 'y'], axis=1, inplace=True)

    N9_farm_yield = (matched_turbines['YLD'].sum()) / 1000  # TWh 

    # Compare yield scenarios
    yield_comparison = compare_yield_scenarios(summary_results, N9_farm_yield)

    # Save results to CSV
    summary_results.to_csv('yield_N9-1-3_external_wakes.csv')
    matched_turbines.to_csv('yield_N9-1-3_external_wake_turb.csv')

    return combined_results, Cluster_Turb_df, yield_comparison

def load_internal_and_external_layouts(turbines_area_of_interest_path, external_farms_path):
    # Read internal turbine layout files
    internal_files = os.listdir(turbines_area_of_interest_path)
    Turb_dfs = [pd.read_csv(os.path.join(turbines_area_of_interest_path, file)) for file in internal_files]

    # Read external turbine layout files
    external_files = os.listdir(external_farms_path)
    external_dfs = [pd.read_csv(os.path.join(external_farms_path, file)) for file in external_files]
    external_combined_df = pd.concat(external_dfs, ignore_index=True)

    # Combine internal and external layouts for wake effect calculation
    Combined_Turb_dfs = []
    for i, Turb_df in enumerate(Turb_dfs):
        combined_df = pd.concat([Turb_df, external_combined_df], ignore_index=True)
        Combined_Turb_dfs.append((combined_df, f"Combined_Cluster{i+1}"))

    return Turb_dfs, Combined_Turb_dfs

def create_states_from_monthly_mean(df_month_mean):
    return foxes.input.states.Timeseries(
        data_source=df_month_mean,
        output_vars=[FV.WS, FV.WD, FV.TI, FV.RHO],
        var2col={FV.WS: "long-term_WS150", FV.WD: "long-term_WD150", FV.TI: "time"},
        fixed_vars={FV.RHO: 1.225, FV.TI: 0.05},
    )

def calculate_farm_results_with_wake_effects(Combined_Turb_dfs, States, Parameters):
    combined_results = []
    for Combined_Turb_df in Combined_Turb_dfs:
        result = Foxes_Farm_Power(Combined_Turb_df, States, Parameters)
        combined_results.append(result)
    return combined_results

def analyze_farm_yield_with_external_effects_v2(df_month_mean, turbines_area_of_interest_path, external_farms_path):
    Turb_dfs, Combined_Turb_dfs = load_internal_and_external_layouts(turbines_area_of_interest_path, external_farms_path)
    
    States = create_states_from_monthly_mean(df_month_mean)

    Parameters = {
        'TType': "IEA15MW",
        'rotor_model': "centre",
        'wake_models': ["Bastankhah2014_linear"],
        'partial_wakes': None,
    }

    combined_results = calculate_farm_results_with_wake_effects(Combined_Turb_dfs, States, Parameters)

    # Process results for each cluster
    cluster_results = []
    for i, (summary_results, turbine_results) in enumerate(combined_results):
        matched_turbines = turbine_results.merge(Turb_dfs[i], left_on=['X', 'Y'], right_on=['x', 'y'])
        matched_turbines = matched_turbines.drop(['x', 'y'], axis=1)
        
        N9_farm_yield = (matched_turbines['YLD'].sum()) / 1000  # TWh

        cluster_results.append({
            'Cluster': f'N9_{i+1}',
            'Summary': summary_results,
            'Turbines': matched_turbines,
            'Farm Yield': N9_farm_yield
        })

    return cluster_results