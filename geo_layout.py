import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import foxes
import foxes.opt.problems.layout.geom_layouts as grg
from iwopy.interfaces.pymoo import Optimizer_pymoo

def set_boundary(site_shp, Areas, N):
    # Set Boundary
    # an list containing stuff for the the areas
    Area_specs = [
        (foxes.utils.geom2d.ClosedPolygon(np.array(site_shp[site_shp['name_fep']==Areas[i]].get_coordinates())),   # create boundary object (Foxes) for area
        Areas[i],
        N[i])    
        for i in range(len(Areas))
        ]
    return Area_specs

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
    problem.add_constraint(grg.Boundary(problem))  # very importent, by my experience
    
    problem.initialize()
    problem.get_fig()     # plot the Problem (is kind of the boundary)
    plt.show()
    
    # define the Solver
    print("new test3")
    solver = Optimizer_pymoo(
        problem,
        problem_pars=dict(vectorize=True),
        algo_pars=dict(
            type="GA",                          # type of algorithm to use. "GA": generic algorithm
            pop_size = Parameters['pop_size'],  # the number of layouts per generation,  more Turbines require mor Layouts or we won't get a success
            seed     = Parameters['seed'],      # the random seed, for reproducible results
        ),
        setup_pars=dict(),
        term_pars=(
            'n_gen', Parameters['n_gen'],          # number of
            #n_gen=2,          # number of 
 
            # ftol=5e-2,     #1e-6 standard
            # xtol=5e-2,     #1e-6
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
    
def plot_optimized_areas(Areas, site_shp, Layout_Path):
    Layout_dfs = [pd.read_csv(file) for file in Layout_Path]

    Visualizer = []
    for i in range(3):
        Visualizer.append(
            np.array(site_shp[site_shp['name_fep']==Areas[i]].get_coordinates())
        )

    colors = ['red', 'green', 'blue']
    fig, ax = plt.subplots(figsize=(12, 8))
    for df, color, area in zip(Layout_dfs, colors, Areas):
        ax.scatter(df['x'], df['y'], color=color, label=area)
    for i in range(3):
        ax.plot(Visualizer[i][:,0], Visualizer[i][:,1])
    
    ax.legend()
    ax.set_xlabel('X axis')
    ax.set_ylabel('Y axis')
    ax.set_title('Area of Interest')
    return fig, ax

def plot_all_optimized_areas(Areas, site_shp):
    Layout_Path = ["NoWake_Layout_" + area + ".csv" for area in Areas]
    plot_optimized_areas(Areas, site_shp, Layout_Path)