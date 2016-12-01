""" Hmm...the Rando Calrissian's are actually a problem, since I have been trying to avoid hard-coding
# stats here, but they need a list of stats to randomize...

# I'm going to make it so that the alternate initialized, used for Randos, needs to also take in a
# list of keys, which can be derived from any other instance in the main.

# stats should vary from 0-10. 5 is average and will not affect any events."""

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
                                           random.randint(-1*self.settings['traitRandomness'], self.settings['traitRandomness']), 0), 10)

    @classmethod
    def makeRandomContestant(cls, name, imageFile, statstemplate, settings):
        inDict = {
            'imageFile': imageFile,
            'stats': {}
            }
        for key in statstemplate:
            inDict['stats'][key] = random.randint(0, 10)
        return cls(name, inDict, settings)

    def InitializeEventModifiers(self, events): # Note that each event carries information about which stats affect them
        # This mixing of classes is regrettable but probably necessary
        self.events = events
        self.statEventMultipliers = {}
        self.fullEventMultipliers = {}
        self.eventAdditions = {}
        self.eventDisabled = {}
        for event in self.events:
            self.statEventMultipliers[event] = {}

            #This is kind of a dumb way to do it, but being more general is a pain
            for multiplierType in ['main', 'participant', 'victim']:
                if multiplierType+'Modifiers' in event.baseProps:
                    self.statEventMultipliers[event][multiplierType] = 1
                    for modifier, multiplier in event.baseProps[multiplierType+'Modifiers']: #I really should look up how python json loading works...
                        self.statEventMultipliers[event][multiplierType] *= (1+self.settings['statInfluence'])**((self.stats[modifier]-5)*multiplier)
                    self.fullEventMultipliers[event][multiplierType] = self.statEventMultipliers[event][multiplierType]

            self.eventAdditions[event] = 0
            self.eventDisabled[event] = event.baseProps['unique'] or event.baseProps['itemRequired']
            if event.baseProps['unique']:
                if self.name in event.baseProps['uniqueUsers']:
                    if event.baseProps['itemRequired']:
                        if event.baseProps['necessaryItem'] in [x.name for x in self.inventory]:
                            self.eventDisabled[event] = False
                    else:
                        self.eventDisabled[event] = False
            else:
                if event.baseProps['itemRequired']:
                    if event.baseProps['necessaryItem'] in [x.name for x in self.inventory]:
                        self.eventDisabled[event] = False

    # Later on, items will be responsible for manipulating the contestant event modifiers on
    # addition to inventory. This gives an item to perform arbitrary manipulations. For example, this could
    # be done by extending the item class for a particular item and making sure to include the new item class in the list.

    # Note that at the moment a full refresh of the contestant is done each time an item is added or removed. This
    # prevents items from having permanent effects after they are lost (outside of edge cases like directly manipulating
    # self.originalStats, etc. In the future, this could be done by adding a
    # persistent effects field, but this is left out for now. An item.onRemoval(self) is called on removal, but this will be
    # pass most of the time.

    # Note that for now there is only ever one instance of a given item. In the future if we want items with
    # changeable properties per contestant, we can add another class specifically to store that and have it include
    # a reference to the base object class.

    def addItem(self, item):
        if item in self.inventory: # at the moment no support is given for multiple copies of an item
            return False
        self.inventory.append(item)
        self.refreshEventState()
        return True

    def removeItem(self, item):
        if item not in self.inventory:
            return False
        self.inventory.remove(item)
        self.refreshEventState()
        item.onRemoval(self)
        return True

    def refreshEventState(self):
        self.stats = self.originalStats.copy()
        self.InitializeEventModifiers(self.events)
        for item in self.inventory:
            item.applyObjectStatChanges(self)
        for item in self.inventory:
            item.onAcquisition(self)
        