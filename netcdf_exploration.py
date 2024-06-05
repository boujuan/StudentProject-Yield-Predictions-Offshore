def overview_ncfile(current_ncfile):
    for group_count, group_name in enumerate(current_ncfile.groups):
        group = current_ncfile.groups[group_name]
        print(f"TopGroup Nr. {group_count + 1}: {group_name}")
    print("---------------------------------------------------------")
    for group_name in current_ncfile.groups:
        group = current_ncfile.groups[group_name]
        print(f"TopGroup: {group_name}")
        for variable_group in group.variables:
            group_variable = group.variables[variable_group]
            print(f"    Groupvariable: {variable_group}")
        for subgroup_name in group.groups:
            subgroup = group.groups[subgroup_name]
            print(f"        Subgroup: {subgroup_name}")
            for variable_name in subgroup.variables:
                variable = subgroup.variables[variable_name]
                print(f"            SubGroupVariable: {variable_name}")
    print("---------------------------------------------------------")

def explore_topgroup_variables(current_ncfile, topgroup_name):
    for variable_name in current_ncfile.groups[topgroup_name].variables:
        variable = current_ncfile.groups[topgroup_name].variables[variable_name]
        print(f"Variable Name: {variable_name}")
        print(f"Variable Attributes:")
        print(f"    Units: {variable.units}")
        print(f"    Long Name: {variable.long_name}")
        print(f"    Shape: {variable.shape}")
        print("---------------------------------------------------------")

def explore_sub_groups(current_ncfile, top_group_name):
    top_group_name = current_ncfile.groups[top_group_name]
    for subgroup_name in top_group_name.groups:
        subgroup = top_group_name.groups[subgroup_name]
        print(f"SUBGROUP: {subgroup_name}")
        for variable_name in subgroup.variables:
            variable = subgroup.variables[variable_name]
            print(f"Variable Name: {variable_name}")
            print(f"Variable Attributes:")
            print(f"    Units: {variable.units}")
            print(f"    Long Name: {variable.long_name}")
            print(f"    Shape: {variable.shape}")
            print("---------------------------------------------------------")