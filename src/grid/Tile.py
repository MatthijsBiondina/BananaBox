class Tile:
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.contents = []

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getFirstElement(self):
        try:
            return self.contents[0]
        except:
            return None

    def getContents(self):
        return self.contents

    def isEmpty(self):
        return len(self.contents) == 0

    def contains(self, entity):
        return entity in self.contents
    
    def addEntity(self, entity):
        self.contents.insert(0,entity)

    def remEntity(self, entity):
        self.contents.remove(entity)

    def toString(self):
        return("Tile @ %s,%s -> %s" % (str(self.x),str(self.y),str(self.contents)))
