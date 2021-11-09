# This file has all we need to deal with the database.

import sqlite3 as sl
import os
import configparser
import io
import csv

from PIL import ImageColor

config = configparser.ConfigParser()
config.sections()

DIR_dino = r'dinos'  # Folder for default .ini files. Perhaps can be changed to ARK's default directory.
DIR_dino_ansi = r'dinosANSI'  # Default folder for .ini files converted as ANSI.
update = False # If enabled, the value of each .ini file will be loaded and updated to the database.


# Removes undesirable characters from elements.
# Returns the element.
def sanitize(valor):
    valor = str(valor)
    valor = valor.replace('(', '')
    valor = valor.replace(')', '')
    valor = valor.replace(',', '')
    valor = valor.replace("'", '')
    return valor


# Returns a vector with 1 for valid creatures regions and 0 for regions that aren't used.
# Name is name of the species.
def get_valid_regions(name):
    con = sl.connect("my-dinos.db")
    cur = con.cursor()
    vetor = [0, 0, 0, 0, 0, 0]

    cur.execute("SELECT region0 FROM species WHERE name = ?", (name,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    vetor[0] = int(SEARCH)

    cur.execute("SELECT region1 FROM species WHERE name = ?", (name,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    vetor[1] = int(SEARCH)

    cur.execute("SELECT region2 FROM species WHERE name = ?", (name,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    vetor[2] = int(SEARCH)

    cur.execute("SELECT region3 FROM species WHERE name = ?", (name,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    vetor[3] = int(SEARCH)

    cur.execute("SELECT region4 FROM species WHERE name = ?", (name,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    vetor[4] = int(SEARCH)

    cur.execute("SELECT region5 FROM species WHERE name = ?", (name,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    vetor[5] = int(SEARCH)

    con.close()
    return vetor


# Creates the table with every DINO, name and regions.
# There's a .csv file that can be used to modify this table.
# Used regions are filled when dinos are added.
# I did this for two reasons: I'm lazy and the program
# updates automatically if Wildcard decides to enable more regions.
def create_table_species():
    conn = sl.connect('my-dinos.db')
    curs = conn.cursor()
    curs.execute('''DROP TABLE IF EXISTS species''')
    curs.execute('''CREATE TABLE species (name TEXT, breedable INT, species_id TEXT, region0 INT, region1 INT, 
    region2 INT, region3 INT, region4 INT, region5 INT, mapknown INT)''')

    cur = conn.cursor()

    # csv.DictReader uses first line in file for column headings by default
    with open('species-list.csv', 'rt') as fin:
        reader = csv.reader(fin)  # Update!!
        to_db = [tuple(line) for line in reader]
    cur.executemany(
        '''INSERT INTO species (name, breedable, species_id, mapknown) VALUES (?, ?, ?,0)''', to_db)
    conn.commit()
    conn.close()


# Creates the table with every color ID, name and hexcode.
# There's a .csv file that can be used to modify this table.
def create_table_colors():
    conn = sl.connect('my-dinos.db')
    curs = conn.cursor()
    curs.execute('''DROP TABLE IF EXISTS colors''')
    curs.execute('''CREATE TABLE colors(codigo INT, hexcode TEXT, name TEXT)''')

    cur = conn.cursor()

    # csv.DictReader uses first line in file for column headings by default
    with open('colors-ids.csv', 'rt') as fin:
        reader = csv.reader(fin)  # Update!!
        to_db = [tuple(line) for line in reader]

    cur.executemany(
        '''INSERT INTO colors (codigo, hexcode, name) VALUES (?, ?, ?)''', to_db)
    conn.commit()
    conn.close()


# This function is used to initialize the empty database and the main table.
# Since this table's contents aren't easily recoverable, this function raises an error if the
# database already exists. Dropping it anyways isn't a good idea.
def create_table_dinos():
    con = sl.connect('my-dinos.db')

    with con:
        con.execute("""
            CREATE TABLE dinos (
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,

                especie TEXT,
                tamedName TEXT,
                female INTEGER,
                neutered INTEGER,
                level INTEGER,
                id1 INTEGER,
                id2 INTEGER,

                color0 INTEGER,
                color1 INTEGER,
                color2 INTEGER,
                color3 INTEGER,
                color4 INTEGER,
                color5 INTEGER,

                hp REAL,
                stamina REAL,
                oxygen REAL,
                torpor REAL,
                food REAL,
                weight REAL,
                damage REAL,
                speed REAL,

                mutMale INTEGER,
                mutFemale INTEGER
            );
        """)


# Converts Unreal's weird decimal notation to RGB.
# The function is called for each of the values bellow.
# ColorSet[0]=(R=0.005000,G=0.005000,B=0.005000,A=0.000000)
def decimal_to_rgb(decimal_value):
    v = 255.999 * pow(decimal_value, 1 / 2.2)
    if v > 255:
        return 255
    if v < 0:
        return 0
    return int(v)


# Converts and RGB value to HEX. Returns the hexcode.
def rgba_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


# Converts an ARK code to RGB. Returns the vector.
def code_to_rgb(code):
    con = sl.connect("my-dinos.db")
    cur = con.cursor()
    rows = cur.execute("SELECT hexcode FROM colors WHERE codigo = ?", (code,)).fetchall()
    valor_cor = str(rows[0]).replace('(', '')
    valor_cor = valor_cor.replace(')', '')
    valor_cor = valor_cor.replace(',', '')
    valor_cor = valor_cor.replace("'", '')
    # print("Recebi: " + code + "e a cor é: " + valor_cor)
    # valor_cor = valor_cor.replace('#', '')
    return (ImageColor.getcolor(valor_cor, "RGB"))


# Converts a color string found in the .ini files to ARK color code
# This function takes values like bellow:
# ColorSet[0]=(R=0.005000,G=0.005000,B=0.005000,A=0.000000)
def string_to_code(color_string):
    con = sl.connect("my-dinos.db")
    cur = con.cursor()

    color_string = color_string.replace('(', '')
    color_string = color_string.replace(')', '')
    color_string = color_string.replace('R=', '')
    color_string = color_string.replace('G=', '')
    color_string = color_string.replace('B=', '')
    color_string = color_string.replace('A=', '')

    r_dec = float(color_string.split(',')[0])
    g_dec = float(color_string.split(',')[1])
    b_dec = float(color_string.split(',')[2])
    a_dec = float(color_string.split(',')[3])

    r = decimal_to_rgb(r_dec)
    g = decimal_to_rgb(g_dec)
    b = decimal_to_rgb(b_dec)

    color_hex = rgba_to_hex(r, g, b)

    if a_dec == 1:  # If alpha = 1, then the color region is not used. We return 0 in this case.
        return 0

    if r_dec == g_dec and g_dec == b_dec and b_dec == 1.75:  # DinoAlbino doesn't have an RGB representation, so we
        # treat this case apart.
        # I bet they could have used some RGB color and have the same results, but that's ARK.
        return 36

    else:  # Any other color belongs in this section.
        rows = cur.execute("SELECT codigo FROM colors WHERE hexcode = ?", (color_hex,)).fetchall()
        valor_cor = str(rows[0]).replace('(', '')
        valor_cor = valor_cor.replace(')', '')
        valor_cor = valor_cor.replace(',', '')
        return int(valor_cor)


# Adds any new dinosaurs in the dinos folder (as .ini files) to the database.
# The update variable has direct impact in this function.
def load_inputs():
    con = sl.connect("my-dinos.db")
    cur = con.cursor()

    for CURRENT_dino in os.listdir(DIR_dino):

        # First, it converts the encoding to ANSI, so it can be manipulated by the configparser.

        # read input file
        with io.open(os.path.join(DIR_dino, CURRENT_dino), 'r', encoding='utf_16') as file:
            lines = file.read()
        # write output file
        with io.open(os.path.join(DIR_dino_ansi, CURRENT_dino), 'w', encoding='ansi') as file:
            file.write(lines)

        # Loads data into variables

        config.read(os.path.join(DIR_dino_ansi, CURRENT_dino))

        # Loads Dino Data

        id_especie = config['Dino Data']['DinoClass']
        id_especie = str(id_especie).rpartition('.')[-1]
        especie = get_species_from_id(id_especie)

        tamedname = config['Dino Data']['TamedName']

        if config['Dino Data']['bIsFemale'] == 'False':
            female = 0
        else:
            female = 1

        if config['Dino Data']['bNeutered'] == 'False':
            neutered = 0
        else:
            neutered = 1

        level = int(config['Dino Data']['CharacterLevel'])

        id1 = config['Dino Data']['DinoID1']
        id2 = config['Dino Data']['DinoID2']

        # Loads Color info

        colorset0 = config['Colorization']['ColorSet[0]']
        colorset1 = config['Colorization']['ColorSet[1]']
        colorset2 = config['Colorization']['ColorSet[2]']
        colorset3 = config['Colorization']['ColorSet[3]']
        colorset4 = config['Colorization']['ColorSet[4]']
        colorset5 = config['Colorization']['ColorSet[5]']

        color0 = string_to_code(colorset0)
        color1 = string_to_code(colorset1)
        color2 = string_to_code(colorset2)
        color3 = string_to_code(colorset3)
        color4 = string_to_code(colorset4)
        color5 = string_to_code(colorset5)

        # Fill color region information

        cur.execute("SELECT mapknown FROM species WHERE species_id = ?", (id_especie,))
        SEARCH_color_known = cur.fetchall()
        SEARCH_color_known = sanitize(SEARCH_color_known[0])

        if SEARCH_color_known == '0':

            if str(color0) == '0':
                cur.execute('''UPDATE species SET region0 = 0 WHERE species_id = ? ''', (id_especie,))
            else:
                cur.execute('''UPDATE species SET region0 = 1 WHERE species_id = ? ''', (id_especie,))

            if str(color1) == '0':
                cur.execute('''UPDATE species SET region1 = 0 WHERE species_id = ? ''', (id_especie,))
            else:
                cur.execute('''UPDATE species SET region1 = 1 WHERE species_id = ? ''', (id_especie,))

            if str(color2) == '0':
                cur.execute('''UPDATE species SET region2 = 0 WHERE species_id = ? ''', (id_especie,))
            else:
                cur.execute('''UPDATE species SET region2 = 1 WHERE species_id = ? ''', (id_especie,))

            if str(color3) == '0':
                cur.execute('''UPDATE species SET region3 = 0 WHERE species_id = ? ''', (id_especie,))
            else:
                cur.execute('''UPDATE species SET region3 = 1 WHERE species_id = ? ''', (id_especie,))

            if str(color4) == '0':
                cur.execute('''UPDATE species SET region4 = 0 WHERE species_id = ? ''', (id_especie,))
            else:
                cur.execute('''UPDATE species SET region4 = 1 WHERE species_id = ? ''', (id_especie,))

            if str(color5) == '0':
                cur.execute('''UPDATE species SET region5 = 0 WHERE species_id = ? ''', (id_especie,))
            else:
                cur.execute('''UPDATE species SET region5 = 1 WHERE species_id = ? ''', (id_especie,))

            cur.execute('''UPDATE species SET mapknown = 1 WHERE species_id = ? ''', (id_especie,))

        cur.execute("SELECT id1 FROM dinos WHERE id1 = ?", (id1,))
        SEARCH_id1 = cur.fetchall()
        cur.execute("SELECT id2 FROM dinos WHERE id2 = ?", (id2,))
        SEARCH_id2 = cur.fetchall()

        if len(SEARCH_id1) == 0 and len(SEARCH_id2) == 0:  # If the dino is not on the database, add it
            cur.execute('''INSERT INTO dinos (especie, tamedName, female, neutered, level, id1, id2, color0, color1, 
            color2, color3, color4, color5) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
                especie, tamedname, female, neutered, level, id1, id2, color0, color1, color2, color3, color4, color5))
        else:
            if update:
                cur.execute('''UPDATE dinos SET especie = ?, tamedName = ?, female =? , neutered=?, level=?, id1=?, 
                id2=?, color0=?, color1=?, color2=?, color3=?, color4=?, color5=? WHERE id1 =? ''', (
                    especie, tamedname, female, neutered, level, id1, id2, color0, color1, color2, color3, color4,
                    color5, id1))

        con.commit()
    con.close()


# Returns a vector of id1s of creatures of said species that has said color.
# Color is a target object. It paris dino regions with target regions in the SQL query.
def list_all_by_color(especie, color):
    con = sl.connect("my-dinos.db")
    cur = con.cursor()
    cur.execute("SELECT id1 FROM dinos WHERE (color0 = ? OR color1 = ? OR color2 = ? OR color3 = ? OR color4 = ? OR "
                "color5 = ?) AND especie = ?", (
                    color.colors[0], color.colors[1], color.colors[2], color.colors[3], color.colors[4],
                    color.colors[5],
                    especie))
    SEARCH_color = cur.fetchall()
    con.close()
    return SEARCH_color

# Giving a species like 'Mantis', it returns the ID, like 'Mantis_Character_BP_C'
def get_id_from_species(name):
    con = sl.connect("my-dinos.db")
    cur = con.cursor()
    cur.execute("SELECT species_id FROM species WHERE name = ?", (name,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    con.close()
    return SEARCH

# Giving an ID like 'Mantis_Character_BP_C', it returns the species, like 'Mantis'
def get_species_from_id(id):
    con = sl.connect("my-dinos.db")
    cur = con.cursor()
    cur.execute("SELECT name FROM species WHERE species_id = ?", (id,))
    SEARCH = cur.fetchall()[0]
    SEARCH = sanitize(SEARCH)
    con.close()
    return SEARCH

# Returns said attribute from the dino that has said id1.
# Usually returns it as string.
def get_attribute(attribute, id1):
    con = sl.connect("my-dinos.db")
    cur = con.cursor()

    if attribute == 'especie':
        cur.execute("SELECT especie FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'tamedName':
        cur.execute("SELECT tamedName FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'female':
        cur.execute("SELECT female FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'neutered':
        cur.execute("SELECT neutered FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'level':
        cur.execute("SELECT level FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'id1':
        cur.execute("SELECT id1 FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'id2':
        cur.execute("SELECT id2 FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'color0':
        cur.execute("SELECT color0 FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'color1':
        cur.execute("SELECT color1 FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'color2':
        cur.execute("SELECT color2 FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'color3':
        cur.execute("SELECT color3 FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'color4':
        cur.execute("SELECT color4 FROM dinos WHERE id1 = ?", (id1,))

    elif attribute == 'color5':
        cur.execute("SELECT color5 FROM dinos WHERE id1 = ?", (id1,))

    SEARCH = cur.fetchall()
    con.close()

    treated = str(SEARCH[0]).replace('(', '')
    treated = treated.replace(')', '')
    treated = treated.replace(',', '')
    treated = treated.replace("'", '')
    return treated
