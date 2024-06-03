import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import foxes
import foxes.variables as FV
import foxes.constants as FC

def Foxes_Farm_Power(Farm_Name,States,Parameters):
    Farm = Farm_Name[0]
    Name = Farm_Name[1]
    
    # Farm   : pd.datafram containing Layout of Turbines
    # States : Wind conditions
    # Parameters: dict
        # TType  : Typ of the Turbine  "NREL5MW" or "IEA15MW"
        # rotor_model   = "centre",
        # wake_models   = ["Bastankhah2014_linear"],
        # partial_wakes = None,
        
    # create Wind Farm
    farm = foxes.WindFarm(name="my_farm")

    #----------------------------------------------Add Turbine----------------------------------------------#
    #for testing
    #dataframes = read_csv("data/turbine-info/coordinates/area_of_interest/layout-N-9.3.geom.csv")
    foxes.input.farm_layout.add_from_df(farm, Farm,turbine_models=["kTI_02",Parameters['TType']])

    # plot  with foxes
    ax = foxes.output.FarmLayoutOutput(farm).get_figure(figsize=(4, 4))
    plt.show()
    #-------------------------------------------------------------------------------------------------------#

    mbook = foxes.ModelBook()
    #mbook.print_toc()       # lists all models

    ###-------------------------------configure the Downwind algorithm--------------------------------------###

    algo = foxes.algorithms.Downwind(
        farm,
        states=States,
        rotor_model=Parameters['rotor_model'],
        wake_models=Parameters['wake_models'],
        partial_wakes=Parameters['partial_wakes'],
        # chunks={FC.STATE: 100, FC.POINT: 4000},  # STATE: how many States should be considered
        chunks={FC.STATE: 100},  # STATE: how many States should be considered

        verbosity=0,
        )

    ###---------------------------------------calculate the results----------------------------------------###
    
    with foxes.utils.runners.DaskRunner() as runner:
        farm_results = runner.run(algo.calc_farm)     # calc_farm: Calculate farm data.
        
    ###----------------------------------------Process Output-----------------------------------------###
    o = foxes.output.FarmResultsEval(farm_results)
    o.add_efficiency()

    fig, axs = plt.subplots(2,1,figsize=(10, 14))
    o = foxes.output.FarmLayoutOutput(farm, farm_results)
    o.get_figure(fig=fig, ax=axs[0], color_by="mean_REWS", title="Mean REWS [m/s]", s=150, annotate=0)
    o.get_figure(fig=fig, ax=axs[1], color_by="mean_EFF", title="Mean efficiency [%]", s=150, annotate=0)
    plt.show()

    o = foxes.output.FarmResultsEval(farm_results)
    P0 = o.calc_mean_farm_power(ambient=True)
    P = o.calc_mean_farm_power()
    print(f"\nFarm power        : {P/1000:.1f} MW")
    print(f"Farm ambient power: {P0/1000:.1f} MW")
    print(f"Farm efficiency   : {o.calc_farm_efficiency()*100:.2f} %")
    print(f"Annual farm yield : {o.calc_farm_yield(algo=algo):.2f} GWh")
    
    ###-----------------------------------------return results--------------------------------------------------###
    data = {
        'Farm power [MW]'         : [P/1000],                    # MW
        'Farm ambient power [MW]' : [P0/1000],                      # MW
        'Farm efficiency [%]'     : [o.calc_farm_efficiency()*100],       # %
        'Annual farm yield [GWh]' : [o.calc_farm_yield(algo=algo)]    # Gwh
    }
    farm_results = pd.DataFrame(data,index=[Name[7:13]])   # layout-  N-9.3.  geom.csv
    
    return farm_results


