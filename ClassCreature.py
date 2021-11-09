# This file has all the definitions that allows us to create and manipule creatures.

from DBtools import *
import names
import random
import string

# Adds random names to the creatures.
# Because differentiating between human names is easier than differentiating
# between numbers or random strings. Unless you are Elon Musk or Grimes.
generatenames = True


# This class is an object containing a vector with either a target color or a '?' for a region
# the creature does not have or that is not important for the breeder.
# Regions is a vector with int or str containing the target color value for each region.
# It returns the same vector passed to str and
class Target(object):
    def __init__(self, regions, species):
        self.species = str(species)
        self.colors = ['?', '?', '?', '?', '?', '?']
        has_region = get_valid_regions(species)
        for i in range(6):
            if has_region[i] == 1:
                self.colors[i] = str(regions[i])

    def displayName(self):
        colorsdisplay = ""
        for i in range(6):
            colorsdisplay = colorsdisplay + str(self.colors[i]) + "-"
        return self.species + "-" + colorsdisplay


# This class represents a creature that's currently in the breeder's pool.
# The id determines if it's a creature from the database, a generic creature or an offspring.
# The target is the color the breeder is looking for at the moment. Every creature has a target insied itself.
# Mother and father are only used in case of offspring.
# Every dino is a Creature object once it's in a pool.
class Creature(object):

    # Constructor.
    def __init__(self, id1, species, target: Target, mother='?', father='?'):

        # This is done for every creature.
        self.especie = species
        self.target = target
        # A custom uniqueID is generated.
        char_set = string.ascii_uppercase + string.digits
        self.unique_id = ''.join(random.sample(char_set * 10, 10))

        # By default, the creature is not an offspring. However,
        # it already receives the name of it's mother and father.
        self.offspring = 0
        self.mother = mother
        self.father = father

        # We assign generic ? colors to the creature.
        self.colors = ['?', '?', '?', '?', '?', '?']

        # In case we got our id1 from a list, we first prepare the result.

        id1 = str(id1)
        id1 = sanitize(id1)

        has_region = get_valid_regions(self.especie)

        # 1) Here, we got  a generic creature, that anyone can tame anytime.

        if id1 == 'AnyF' or id1 == 'AnyM':  # Creates the generic animal with any colors.
            # This is done for both sexes.

            self.chance = 1
            self.level = '?'
            self.neutered = '0'
            self.id1 = id1
            self.id2 = id1
            self.tamedName = "Any "

            if id1 == 'AnyF':  # Decides the sex.
                self.female = '1'
            else:
                self.female = '0'

        #   2)  Here, we got the order to produce an offspring of said sex

        elif id1 == 'offspringF' or id1 == 'offspringM':  # Case of offspring

            self.chance = mother.chance * father.chance
            self.offspring = 1
            self.level = '?'
            self.neutered = '0'
            self.id1 = id1
            self.id2 = id1

            # Calculate colors

            for i in range(6):
                if father.colors[i] == self.target.colors[i] and mother.colors[i] == self.target.colors[i]:
                    self.colors[i] = self.target.colors[i]
                    self.chance = self.chance * 1
                elif father.colors[i] == self.target.colors[i] or mother.colors[i] == self.target.colors[i]:
                    self.colors[i] = self.target.colors[i]
                    self.chance = self.chance * 0.5
                elif father.colors[i] == mother.colors[i]:
                    self.colors[i] = father.colors[i]
                else:
                    self.colors[i] = '?'

            # Set name and sex

            if id1 == 'offspringF':
                if generatenames:
                    self.tamedName = names.get_first_name(gender='female')
                else:
                    self.tamedName = ''
                self.female = '1'
            else:
                if generatenames:
                    self.tamedName = names.get_first_name(gender='male')
                else:
                    self.tamedName = ''
                self.female = '0'

        #   3) It's a real creature.

        else:  # Fill the real creature's attributes.
            self.chance = 1
            self.especie = get_attribute('especie', str(id1))

            self.level = get_attribute('level', str(id1))
            self.female = get_attribute('female', str(id1))
            self.neutered = get_attribute('neutered', str(id1))
            self.id1 = id1
            self.id2 = get_attribute('id2', str(id1))
            self.tamedName = get_attribute('tamedName', str(id1))

            for i in range(6):
                if has_region[i]:
                    self.colors[i] = get_attribute('color' + str(i), str(id1))
                else:
                    self.colors[i] = '?'

            '''
            self.colors[0] = get_attribute('color0', str(id1))
            self.colors[1] = get_attribute('color1', str(id1))
            self.colors[2] = get_attribute('color2', str(id1))
            self.colors[3] = get_attribute('color3', str(id1))
            self.colors[4] = get_attribute('color4', str(id1))
            self.colors[5] = get_attribute('color5', str(id1))
            '''

            self.father = '?'
            self.mother = '?'

        # Now we are back at the stuff we do for every creature.
        # Values pertaining the fitness of a creature. We have to compare each
        # color with the target's color.

        self.max_fitness = 0
        self.fitness = 0

        for i in range(6):
            if has_region[i]:
                self.max_fitness = self.max_fitness + 1

        for i in range(6):
            if has_region[i]:
                if self.colors[i] == target.colors[i]:
                    self.fitness = self.fitness + 1

    # Returns the display name of the creature.
    def display_name(self):
        if self.female == '1':
            displaySex = 'F'
        else:
            displaySex = 'M'
        if self.tamedName != '':
            return str(self.tamedName) + " (" + str(self.level) + "-" + str(displaySex) + ")"
        else:
            return str(self.especie) + " (" + str(self.level) + "-" + str(displaySex) + ")"

    # Prints a summary of the creature
    def print_sum(self):
        print("     " + self.display_name() + "     ")
        print(
            self.colors[0] + "-" + self.colors[1] + "-" + self.colors[2] + "-" + self.colors[3] + "-" + self.colors[
                4] + "-" + self.colors[5])
        print("Fitness = " + str(self.fitness) + "/" + str(self.max_fitness))
        print("Chance = " + str(self.chance))
        if self.offspring == 1:
            print("Ancestry = " + str(self.father.display_name()) + " + " + str(self.mother.display_name()))
            print("Female = " + str(self.female))
        print("----------------------------------")


