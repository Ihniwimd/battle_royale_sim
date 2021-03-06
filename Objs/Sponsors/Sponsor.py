
from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.
from ..Contestants.Contestant import Contestant
import json
import random
from ..Sponsors.Traits import Traits

TRAIT_FILE_PATH = 'Objs\Sponsors\Traits.json'
with open(TRAIT_FILE_PATH) as TRAIT_FILE:
    RANDOM_TRAITS = json.load(TRAIT_FILE)["Traits"]

def contestantIndivActorWithSponsorsCallback(_, sponsor, baseEventSponsorWeight, event):
    try:
        addition = sponsor.eventAdditions[event.name]["sponsor"]
    except KeyError:
        addition = 0
    
    try:
        multiplier = sponsor.fullEventMultipliers[event.name]["sponsor"]
    except KeyError:
        multiplier = 1
    return (baseEventSponsorWeight*multiplier+addition, True)

class Sponsor(Contestant):  # sponsors are so similar to Contestants that it's easiest just to subclass. Really, though, they should both be inheriting from a more general parent class...
    
    traits = Traits()
    
    def __init__(self, name, inDict, settings):
        super().__init__(name, inDict, settings)
        self.primary_trait = inDict['trait']
        self.secondary_trait = random.choice(RANDOM_TRAITS)
        
    def initializeTraits(self, state):
        def startTrait(trait_name):
            if trait_name in self.traits.starting_effects:
                self.traits.starting_effects[trait_name](self, state)
        startTrait(self.primary_trait)
        startTrait(self.secondary_trait)
    
    # this is the main thing that needs overriding (mostly to be simpler)
    def InitializeEventModifiers(self, events): # Note that each event carries information about which stats affect them
        # This mixing of classes is regrettable but probably necessary
        self.events = events
        for eventName, event in self.events.items():
            #This is kind of a dumb way to do it, but being more general is a pain
            multiplierType = 'sponsor'
            self.eventAdditions[eventName][multiplierType] = 0
            if multiplierType+'Modifiers' in event.baseProps:
                self.statEventMultipliers[eventName][multiplierType] = 1
                for modifier, multiplier in event.baseProps[multiplierType+'Modifiers'].items():
                    self.statEventMultipliers[eventName][multiplierType] *= (1+self.settings['statInfluence'])**((self.stats[modifier]-5)*multiplier)
                self.fullEventMultipliers[eventName][multiplierType] = self.statEventMultipliers[eventName][multiplierType]
    
    def __str__(self):
        return self.name
    