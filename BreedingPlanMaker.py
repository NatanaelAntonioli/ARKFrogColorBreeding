# This file has all we need to create the (not so fancy) breeding plan.

import sys
from PIL import Image, ImageDraw, ImageFont, ImageOps

from ClassCreature import Creature, Target
from DBtools import *


import warnings
warnings.filterwarnings("ignore")

def vector_sum(a, b):
    c = [0, 0]
    c[0] = a[0] + b[0]
    c[1] = a[1] + b[1]
    return c


def get_local_chance(c1: Creature, c2: Creature, target: Target):
    chance = 1

    for i in range(6):
        if c1.colors[i] == target.colors[i] and c2.colors[i] == target.colors[i]:
            chance = chance * 1
        elif c1.colors[i] == target.colors[i] or c2.colors[i] == target.colors[i]:
            chance = chance * 0.5
        #print(c1.colors[i] + "--" + c2.colors[i] + '---' + target.colors[i])
    return chance/2


def get_concat_v(im1, im2):
    dst = Image.new('RGB', (im1.width, im1.height + im2.height))
    dst.paste(im1, (0, 0))
    dst.paste(im2, (0, im1.height))
    return dst


def write(pedigree, target):
    line_production = []

    font = ImageFont.truetype("modelimages//cambriab.ttf", 38)
    color_text = (0, 0, 0)
    offset = [0, 0]

    first = Image.open("modelimages//top.png")
    draw2 = ImageDraw.Draw(first)


    draw2.text((725, 30), "Breeding plan", color_text, font=font)

    place_name = [21, 23]
    place_color= [15, 100, 180, 265, 330, 415]
    place_color_painting = [38, 122, 196, 264, 360, 426]

    j = 0

    for degree in pedigree:
        img1 = Image.open("modelimages//modelblank.png")
        img = img1.convert("RGB")
        draw = ImageDraw.Draw(img)
        i = 0
        j = j + 1
        for creature in degree:
            i = i + 1
            if i == 1:
                offset = [0, 0]
            if i == 2:
                offset = [590, 0]
            if i == 3:
                offset = [1190, 0]
                display_chance = get_local_chance(creature.mother, creature.father, target)
                display_chance = display_chance * 100
                draw.text((1200,225), "Chance: " + str(display_chance) + "%", color_text, font=font)

            draw.text(vector_sum(place_name, offset), creature.display_name(), color_text, font=font)
            for k in range(6):
                draw.text(vector_sum([place_color[k],100], offset), creature.colors[k], color_text, font=font)
                if creature.colors[k] != '?' and creature.colors[k] != '0':
                    color = (code_to_rgb(creature.colors[k]))
                    ImageDraw.floodfill(img, vector_sum([place_color_painting[k],180], offset), color, thresh=50)

        line_production.append(img)

    i = 0
    for step in line_production:
        i = i + 1
        if i == 1:
            out = get_concat_v(first, step)
        else:
            out = get_concat_v(out, step)

    img_with_border = ImageOps.expand(out, border=50, fill='white')
    img_with_border.save(str(target.displayName()).replace('?','') + ".pdf")