# Now we have some functions that are useful to manipule Creatures.

# Checks if we have enough dinos to obtain a creature with said color target.
# We have if we have at least one dino with said target color on said region.
# Otherwise, we'd have to count on mutations, or tame/buy more dinos.
def check_target_color_possible(especie, target: Target):
    totals = [0, 0, 0, 0, 0, 0]
    possible = 1
    list_creatures = []

    list_creatures = list_all_by_color(especie, target)

    for k in list_creatures:

        # Checks how many creatures with said color on said region we have

        c = Creature(k, especie, target)
        for i in range(6):
            if c.colors[i] == target.colors[i] or target.colors[i] == '?':
                totals[i] = totals[i] + 1

    # Checks what regions said creature uses

    has_region = get_valid_regions(especie)

    for i in range(6):
        if has_region[i]:
            possible = possible * totals[i]
    if possible > 0:
        return True
    else:
        return False


# Creates the typical pool a breeder starts. It has every dino with said color,
# plus a male and female dino with generic colors.
# Returns the pool.
# Color in here means target object. The list_all_by_color function receives the target object
# and returns the pool with  each dino that has the color in the target regions.
def generate_pool(species, color):
    creature_pool = []
    nominal_pool = list_all_by_color(species, color)  # Returns a list of IDs.

    nominal_pool.append('AnyF')
    nominal_pool.append('AnyM')

    for k in nominal_pool:
        # print("Adding... " + str(k))
        c1 = Creature(k, species, color)
        creature_pool.append(c1)  # Returns the pool of creatures.

    return creature_pool


# Returns False if:
# - Both are of the same sex.
# - One of then is neutered.
# This function checks if we can breed two creatures.
def breed_possible(c1: Creature, c2: Creature):
    if int(c1.female) == int(c2.female) or str(c1.neutered) == '1' or str(c2.neutered) == '1':
        return False
    else:
        return True


# Breeds the best combination for two creatures considering an specific color.
# For every pair, it returns the combination that's closer to the target.
# The chance of getting said result is added in the chance attribute of the creature.
# Returns a creature.
def breed(c1: Creature, c2: Creature, sex):
    if not breed_possible(c1, c2):
        print("Warning! Breeding two creatures of the same sex or one neutered creature. This should not happen.")
    # But We are breeding it anyway.
    offspring = Creature(sex, c1.especie, c1.target, c1, c2)

    return offspring


# Returns the pool with creatures of the desired color, and all the dinos generated in between.
# That's no answer, that's just a big pool of trials. We still have to extract the best route to get the
# dino with the desired color.
# The next step is finding the easiest creature with maximum fitness among all this creatures.
def find_path(pool):
    timestop = False
    best_chance = 0
    gen = []

    for current_creature in pool:
        for current_pair in pool:
            if current_creature != current_pair and breed_possible(current_creature, current_pair):
                offF = breed(current_creature, current_pair, 'offspringF')
                offM = breed(current_creature, current_pair, 'offspringM')
                # print("Breeding: " + current_creature.displayName + "with" + current_pair.displayName + "With fitness: " +
                # str(offF.fitness) + "/" + str(offF.max_fitness) + "producing " + str(offM.displayName))
                # print("Breeding: " + current_creature.displayName + "with" + current_pair.displayName + "With fitness: " +
                #      str(offF.fitness) + "/" + str(offF.max_fitness) + "producing " + str(offF.displayName))

                gen.append(offM)
                gen.append(offF)

                if offM.fitness == offM.max_fitness:
                    timestop = True

        pool.remove(current_creature)

        for new_off in gen:
            pool.append(new_off)
            gen = []

        if timestop:
            return pool


# Returns the dino with maximum fitness and biggest chance in the pool.
# This finds our objective.
# The next step is finding how we reached this objective.
def get_best_dino(pool, sex):
    biggest_chance = 0
    if sex == 'F':
        sexNum = '1'
    else:
        sexNum = '0'

    for b in pool:
        if b.fitness == b.max_fitness and b.female == sexNum:
            if b.chance > biggest_chance:
                biggest_chance = b.chance
                best_dino = b
    return best_dino


# This shows how we reached the objective.
# It returns a matrix in the following organization, for each creature involved in
# generating the objective.
# [Mother, Father, Creature]
# [Mother, Father, Creature]
# [Mother, Father, Creature]
def get_pedigree(c1: Creature, pedigree):
    name_mother = 0
    name_father = 0
    if c1.mother != '?':
        name_mother = c1.mother.display_name()
        get_pedigree(c1.mother, pedigree)

    if c1.father != '?':
        name_father = c1.father.display_name()
        get_pedigree(c1.father, pedigree)

    if not (name_father == 0 and name_mother == 0):
        print("Breed " + str(name_mother) + " with " + str(name_father) + " to get " + str(c1.display_name()))
        # c1.print_sum()
        pedigree.append([c1.mother, c1.father, c1])


# I don't know why this function exists.
# I don't even know what I was thinking when I made this.
# Like why the fuck would I need to create a creature that is it's own father and mother.
# Oh now I remember. It was for testing when I didn't have enough creatures.
# Leaving it here anyways.
def make_tuple(c1: Creature, pedigree):
    pedigree.append([c1, c1, c1])
