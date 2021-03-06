"""A dumb very specific html writer, because I don't want to figure out the various library options."""

import re

class HTMLWriter(object):

    header = """<!DOCTYPE html>
<html>
<head>
<style>
eventnormal {
    color: black;
}
p {
    text-align: center;
}
contestant {
    color: DarkBlue;
}
item {
    color: Red;
}
sponsor {
    color: DarkGoldenRod;
}
banner {
    text-align: center;
    font-size: 200%;
}
img {
    width: 128px
}
</style>
</head>
<body>"""

    footer = """</body>
</html>"""

    def __init__(self):
        self.bodylist = [self.header]
    
    def reset(self):
        self.bodylist = [self.header]
    
    def wrap(self, text, wrapname):
        return "<"+wrapname+">\n"+text+"\n</"+wrapname+">\n"
    
    def addTitle(self, title):
        self.bodylist.insert(1,self.wrap(self.wrap(title, "banner"),"p"))
    
    def massInsertTag(self, desc, findString, insertString):
        stringList = desc.split(findString)
        if len(stringList) == 1:
            return desc
        for i in range(len(stringList)):
            if i>0:
                if not stringList[i].lower().startswith('.jpg') and not stringList[i].lower().startswith('.png') and not stringList[i].lower().startswith('.gif'):
                    stringList[i] = "</" + insertString + ">" + stringList[i]
            if i<len(stringList)-1:
                # Massive kludge. I didn't realize this would be a problem, so a lot of the images are named the same as the characters. Then again, this whole object is a kludge :p.
                if not stringList[i+1].lower().startswith('.jpg') and not stringList[i+1].lower().startswith('.png') and not stringList[i+1].lower().startswith('.gif'):
                    stringList[i] = stringList[i] + "<" + insertString + ">"
        return findString.join(stringList)
        
    def colorize(self, desc, state):
        # This would be more efficient if handled at the event level, but then it'd have to be worried about, etc. and require rewriting. Better to just waste a little computation dealing with it here.
        for x in state["contestants"]:
            desc = self.massInsertTag(desc, x, "contestant")
        for x in state["sponsors"]:
            desc = self.massInsertTag(desc, x, "sponsor")
        for x in state["items"].values():
            desc = self.massInsertTag(desc, x.friendly, "item")
        return desc
        
    def addEvent(self, desc, descContestants, state=None, preEventInjuries=None):
        tempStringList = []
        for contestant in descContestants:
            if state is not None:
                tempList = desc.split(str(contestant))
                insertionString = str(contestant)
                if hasattr(contestant, "injured") and (str(contestant) not in preEventInjuries or preEventInjuries[str(contestant)]) and contestant.injured:
                    insertionString += ' (Injured)'
                if hasattr(contestant, "hypothermic") and contestant.hypothermic is not None:
                    insertionString += ' (Hypothermic)'
                desc = insertionString.join(tempList)
            tempStringList.append("<img src='"+contestant.imageFile+"'>")
        tempStringList.append("<br>")
        tempStringList.append(self.wrap(desc, "eventnormal"))
        self.bodylist.append(self.wrap('\n'.join(tempStringList),"p"))
        
    def finalWrite(self, filepath, state):
        self.bodylist.append(self.footer)
        with open(filepath, 'w') as target:
            for line in self.bodylist:
                target.write(self.colorize(line, state))
                
    def addBigLine(self, line):
        self.bodylist.append(self.wrap(line, "p"))