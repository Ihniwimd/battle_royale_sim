# Hmm...the Rando Calrissian's are actually a problem, since I have been trying to avoid hard-coding
# stats here, but they need a list of stats to randomize...

# I'm going to make it so that the alternate initialized, used for Randos, needs to also take in a
# list of keys, which can be derived from any other instance in the main.

# stats should vary from 0-10. 5 is average and will not affect any events.

import random


class Contestant(object):

    def __init__(self, name, inDict, settings): # In this case, best to bake the stats as its own thing in the json...
        self.name = name
        self.imageFile = inDict['imageFile']
        self.stats = inDict['stats']
        self.inventory = []
        self.settings = settings
        self.contestantStatRandomize()
        self.originalStats = self.stats.copy() # NOT a reference, but an actual copy. Probably useful for some events.
        # Note that this is not a deepcopy.
        self.alive = True # Might be a useful flag, might not
        self.events = None
        self.statEventMultipliers = None # For efficiency, each contestant stores information about how their
        # event probabilities differ from the base. This cannot be fully initialized until the Events are known,
        # and I choose to defer it to its own step in main. statEventMultipliers are calculated off of base stats
        # The rest come from items and perhaps other sources.
        self.fullEventMultipliers = None
        self.eventAdditions = None
        self.eventDisabled = None # These events cannot happen to this contestant
        
    def contestantStatRandomize(self):
        for statName in self.stats: #this heavily depends on the type self.stats turns out to have... I need to look at what json supports
            self.stats[statName] = min(max(self.stats[statName]+
              random.randint(-1*self.settings['traitRandomness'],self.settings['traitRandomness']),0),10)
    
        
    def InitializeEventModifiers(self, events): # Note that each event carries information about which stats affect them
        # This mixing of classes is regrettable but probably necessary
        self.events = events
        self.statEventMultipliers = {}
        self.fullEventMultipliers = {}
        self.eventAdditions = {}
        self.eventDisabled = {} 
        for event in self.events:
            self.statEventMultipliers[event] = 1
            for modifier, multiplier in event.baseProps['mainModifiers']: #I really should look up how python json loading works...
                self.statEventMultipliers *= (1+self.settings['statInfluence'])**((self.stats['modifier']-5)*multiplier)
            self.fullEventMultipliers[event] = self.statEventMultipliers[event]
            self.eventAdditions[event] = 0
            self.eventDisabled[event] = event.baseProps['unique']
            if event.baseProps['unique']:
                if self.name in event.baseProps['uniqueUsers']:
                    self.eventDisabled[event] = False
    
    # Later on, items will be responsible for manipulating the contestant event modifiers, both on
    # addition to inventory and removal. In case of ambiguity (e.g. if an item that disables an event
    # is removed, but there might be two items that both disable that event), a full refresh is
    # performed. This allows flexibility for an item to perform arbitrary manipulations, if desired.
    
    # Note that for now there is only ever one instance of a given item. In the future if we want items with
    # changeable properties per contestant, we can add another class specifically to store that and have it include
    # a reference to the base object class.
    
    def addItem(self, item):
        self.inventory.append(item)
        item.onAcquisition(self)
        
    def removeItem(self, item):
        self.inventory.remove(item)
        item.onRemoval(self)
        
    def refreshEventState(self): #Called by item.onRemoval sometimes
        self.InitializeEventModifiers(self.events)
        for item in self.inventory:
            item.onAcquisition(self)
        