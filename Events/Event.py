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
        # int numParticipants, int numVictims, dict (string: float) mainModifiers,
        # dict (string: float) optional participantModifiers, dict (string: float) optional victimModifiers,
        # bool unique, list[string] optional uniqueUsers #at the moment only supports unique contestants performing the event, rather than being the victim etc. This is bad for, say, Mami getting her head eaten.
        # bool itemRequired, string optional necessaryItem
        # (The event is more (or less) likely if actor has ANY relationship that meets the criterion >mainFriendLevel. Set bool to false if you want < instead.
        # float mainFriendEffect (set 0 for none), (relation: bool, value: int) mainNeededFriendLevel  
        # float mainLoveEffect (set 0 for none), (relation: bool, value:int) mainNeededLoveLevel
        # float friendEffect (set 0 for none) [FROM ACTOR to PARTICIPANT (except for >2 people, in which case all are checked)]
        # float loveEffect (set 0 for none)
        # float friendEffectVictim
        # float loveEffectVictim
        # If first bool is true, then you need friendship level > (or if bool false, <) the specified needed level
        # bool friendRequired, (relation: bool, value:int) optional neededFriendLevel 
        # bool loveRequired, (relation: bool, value:int) optional, neededLoveLevel
        # bool friendRequiredVictim, (relation: bool, value:int) optional neededFriendLevelVictim
        # bool loveRequiredVictim, (relation: bool, value:int) optional, neededLoveLevelVictim

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
        for multiplierType in ['main', 'participant', 'victim']:
            if multiplierType+'Weight' in self.baseProps:
                self.eventRandomize(multiplierType+'Weight')

    def doEvent(self, mainActor, state=None, participants=None, victims=None): # State, participants and victims here for this particular function are clearly unused and could be _ , but this provides max clarity for copying into other events
        desc = mainActor.name+' did absolutely nothing.'
        return desc

    def eventRandomize(self, propName):
        self.baseProps[propName] = (self.baseProps[propName]
                                    *(1+random.uniform(-1*self.settings['eventRandomness'], self.settings['eventRandomness'])))
