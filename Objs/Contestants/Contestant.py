"""stats should vary from 0-10. 5 is average and will not affect any events."""

from __future__ import division # In case of Python 2+. The Python 3 implementation is way less dumb.

import random
import collections

def contestantIndivActorCallback(actor, baseEventActorWeight, event):
    try:  # Pythonic, etc. Really, it's preferred this way...
        if actor.eventDisabled[event.name]["main"]:
            return (0, False)
    except KeyError:
        pass
    
    try:
        addition = actor.eventAdditions[event.name]["main"]
    except KeyError:
        addition = 0

    try:
        multiplier = actor.fullEventMultipliers[event.name]["main"]
    except KeyError:
        multiplier = 1
    # Base single event probability
    return (baseEventActorWeight*multiplier+addition, True)
    
def contestantIndivActorWithParticipantsCallback(_, participant, baseEventParticipantWeight, event):
    try:
        addition = participant.eventAdditions[event.name]["participant"]
    except KeyError:
        addition = 0
    
    try:
        multiplier = participant.fullEventMultipliers[event.name]["participant"]
    except KeyError:
        multiplier = 1
    return (baseEventParticipantWeight*multiplier+addition, True)

def contestantIndivActorWithVictimsCallback(_, victim, baseEventVictimWeight, event):
    try:
        addition = victim.eventAdditions[event.name]["victim"]
    except KeyError:
        addition = 0

    try:
        multiplier = victim.fullEventMultipliers[event.name]["victim"]
    except KeyError:
        multiplier = 1
    return (baseEventVictimWeight*multiplier+addition, True)                                                                           

class Contestant(object):

    def __init__(self, name, inDict, settings): # In this case, best to bake the stats as its own thing in the json...
        self.name = name
        self.gender = inDict['gender']
        self.imageFile = inDict['imageFile']
        self.stats = inDict['stats']
        self.inventory = []
        self.settings = settings
        if not self.settings["statNormalization"]:
            self.contestantStatRandomize()
        self.originalStats = self.stats.copy() # NOT a reference, but an actual copy. Probably useful for some events.
        # Note that this is not a deepcopy.
        self.alive = True
        self.events = None
        self.statEventMultipliers = collections.defaultdict(dict) # For efficiency, each contestant stores information about how their
        # event probabilities differ from the base. This cannot be fully initialized until the Events are known,
        # and I choose to defer it to its own step in main. statEventMultipliers are calculated off of base stats
        # The rest come from items and perhaps other sources.
        self.fullEventMultipliers = collections.defaultdict(dict) # Note that I _could_ pass in another default dict to give default values,
        # but this isn't actually a good idea (I actually want access attempts to the bottom layer to fail if unavailable). However, every
        # event should have its own dict in here regardless of anything else that is going on, so that's safe.
        self.eventAdditions = collections.defaultdict(dict)
        self.eventDisabled = collections.defaultdict(dict) # These events cannot happen to this contestant. Default False
        self.injured = False
        self.hypothermic = None # This is an integer indicating which turn it happened on. It's canceled at the end of the next turn unless set again.

    def __str__(self):
        return self.name
        
    def contestantStatRandomize(self):
        for statName in self.stats:
            self.stats[statName] = min(max(self.stats[statName]+
                                           random.randint(-1*self.settings['traitRandomness'], self.settings['traitRandomness']), 0), 10)
                                           
    def contestantStatFill(self, statsTemplate):  # Fills in missing stats based on a template
        for x in statsTemplate:
            if x not in self.stats:
                self.stats[x] = random.randint(0, 10)

    @classmethod
    def makeRandomContestant(cls, name, gender, imageFile, statstemplate, settings):
        inDict = {
            'imageFile': imageFile,
            'stats': {},
            'gender': gender,
            }
        for key in statstemplate:
            inDict['stats'][key] = random.randint(0, 10)
        return cls(name, inDict, settings)

    def contestantStatNormalizer(self, target):
        vari = random.uniform(1-self.settings["normalizationRange"], 1+self.settings["normalizationRange"])
        curSum = sum(self.stats.values())
        modifier = vari*target/curSum
        for i in self.stats:
            self.stats[i] = round(self.stats[i]*modifier)
        # Shuffle overflow stats (>10 or <0) to something else
        for key, value in self.stats.items():
            distribute = 0
            if value < 0:
                distribute = value
                self.stats[key] = 0
            elif value > 10:
                distribute = value - 10
                self.stats[key] = 10
            move = 1 if distribute > 0 else -1
            if move > 0:
                valid = lambda y: y < 10
            else:
                valid = lambda y: y > 0
            validList = [x for x, y in self.stats.items() if valid(y)]
            for _ in range(abs(distribute)):
                if not len(validList):
                    raise AssertionError('Stats reached limit in stat normalization!')
                chosen = random.choice(validList)
                self.stats[chosen] += move
                if not valid(self.stats[chosen]):
                    validList.remove(chosen)
        self.originalStats = self.stats.copy()
        
    def InitializeEventModifiers(self, events): # Note that each event carries information about which stats affect them
        # This mixing of classes is regrettable but probably necessary
        self.events = events
        for eventName, event in self.events.items():
            #This is kind of a dumb way to do it, but being more general is a pain
            for multiplierType in ['main', 'participant', 'victim']:
                self.eventAdditions[eventName][multiplierType] = 0
                if multiplierType+'Modifiers' in event.baseProps:
                    self.statEventMultipliers[eventName][multiplierType] = 1
                    for modifier, multiplier in event.baseProps[multiplierType+'Modifiers'].items():
                        self.statEventMultipliers[eventName][multiplierType] *= (1+self.settings['statInfluence'])**((self.stats[modifier]-5)*multiplier)
                    self.fullEventMultipliers[eventName][multiplierType] = self.statEventMultipliers[eventName][multiplierType]

            # NOTE: at the moment, the unique and itemrequired fields can only affect events for which the contestant is the main actor. This may need expansion in the future.
            self.eventDisabled[eventName] = {}
            self.eventDisabled[eventName]['main'] = event.baseProps['unique'] or event.baseProps['itemRequired']
            if event.baseProps['unique']:
                if self.name in event.baseProps['uniqueUsers']:
                    if event.baseProps['itemRequired']:
                        if event.baseProps['necessaryItem'] in [x.name for x in self.inventory]:
                            self.eventDisabled[eventName]['main'] = False
                    else:
                        self.eventDisabled[eventName]['main'] = False
            else:
                if event.baseProps['itemRequired']:
                    if event.baseProps['necessaryItem'] in [x.name for x in self.inventory]:
                        self.eventDisabled[eventName]['main'] = False
    
    def SetInjured(self):
        if self.injured:
            return
        self.permStatChange({'stability': -1,
                             'endurance': -2,
                             'combat ability': -2})
        self.injured = True
        
    def SetUninjured(self):
        if not self.injured:
            return
        self.permStatChange({'stability': 1,
                             'endurance': 2,
                             'combat ability': 2})
        self.injured = False
        
    def SetHypothermic(self, turnNumber):
        if not self.hypothermic:
            self.permStatChange({'stability': -1,
                             'endurance': -2})
        self.hypothermic = turnNumber
        
    def SetUnhypothermic(self):
        if not self.hypothermic:
            return
        self.permStatChange({'stability': 1,
                             'endurance': 2})
        self.hypothermic = None
        
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
        
    def permStatChange(self, dictOfChanges): # NOT to be called by items!
        """dictOfChanges is statName -> change"""
        for statName, change in dictOfChanges.items():
            self.originalStats[statName] += change
        self.refreshEventState()
        