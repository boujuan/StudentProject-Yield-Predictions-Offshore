import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import foxes
import foxes.variables as FV
import foxes.constants as FC

def Foxes_Farm_Power(Farm_Name, States, Parameters):
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

    # Get data for plotting
    rews_data = layout_output.get_data(color_by="mean_REWS")
    eff_data = layout_output.get_data(color_by="mean_EFF")

    # Extract data into a DataFrame
    single_results = pd.DataFrame({
        'x': rews_data['x'],
        'y': rews_data['y'],
        'mean_REWS': rews_data['mean_REWS'],
        'mean_EFF': eff_data['mean_EFF']
    })
    
    single_results.to_csv('farm_layout_data.csv', index=False)

    P0 = o.calc_mean_farm_power(ambient=True)
    P = o.calc_mean_farm_power()
    
    # Create summary results
    data = {
        'Farm power [MW]': [P/1000],  # MW
        'Farm ambient power [MW]': [P0/1000],  # MW
        'Farm efficiency [%]': [o.calc_farm_efficiency() * 100],  # %
        'Annual farm yield [TWh]': [o.calc_farm_yield(algo=algo) / 1000]  # TWh
    }
    
    if Name[7:8] == "N":
        Results = pd.DataFrame(data, index=[Name[7:13]])  # "layout-  N-9.3.  geom.csv" only use middle as name 
    else:
        Results = pd.DataFrame(data, index=[Name])  
    
    # Merge single results with summary results
    single_results['Farm'] = Name  # Add a column to identify the farm in single results
    Results = Results.append(single_results, ignore_index=True)

    return Results

