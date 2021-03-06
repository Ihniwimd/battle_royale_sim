from Objs.Events.Event import Event
from Objs.Events.IndividualEventHandler import IndividualEventHandler
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    state["allRelationships"].IncreaseFriendLevel(mainActor, sponsors[0], random.randint(2, 3))
    mainActor.permStatChange({'survivalism': 2,
                              'cleverness': 2})
    choice = random.randint(0,1)
    
    #This cannot happen more than once
    eventHandler = IndividualEventHandler(state)
    eventHandler.banEventForSingleContestant("SponsorGivesTips", mainActor.name, state)
    # This will remain in place for the rest of the game
    self.eventStore[mainActor.name] = eventHandler
    if choice:
        desc = sponsors[0].name+' gave a map and a book of instructions to '+mainActor.name+"."
        return (desc, [sponsors[0], mainActor], [])
    else:
        desc = 'An unknown sponsor gave a map and a book of instructions to '+mainActor.name+"."
        return (desc, [mainActor], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.registerEvent("SponsorGivesTips", func)