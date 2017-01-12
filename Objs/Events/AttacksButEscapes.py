
from Objs.Events.Event import Event
import random

def func(Event, mainActor, state=None, participants=None, victims=None, sponsors=None):
    # Hmm...having an object that takes care of this max 5 business would be nice    
    # Deteriorate relationship of victim toward participant
    state["allRelationships"].IncreaseFriendLevel(victims[0], mainActor, -2)
    state["allRelationships"].IncreaseLoveLevel(victims[0], mainActor, -3)
    desc = mainActor.name+' attacked '+victims[0].name+', but '+Event.parseGenderSubject(victims[0])+' escaped.'
    return (desc, [mainActor, victims[0]], []) # Second entry is the contestants or items named in desc, in desired display. Third is anyone who died. This is in strings.

Event.doEventAttacksButEscapes = classmethod(func)

Event.registerEvent("AttacksButEscapes", Event.doEventAttacksButEscapes)
