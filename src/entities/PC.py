import pygame
import math
import numpy as np
from network.Vision import *

class PC():
    blocking = True
    updateable = True
    
    def __init__(self,name,x,y,o,hp,max_hp,sprite_name,model):
        self.name = name
        self.x = x
        self.y = y
        self.o = o
        self.hp = hp
        self.max_hp = max_hp
        self.sprites = self.loadSprites(sprite_name)
        self.model = model
        
        self.maxmom = 6
        (self.x_grid,self.y_grid) = model.getGridPosition(x,y)
        self.x_mom  = 0
        self.y_mom  = 0
        self.d_mom  = 0.33
        self.speed  = 2

        self.V = Vision( self.model.getGrid(), 11)
        

    def loadSprites(self,sprite_name):
        path = "../res/sprites/%s/" % (sprite_name)
        sprites = {8:pygame.image.load(path+'N.png' ),
                   9:pygame.image.load(path+'NE.png'),
                   6:pygame.image.load(path+'E.png' ),
                   3:pygame.image.load(path+'SE.png'),
                   2:pygame.image.load(path+'S.png' ),
                   1:pygame.image.load(path+'SW.png'),
                   4:pygame.image.load(path+'W.png' ),
                   7:pygame.image.load(path+'NW.png')}
        return sprites
        
    def damage(self,amount):
        self.hp = max(0,self.hp-amount)

    def heal(self,amount):
        self.hp = min(self.max_hp, self.hp+amount)

    def update(self):
        keys = {'w':self.model.getKey(119),
                'a':self.model.getKey( 97),
                's':self.model.getKey(115),
                'd':self.model.getKey(100)}

        (self.x_mom, self.y_mom)    = self.updateMoment(self.x_mom, self.y_mom, keys)
        (self.x,self.y,x_spd,y_spd) = self.updateCoords(self.x,self.y,self.x_mom,self.y_mom)
        self.o                      = self.determineOrientation(x_spd,y_spd,keys)

        old_x_grid = self.x_grid
        old_y_grid = self.y_grid
        (self.x_grid,self.y_grid) = self.model.getGridPosition(self.x,self.y)
        return (old_x_grid,old_y_grid,self.x_grid,self.y_grid)

    """MOVEMENT METHODS"""
    
    def determineOrientation(self,dx,dy,keys):
        o = self.o
        if (keys['w'] or keys['a'] or keys['s'] or keys['d']) and not (dx == 0 and dy == 0):
            if dx > 2*abs(dy):        o = 6
            elif -dx > 2*abs(dy):     o = 4
            elif dy > 2*abs(dx):      o = 2
            elif -dy > 2*abs(dx):     o = 8
            elif dx >= 0 and dy >= 0: o = 3
            elif dx <= 0 and dy >= 0: o = 1
            elif dx <= 0 and dy <= 0: o = 7
            elif dx >= 0 and dy <= 0: o = 9
        return o

    def updateMoment(self,x_mom,y_mom, keys):
        if   x_mom > 0: x_mom = max(0,min( self.maxmom, x_mom + (self.d_mom if keys['d'] and not keys['a'] else -self.d_mom)))
        elif x_mom < 0: x_mom = min(0,max(-self.maxmom, x_mom - (self.d_mom if keys['a'] and not keys['d'] else -self.d_mom)))
        else:           x_mom = x_mom + (self.d_mom if keys['d'] else 0) - (self.d_mom if keys['a'] else 0)

        if   y_mom > 0: y_mom = max(0,min( self.maxmom, y_mom + (self.d_mom if keys['s'] and not keys['w'] else -self.d_mom)))
        elif y_mom < 0: y_mom = min(0,max(-self.maxmom, y_mom - (self.d_mom if keys['w'] and not keys['s'] else -self.d_mom)))
        else:           y_mom = y_mom + (self.d_mom if keys['s'] else 0) - (self.d_mom if keys['w'] else 0)

        #determine hypothesized next x and y coords to prevent walking in walls
        x_hyp = self.x + self.mom2spd( x_mom )
        y_hyp = self.y + self.mom2spd( y_mom )

        #you can't walk through walls:
        x_mom = max(0,x_mom) if self.model.isBlocked(x_hyp-16,self.y-16,self.name) or self.model.isBlocked(x_hyp-16,self.y+16,self.name) else x_mom
        x_mom = min(0,x_mom) if self.model.isBlocked(x_hyp+16,self.y-16,self.name) or self.model.isBlocked(x_hyp+16,self.y+16,self.name) else x_mom
        y_mom = max(0,y_mom) if self.model.isBlocked(self.x-16,y_hyp-16,self.name) or self.model.isBlocked(self.x+16,y_hyp-16,self.name) else y_mom
        y_mom = min(0,y_mom) if self.model.isBlocked(self.x-16,y_hyp+16,self.name) or self.model.isBlocked(self.x+16,y_hyp+16,self.name) else y_mom

        return (x_mom,y_mom)

    def updateCoords(self,x,y,x_mom,y_mom):
        x_spd = self.mom2spd( x_mom )
        y_spd = self.mom2spd( y_mom )
        #update absolute position
        x = x + x_spd
        y = y + y_spd
        return (x,y,x_spd,y_spd)

    def mom2spd( self,mom ):
        return (1 / (1 + math.exp(-mom)) - 0.5) * 2 * self.speed

    """GETTER METHODS"""

    def getVision(self):
        inputs = []
        for i in range(11):
            (dheat,cheat) = self.V.getVision(self.x_grid,self.y_grid,self.o, 11-i )
            inputs.append(dheat)
            inputs.append(cheat)
        return inputs

    def getLocation(self):
        return (self.x,self.y,self.o)

    def getName(self):
        return self.name

    def getSprite(self):
        return self.sprites[self.o]

    def getBlocking(self):
        return self.blocking

    def getCHeat(self):
        return 1

    def canUpdate(self):
        return self.updateable

    def toString(self):
        return "%s @ (%s,%s) facing %s" % (self.name, str(self.x), str(self.y), str(self.o))

