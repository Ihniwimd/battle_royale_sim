"""Provides an object that handles the registration and deregistration of the callbacks for a given non-standard event,
providing convenient methods for common tasks.

Usage: Instantiate the object when needed, perform the necessary operations, and store in state["callbackStore"] (probably
under a key such as mainActor.name which will properly identify it). When the callbacks are no longer leader, delete from the
state. If a group of callbacks may be deleted under different circumstances, it is probably best to make two objects."""

from functools import partial
import warnings

class IndividualEventHandler(object):

    def __init__(self, state):
        self.state = state
        self.callbackReferences = [] # List of tuples, (callback list name where callback is stored, callback)
        
    def __del__(self):
        for toRemove in self.callbackReferences:
            try:
                self.state["callbacks"][toRemove[0]].remove(toRemove[1])
            except ValueError:
                pass
                #warnings.warn('IndividualEventHandler: Attempted to remove invalid callback '+str(toRemove[1])+'('+toRemove[1].eventName+') from '+toRemove[0])
        self.callbackReferences = []
    
    def registerEvent(self, locationListName, func, front=True):
        if front:
            self.state["callbacks"][locationListName].insert(0, func)
        else:
            self.state["callbacks"][locationListName].append(func)
        self.callbackReferences.append((locationListName, func))
    
    def setEventWeightForSingleContestant(self, eventName, contestantName, weight, state):
        def func(actor, origWeight, event):
            # if we're trying to set a weight to positive but it's the wrong phase
            if weight and "phase" in event.baseProps and state["curPhase"] not in event.baseProps["phase"]:
                return (origWeight, True)
            if event.name == eventName and actor.name == contestantName:
                return (weight, bool(weight))  # if weight is 0, we almost always want this to return False and block the event entirely
            else:
                return (origWeight, True)
        anonfunc = lambda actor, origWeight, event: func(actor, origWeight, event) # this anonymizes func, giving a new reference each time this is called
        anonfunc.eventName = eventName # Notes on the functor for debug purposes
        anonfunc.contestantName = contestantName
        self.registerEvent("modifyIndivActorWeights", anonfunc) # This needs to be at beginning for proper processing
        return anonfunc # Just in case it's needed by the calling function
        
    def bindRoleForContestantAndEvent(self, roleName, fixedRoleList, relevantActor, eventName):
        anonfunc = partial(self.fixedRoleCallback, roleName, fixedRoleList, relevantActor, eventName)
        anonfunc.eventName = eventName # Notes on the functor for debug purposes
        anonfunc.relevantActor = relevantActor
        anonfunc.fixedRoleList = fixedRoleList
        self.registerEvent("overrideContestantEvent", anonfunc)
        # It must _also_ be checked that the people bound all still live. This has be done before the event is selected, to prevent the selection
        # of invalid events.
        def func(actor, origWeight, event): # Black magic
            if event.name == eventName and actor.name == relevantActor.name:
                for person in fixedRoleList:
                    if not person.alive:
                        return (0, False)
            return (origWeight, True)
        anonfunc2 = lambda actor, origWeight, event: func(actor, origWeight, event) # this anonymizes func, giving a new reference each time this is called
        self.registerEvent("modifyIndivActorWeights", anonfunc2, False) # This needs to be at beginning for proper processing
        return anonfunc, anonfunc2 # Just in case it's needed by the calling function
    
    @staticmethod
    def fixedRoleCallback(roleName, fixedRoleList, relevantActor, eventName, contestantKey, thisevent, state, participants, victims, sponsorsHere):
        #Avoiding eval here
        roleDict = {"participants": participants,
        "victims": victims,
        "sponsors": sponsorsHere}   
        if thisevent.name==eventName and relevantActor.name == contestantKey:
            del roleDict[roleName][:] # Have to clear the list BUT keep the reference
            roleDict[roleName].extend(fixedRoleList)
        return True, False
        
    def banEventForSingleContestant(self, eventName, contestantName, state):
        self.setEventWeightForSingleContestant(eventName, contestantName, 0, state)
        
    def banMurderEventsAtoB(self, cannotKill, cannotBeVictim):
        def func(contestantKey, thisevent, state, participants, victims, sponsorsHere):
            if  "murder" in thisevent.baseProps and thisevent.baseProps["murder"] and contestantKey == str(cannotKill):
                if cannotBeVictim in victims or (not victims) and cannotBeVictim in participants:
                    return False, True
            return True, False
        anonfunc = lambda contestantKey, thisevent, state, participants, victims, sponsorsHere: func(contestantKey, thisevent, state, participants, victims, sponsorsHere) # this anonymizes func, giving a new reference each time this is called
        anonfunc.cannotKill = cannotKill # Notes on the functor for debug purposes
        anonfunc.cannotBeVictim = cannotBeVictim
        self.registerEvent("overrideContestantEvent", anonfunc) # This needs to be at beginning for proper processing
        return anonfunc # Just in case it's needed by the calling function
