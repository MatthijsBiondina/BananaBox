import pygame

"""Entity class for a consumable object"""
class Consumable():
    blocking = False
    updateable = False
    
    def __init__(self,name,x,y,sprite_name,color_heat,model):
        self.name = name
        self.x = x
        self.y = y
        self.sprite = pygame.image.load("../res/sprites/%s/N.png" % (sprite_name))
        self.model = model
        self.c_heat = color_heat


    #Since food does not run away (yet), update function is implemented as dummy method 
    def update(self):
        return (0,0,0,0)

    """GETTER METHODS"""
    
    def getPblock(self):
        return self.pb

    def getLocation(self):
        return (self.x,self.y,0)

    def getName(self):
        return self.name

    def getSprite(self):
        return self.sprite

    #color is a single float representing a pint on a matplotlib color map
    def getCHeat(self):
        return self.c_heat

    def getBlocking(self):
        return self.blocking

    def canUpdate(self):
        return self.updateable
    
    def toString(self):
        return "%s @ (%s,%s)" % (self.name, str(self.x), str(self.y))
