from DBtools import *
from ClassCreature import *
from BreedingPlanMaker import *


# Creates the databases and tables.
def create_database():
    try:
        create_table_dinos()
        print("Database created!")
    except:
        print("An error occurred while creating the database. Perhaps there's already one?")
    create_table_colors()
    create_table_species()


# Generates the breeding plan for certain species, color and sex.
def get_breeding_plan_color(species, target, sex):
    # Creates the dino pool
    p = generate_pool(species, target)

    if check_target_color_possible(species, target):
        # Finds the quickest route
        p_pos = find_path(p)

        k = get_best_dino(p_pos, sex)

        ped = []
        get_pedigree(k, ped)

        write(ped, target)
    else:
        print("Error! You don't have enough creatures")


# Gets all the colors for we can have a full color dino
def get_possible_colors(species):
    possible = []
    for i in range(227):
        current_target = Target([i, i, i, i, i, i], species)
        if check_target_color_possible(species, current_target):
            possible.append(i)
    print("You can breed a full color " + species + "s of the following colors: " + str(possible))


def require_main_menu():
    print("+--------------------------------------------------------------------------------------------------+")
    print("| ARK FROG COLOR BREEDING that definitely works for other species, but frogs are superior anyways. |")
    print("+--------------------------------------------------------------------------------------------------+")
    print("| 0 - Help                                                                                         |")
    print("| 1 - Create database                                                                              |")
    print("| 2 - Load more dinos                                                                              |")
    print("| 3 - Start breeding plan                                                                          |")
    print("| 4 - Quit                                                                                         |")
    print("+--------------------------------------------------------------------------------------------------+")

    menu_principal = str(input("What's your intention? "))

    while menu_principal != "1" and menu_principal != "2" and menu_principal != "3" and menu_principal != "4":
        menu_principal = str(input("Please insert a valid option: "))

    if menu_principal == "4":
        quit()
    else:
        return str(menu_principal)


def require_species():
    species_return = str(input("What species do you plan on breeding? "))
    return species_return


def require_sex():
    sex_return = str(input("What sex are you hoping to get (M/F)? "))
    return sex_return


def require_target(species):
    valid_regions = get_valid_regions(species)
    colors = ['?', '?', '?', '?', '?', '?']
    print("You can specify any color, or a ? in case you don't care about said region.")
    for i in range(6):
        if valid_regions[i]:
            colors[i] = str(input("Insert target color for region " + str(i) + ": "))
    return Target(colors, species)


## MAIN CODE

while (True):
    main_menu_option = require_main_menu()
    if main_menu_option == '1':
        create_database()
        load_inputs()

    elif main_menu_option == '2':
        load_inputs()

    elif main_menu_option == '3':
        species = require_species()
        target = require_target(species)
        sex = require_sex()
        print("+--------------------------------------------------------------------------------------------------+")
        print("Please wait while we calculate the best plan...")
        print("+--------------------------------------------------------------------------------------------------+")
        get_breeding_plan_color(species, target, sex)
        print("Plan saved to PDF!")
        print("+--------------------------------------------------------------------------------------------------+")
# target73 = Target([20, 863, 20, 20, 20, 20], 'Beelzebufo')

# get_breeding_plan_color('Beelzebufo', target73, 'M')
