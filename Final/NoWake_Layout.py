# skript to create a geometric Layout (No Wake Effect), that can be optimized.
# May be not nesessary, but Layout optimazation seem to require initial pos. input
# Most Examples for Wake Effect Layouts seem to add Turbs manually, but it seems a bit anoying to do
import os
import numpy as np
import pandas as pd
# import netCDF4 as nc
import matplotlib.pyplot as plt
# import cartopy.crs as ccrs
import foxes
import foxes.variables as FV
import foxes.constants as FC
import foxes.opt.problems.layout.geom_layouts as grg# Purely geometrical layout problems (wake effects are not evaluated).
from iwopy.interfaces.pymoo import Optimizer_pymoo        # some optimization Package idk
# import geopandas as gpd

import foxes.opt.problems.layout.geom_layouts as grg      # Purely geometrical layout problems (wake effects are not evaluated).
# to include Wake effect look up: https://fraunhoferiwes.github.io/foxes.docs/api_opt_problems.html#foxes-opt-problems-layout

from iwopy.interfaces.pymoo import Optimizer_pymoo        # some optimization Package idk
# import geopandas as gpd



def NoWake_Layout(Place,Parameters):
    # No influenz from Wind conditions, just geometric Data

    # Farm layout turbine positioning problems. (No Wake)
    # GeomLayout        ##  A layout within a boundary geometry, purely defined by geometrical optimization (no wakes).
    # GeomRegGrid       ##  A regular grid within a boundary geometry.
    # GeomLayoutGridded ##  A layout within a boundary geometry, purely defined by geometrical optimization (no wakes), on a fixes background point grid.
    # GeomRegGrids      ##  A regular grid within a boundary geometry.
    
    # get area specific specs
    boundary = Place[0]
    name = Place[1]
    N    = Place[2]
    
    problem = grg.GeomRegGrid(
        boundary, 
        n_turbines=N,                                       # the number of turbines to be placed 
        min_dist=Parameters['min_dist']*Parameters['D'],    # the minimal distance between turbines
        # n_grids = 10                                      # number of Grids for GeomRegGrids
        # D=Parameters['D']                                 # this avoids that rotor blades can reach out of area
    )
    ###  https://fraunhoferiwes.github.io/foxes.docs/api_opt_problems_geom.html#foxes-opt-problems-layout-geom-layouts-objectives

    # only one objective
    problem.add_objective(grg.MaxDensity(problem, dfactor=2)) # objective function, which maximizes the grid spacing:
    #problem.add_objective(grg.MeMiMaDist(problem))           # Mean-min-max distance objective for purely geometrical layouts problems.

    # add a constraint that considers only valid layouts, for which exactly N points lie within the area. 
    problem.add_constraint(grg.Valid(problem))
    problem.add_constraint(grg.Boundary(problem))  # very importen, by my experience
    
    problem.initialize()
    problem.get_fig()     # plot the Problem (is kind of the boundary)
    plt.show()
    
    # define the Solver
    solver = Optimizer_pymoo(
        problem,
        problem_pars=dict(vectorize=True),
        algo_pars=dict(
            type="GA",                          # type of algorithm to use. "GA": generic algorithm
            pop_size = Parameters['pop_size'],  # the number of layouts per generation,  more Turbines require mor Layouts or we won't get a success
            seed     = Parameters['seed'],      # the random seed, for reproducible results
        ),
        setup_pars=dict(),
        term_pars=dict(
            n_gen=Parameters['n_gen'],          # number of 
            ftol=5e-2,     #1e-6 standard
            xtol=5e-2,     #1e-6
            ),  # the number of generations 
    )
    solver.initialize()
    solver.print_info()

    # Now let's run the optimization:
    results = solver.solve()
    solver.finalize(results)


    xy, valid = results.problem_results
    problem.get_fig(xy, valid, title=name)
    plt.show()

    #The list of turbine coordinates is now stored as a numpy array under `xy`:
    # print(xy)
    df = pd.DataFrame(xy, columns=['x','y'])
    # print(df)
    
    ###------------------------------------save csv ------------------------------#######
  
    File_Name = "NoWake_Layout_" + name + ".csv"
    df.to_csv(File_Name, header=True, index=False)