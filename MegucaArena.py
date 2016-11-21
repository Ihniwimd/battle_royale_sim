import json
import os
import random #A not very good random library, but probably fine for our purposes

from Contestants.Contestant import Contestant
from Events.Event import Event
from Items.Item import Item
from Sponsors.Sponsor import Sponsor
from World.World import World
import ArenaUtils

# Initial Setup:

# Import Settings from JSON -> going to make it a dictionary
with open('Settings.json') as settings_file:
    settings = json.load(settings_file)

# List of settings as I come up with them. It can stay as a dict.
# traitRandomness = 3
# numContestants = 24 # Program should pad or randomly remove contestants as necessary
# sponsorProbability = pass #This is the weight that the "sponsor gives resources" event has relative to other events\
# Note that this is independent of the number of sponsors, in defiance of logic (but makes for clearer design). Once the
# event is chosen, a sponsor is chosen randomly.


# Initialize Arena State

# Import and initialize contestants -> going to make it dictionary name : (imageName, baseStats...)
contestants = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Contestants', 'Contestant.json'),settings,Contestant)
# If number of contestants in settings less than those found in the json, randomly remove some
contestantNames = constestantsFromFile.keys()
if settings['numContestants'] < len(contestantNames):
    contestantNames = random.sample(contestantNames, len(contestantNames)-settings['numContestants'])
    for remove in contestantNames:
        del contestants[remove]
# If number of contestants in settings more than those found in the json, add Rando Calrissians
for i in range(len(contestantNames),settings['numContestants']):
    constestants['Rando Calrissian ' + i] =  Constestant('Rando Calrissian ' + i, pass, settings) # Constructor should \
     # also take in string, image, settings and make full random stats (need Rando image to put here)

# Import and initialize sponsors -> going to make it dictionary name : (imageName,baseStats...)
# baseStats =  weight (probability relative to other sponsors, default 1), objectPrefs (any biases towards or away any \
# from any type of object gift, otherwise 1, Anything else we think of)
# No placeholder sponsors because of the way it is handled.
sponsors = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Sponsors', 'Sponsor.json'),settings,Sponsor)

# Import and initialize Items -> going to make it dictionary name : (imageName,baseStats...)
items = ArenaUtils.LoadJSONIntoDictOfObjects(os.path.join('Items', 'Item.json'),settings,Item)

#Initialize World - Maybe it should have its own settings?
arena = World(settings) #Maybe other arguments in future, i.e. maybe in an extended world items can be found on the ground, but leaving this as-is for now.

