from Objs.Events.Event import Event
from ..Utilities.ArenaUtils import weightedDictRandom
import random

# For perfornace reasons, this could be a self-removing callback that sets a flag and destroys itself. However, in case we ever allow resurrection, I will do it this way.
TURNS_UNTIL_FORCE_FIGHT = 3

def allowForceFight(liveContestants, baseEventActorWeights, baseEventParticipantWeights, baseEventVictimWeights, baseEventSponsorWeights, turnNumber, state):
    if turnNumber[0]<TURNS_UNTIL_FORCE_FIGHT:
        return
    for x in range(1, TURNS_UNTIL_FORCE_FIGHT+1):
        comparison =  len(state["callbackStore"]["contestantLog"][turnNumber[0]-x+1]) if x>1 else len(liveContestants)  # Because of potential callback order issues
        if len(state["callbackStore"]["contestantLog"][turnNumber[0]-x])>3 or comparison!=len(state["callbackStore"]["contestantLog"][turnNumber[0]-x]):
            return
    baseEventActorWeights["SponsorForceFight"] = 5 + state["events"]["SponsorForceFight"].eventStore.setdefault("forceLevel", 0)
    state["events"]["SponsorForceFight"].eventStore["forceLevel"] += 2

Event.registerInsertedCallback("modifyBaseWeights", allowForceFight)

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    desc = "Tired of waiting, the sponsors force two of the remaining contestants to fight. "
    
    # Build dict of weights for various possibilities
    optionDict = {'fight': 1}
    if state['allRelationships'].friendships[str(mainActor)][str(participants[0])]>3 and state['allRelationships'].friendships[str(participants[0])][str(mainActor)]>3:
        optionDict['attemptEscape'] = 2
    if state['allRelationships'].loveships[str(mainActor)][str(participants[0])]>3:
        optionDict['actorSuicide'] = 1
        optionDict['actorBegToKill'] = 1
    if state['allRelationships'].loveships[str(participants[0])][str(mainActor)]>3:
        optionDict['participantSuicide'] = 1
        optionDict['participantBegToKill'] = 1
    chosen = weightedDictRandom(optionDict, 1)[0]
    
    if chosen == 'fight':
        fightDesc, fightList, fightDead = Event.fight([mainActor, participants[0]], state['allRelationships'], state['settings'])
        desc += "They did so, and " + fightDesc
        return (desc, [mainActor, participants[0]]+fightList, [str(x) for x in fightDead])
    if chosen == 'attemptEscape':
        dead = mainActor if random.randint(0,1) else participants[0]
        desc += 'Instead of fighting, the two contestants attempt to escape, but '+dead.name+' is caught and killed by the sponsors!'
        dead.alive = False
        return(desc, [mainActor, participants[0]], [dead.name])
    if chosen == 'actorSuicide':
        desc += "Rather than be forced to fight "+Event.parseGenderPossessive(mainActor)+" loved one, "+str(mainActor)+" committed suicide!"
        mainActor.alive = False
        return(desc, [mainActor, participants[0]], [mainActor.name])   
    if chosen == 'participantSuicide':
        desc += "Rather than be forced to fight "+Event.parseGenderPossessive(participants[0])+" loved one, "+str(participants[0])+" committed suicide!"
        participants[0].alive = False
        return(desc, [mainActor, participants[0]], [participants[0].name]) 
    if chosen == 'actorBegToKill':
        desc += str(mainActor)+" begged "+str(participants[0])+" to kill "+Event.parseGenderObject(mainActor)
        if state['allRelationships'].loveships[str(participants[0])][str(mainActor)]<4 or random.random()>0.5:
            desc += ', forcing '+str(participants[0])+' to go through with it.'
            mainActor.alive = False
            deadList = [mainActor.name]
        else:
            desc += ', but '+Event.parseGenderSubject(participants[0])+' refused, killing '+Event.parseGenderReflexive(participants[0])+ ' instead!'
            participants[0].alive = False
            deadList = [participants[0].name]
        return(desc, [mainActor, participants[0]], deadList)
    if chosen == 'participantBegToKill':
        desc += str(participants[0])+" begged "+str(mainActor)+" to kill "+Event.parseGenderObject(participants[0])
        if state['allRelationships'].loveships[str(mainActor)][str(participants[0])]<4 or random.random()>0.5:
            desc += ', forcing '+str(mainActor)+' to go through with it.'
            deadList = [participants[0].name]
            participants[0].alive = False
        else:
            desc += ', but '+Event.parseGenderSubject(mainActor)+' refused, killing '+Event.parseGenderReflexive(mainActor)+ ' instead!'
            mainActor.alive = False
            deadList = [mainActor.name]
        return(desc, [mainActor, participants[0]], deadList)  
    raise AssertionError("This should not happen! "+chosen)
    
        
Event.registerEvent("SponsorForceFight", func)