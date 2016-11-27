# Unlike the other main classes, the Event object is mostly not directly used, since events can have arbitrary effects.
# Instead, Event serves as the parent class for all other types of events, providing most of the structure but leaving
# the key method(s) for those event subtypes to determine. On its own, Event serves a default "does nothing" event.

# Yes, I know the trend nowadays is composition >> inheritance but _in this case_ it's extremely logical inheritance,
# and we'll probably never need to replace the parent class of any event. (Murphy's law: yes we will)

# Note that it is very likely feasible to define some helper methods (like kill_player) here that events can call for common
# shared events.

import random

class Event(object): #Python 2.x compatibility
    
    def __init__(self, name, inDict, settings):
        self.baseProps = inDict # Hey, it's the most straightforward way and basically achieves the purpose
        # Could also use setattr, but...
        # Should be: float mainWeight, float optional participantWeight, float optional victimWeight,
        # int numParticipants, int numVictims, list[(string,float)] mainModifiers,
        # list[(string,float)] optional participantModifiers, list[(string,float)] optional victimModifiers,
        # bool unique, list[string] optional uniqueUsers
        # bool itemRequired, string optional requiredItem
        
        # mainWeight = sets relative probability of rolling event for given character, participantWeight
        # sets probability of any given other contestant getting involved, victimWeight sets probability
        # of any given contestant being the victim
        
        # modifier values list the contestant stats that affect the probabilities of these and by how relatively much (though
        # usually just 1 or -1). If there is a good way to make the json thing give dict(string)->float instead that'd be
        # preferred
        
        # unique signals the event processor that only the characters listed in uniqueUsers may trigger this event
        
        # Randomize baseWeight a little
        self.name = name
        self.settings = settings #screw it, everyone gets a copy of what they need. Python stores by reference anyway.
        #This is kind of a dumb way to do it, but being more general is a pain
        for multiplierType = ['main','participant','victim']:
            if multiplierType+'Weight' in self.baseProps:
                self.eventRandomize(multiplierType+'Weight')
        
    def doEvent(self,*args,**kwargs): # args allows passing of arbitrary number of contestants (or other arguments), kwargs allows passing of specific args
        # like settings. The default doEvent expects one contestant
        desc = args[0].name+' did absolutely nothing.'
        return desc
    
    def eventRandomize(propName):
        self.baseProps[propName] = (self.baseProps[propName]
            *(1+random.uniform(-1*self.settings['eventRandomness'],self.settings['eventRandomness'])))