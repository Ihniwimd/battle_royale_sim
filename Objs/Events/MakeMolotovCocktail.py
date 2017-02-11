
from Objs.Events.Event import Event
import random

def func(self, mainActor, state=None, participants=None, victims=None, sponsors=None):
    probSuccess = mainActor.stats["cleverness"]*0.03+0.3
    probNormalFailure = (1-probSuccess)*0.8
    probHorrifcFailure = 1-probNormalFailure-probSuccess
    randValue = random.random()
    if randValue < probSuccess:
        mainActor.addItem(state["items"]["MolotovCocktail"])
        desc = mainActor.name + ' crafted a Molotov Cocktail.'
        return (desc, [mainActor, state["items"]["MolotovCocktail"]], [])
    elif randValue < probSuccess+probNormalFailure:
        desc = mainActor.name + ' tried to make a Molotov Cocktail, but burned '+Event.parseGenderReflexive(mainActor)+' instead.'
        mainActor.permStatChange({'stability': -1,
                              'endurance': -1,
                              'combat ability': -1})
        return (desc, [mainActor], [])
    else:
        desc = mainActor.name + ' tried to make a Molotov Cocktail, but lit '+Event.parseGenderReflexive(mainActor)+' on fire, dying horribly.'
        mainActor.alive = False
        return (desc, [mainActor], [mainActor.name])
        
Event.registerEvent("MakeMolotovCocktail", func)